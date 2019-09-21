import re 
import base64, urllib
import os
from openerp.addons.decimal_precision import decimal_precision as dp
import cStringIO
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, Alignment, easyxf
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import pymssql
import psycopg2
from openerp.osv import osv,fields
from openerp.tools.translate import _
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import time
import math
import csv
import random
import calendar
from dateutil import rrule




class attendance_synchronization(osv.osv):
    _name = "attendance.synchronization"
       
    def run_attendance(self,cr,uid,ids,context=None):
        res = {}
        bar_obj = self.pool.get('employee.barcode')
        emp_obj = self.pool.get('hr.employee')
        raw_obj = self.pool.get('raw.attendance')
        exclude = barcode_ids = []
        for val in self.browse(cr, uid, ids):
            date1 = val.date
            query = "select name,punch from employee_barcode where punch_date = '"+str(date1)+"' order by name,punch"  
            cr.execute(query)
            result = cr.fetchall()
            for line in result:  
                try:              
                    code = line[0].strip()
                    code = code.upper()
                    date1 = line[1]
                    date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
                    date1 = date1.strftime("%Y-%m-%d %H:%M:%S")
                    today = datetime.today().strftime('%Y-%m-%d')
                    emp_id = emp_obj.search(cr, uid, [('sinid','=',code),('active','=',True)])
                    
                    if emp_id:
                        barcode_ids.append(emp_id[0])
                        cr.execute("delete from raw_attendance where name='"+str(date1)+"' and employee_id = '"+str(emp_id[0])+"'")
                        create_id = raw_obj.create(cr, uid, {'name':date1,'employee_id':emp_id[0]})
                        print "==============RAW ATTENDANCE CREATED===============",create_id
                except:
                    pass
    
        return True
    
   
    
    _columns = {
                'name':fields.char('Server Name',size=64,required=True),
                'port':fields.char('Port',size=64,required=True),
                'user':fields.char('User',size=64,required=True),
                'password':fields.char('Password',size=64,required=True),
                'database':fields.char('Database',size=64,required=True,),
                
                'date':fields.date('Create Date',required=True),
                'state':fields.selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')],'State',readonly=True),
                }

    _defaults = {
                 'state':'draft',
                 }
    
    def confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'confirm'})
        return True

    def cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'})
        return True
    
    def reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    


class raw_attendance(osv.osv):
    _name = 'raw.attendance'
    _order = 'name desc,employee_id' 
    
    def _calculate_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d %H:%M:%S').timetuple()
            month = tm_tuple.tm_mon
            res[each.id] = month     
        return res
    
    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d %H:%M:%S').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                res[each.id] = year_id[0]  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res   
    
    _columns = {
                
        'name': fields.datetime('Date', required=True, select=1),
        'employee_id': fields.many2one('hr.employee', "Employee's Name", required=True, select=True),
        'department_id':fields.related('employee_id','department_id',type="many2one",relation='hr.department',string='Department'),
        'company_id':fields.related('employee_id','resource_id','company_id',relation='res.company',string='Company Name',type='many2one',store=False),
        'month':fields.function(_calculate_month,method=True,type='integer',string='Month',store=True),
        'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
        'year':fields.selection([('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),
                                         ('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),
                                         ('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),
                                         ('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),
                                         ('2030','2030'),('2031','2031'),('2032','2032'),('2033','2033'),
                                         ('2034','2034'),('2035','2035'),],'YEAR'),
        'active':fields.boolean('Active'),
        'emp_category':fields.related('employee_id','category',selection=[('Skilled','Skilled'),('UnSkilled','UnSkilled'),('Semi_Skilled','Semi_Skilled')],type='selection',relation='hr.employee',string="Category"),
        'search_date':fields.date(string="Date"),        
        'real_name': fields.datetime('Real Date'),
        'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),
        'job_id':fields.related('employee_id','job_id',type="many2one",relation='hr.job',string='Designation'),
        'm_id':fields.char('Machine Id', size=128),
        }
    
    _sql_constraints = [('unique_raw_attendance','unique(employee_id,name)','Duplicate entries are not allowed')]
    
    _defaults = {
                 'year':time.strftime('%Y'),
                 'active':True
                 }
    
class synchronization(osv.osv):
    _name = "synchronization"
    
    def server_connect(self, line):
        server=line.name
        port=line.port
        user=line.user
        password=line.password
        database=line.database        
        try:
            connection = pymssql.connect(host=server+':'+port, user=user, password=password, database=database)
            return connection
        except:
            raise osv.except_osv(_('Warning !'),_("Unable to connect to server, please check the parameters and network connections."))        
    
    def server_connect_141(self, line):
        server=line.name
        port=line.port
        user=line.user
        password=line.password
        database=line.database
        print"server_connect_new============================="
        try:
#             conn_string = "host='192.168.0.141' dbname='DESIGNCO_PREPRODUCTION_V1' user='erp' password='123456'"
#             connection = psycopg2.connect(conn_string)
            connection = psycopg2.connect(host=server, port=port, user=user, password=password, dbname=database)
#             cursor = connection.cursor()
            return connection
        except:
            raise osv.except_osv(_('Warning !'),_("Unable to connect to server, please check the parameters and network connections."))
    
    def run_attendance(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        raw_obj = self.pool.get('raw.attendance')
        year = time.strftime('%Y')
        month=''
        year_id=''
        for val in self.browse(cr, uid, ids):
            PAYCODE = []
            count = 0
            conn = self.server_connect(val)
            cursor = conn.cursor() 
            start_date = datetime.strptime(val.date,'%Y-%m-%d')
            end_date = datetime.strptime(val.end_date,'%Y-%m-%d')
            end_tm_tuple = datetime.strptime(val.end_date,'%Y-%m-%d').timetuple()
            if val.employee_id:
                emp_data = emp_obj.read(cr, uid, [val.employee_id.id], ['sinid'])
            else:
                emp_data = emp_obj.read(cr, uid, emp_obj.search(cr, uid, [('active','=',True)]), ['sinid'])
            for data in emp_data:
                PAYCODE.append(str(data['sinid']).upper())
            if PAYCODE and len(PAYCODE) == 1:
                PAYCODE.append(PAYCODE[0])
            PAYCODE = tuple(PAYCODE)
            
            while (start_date <= end_date):
                date2 = start_date.strftime('%Y-%m-%d')
                tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                    break
                if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                    break
                date1 = date2.replace('-','/')
                query = "select PAYCODE,convert(varchar,OFFICEPUNCH,120),CARDNO from MachineRawPunch where convert(varchar,OFFICEPUNCH,111) = '"+str(date1)+"' and PAYCODE in %s order by PAYCODE,convert(varchar,OFFICEPUNCH,120)" % (PAYCODE,)
                cursor.execute(query)
                result = cursor.fetchall()
                for line in result:
                    year = time.strftime('%Y')
                    try:           
                        code = line[0].strip()
                        code = code.upper()
                        date1 = line[1]
                        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
                        date1 = date1 - timedelta(hours=5,minutes=30)
                        date3 = date1.strftime("%Y-%m-%d")
                        date1 = date1.strftime("%Y-%m-%d %H:%M")
                        tm_tuple = datetime.strptime(str(date1),'%Y-%m-%d %H:%M').timetuple()
                        year = tm_tuple.tm_year
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                        if year_id:
                            year_id = year_id[0]
                        tm_tuple = datetime.strptime(str(date1),'%Y-%m-%d %H:%M').timetuple()
                        month = tm_tuple.tm_mon
                        cr.execute("select id from hr_employee where sinid = '"+str(code)+"'")
                        emp_id = cr.fetchone()[0]
                        cr.execute("delete from raw_attendance where name='"+str(date1)+"' and employee_id = '"+str(emp_id)+"'")
                        print "==============RAW ATTENDANCE CREATED===============",count,date3,"==================",date1,date3
                            #raw_obj.create(cr, uid, {'name':date1,'employee_id':emp_id})
                        obj = cr.execute('insert into raw_attendance (name,employee_id,month,year,year_id,active,search_date) values (%s,%s,%s,%s,%s,%s,%s)', (date1,emp_id,str(month),str(year),str(year_id),True,date3))
                        count += 1
                            #print "==============RAW ATTENDANCE CREATED===============",count,date2,"==================",time.strftime('%M:%S')
                    except:
                        pass
                start_date += timedelta(days=1)                 
            cursor.close()             
        return True

    def run_attendance_new(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        raw_obj = self.pool.get('raw.attendance')
        mc_obj = self.pool.get('raw_punch_attendance')
        year = time.strftime('%Y')
        month=''
        year_id=''
        for val in self.browse(cr, uid, ids):
            cardno = []
            count = 0
#             conn = self.server_connect(val)
#             cursor = conn.cursor() 
            start_date = datetime.strptime(val.date,'%Y-%m-%d')
            end_date = datetime.strptime(val.end_date,'%Y-%m-%d')
            end_tm_tuple = datetime.strptime(val.end_date,'%Y-%m-%d').timetuple()
            if val.employee_id:
                emp_data = emp_obj.read(cr, uid, [val.employee_id.id], ['ssnid'])
            else:
                emp_data = emp_obj.read(cr, uid, emp_obj.search(cr, uid, [('active','=',True)]), ['ssnid'])
            for data in emp_data:
#                 cardno.append(str(data['sinid']).upper())
                cardno.append(str(data['ssnid']).upper())
            if cardno and len(cardno) == 1:
                cardno.append(cardno[0])
            cardno = tuple(cardno)
            while (start_date <= end_date):
                date2 = start_date.strftime('%Y-%m-%d')
                tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                    break
                if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                    break
#                 date1 = date2.replace('-','/')
                query = "select cardno,punch_time from raw_punch_attendance where to_char(punch_time,'YYYY-MM-DD')= '"+str(date2)+"' and cardno in %s order by cardno,punch_time" % (cardno,)
                cr.execute(query)
#                 result = cursor.fetchall()s
                result = cr.fetchall()
                for line in result:
                    year = time.strftime('%Y')
                    try:           
                        code = line[0].strip()
                        code = code.upper()
                        date1 = line[1]
                        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
                        date1 = date1 - timedelta(hours=5,minutes=30)
                        date2 = date1.strftime("%Y-%m-%d")
                        date1 = date1.strftime("%Y-%m-%d %H:%M")
                        tm_tuple = datetime.strptime(str(date1),'%Y-%m-%d %H:%M').timetuple()
                        year = tm_tuple.tm_year
                        month = tm_tuple.tm_mon
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                        if year_id:
                            year_id = year_id[0]
                        cr.execute("select id from hr_employee where ssnid = '"+str(code)+"'")
                        emp_id = cr.fetchone()[0]
                        cr.execute("delete from raw_attendance where name='"+str(date1)+"' and employee_id = '"+str(emp_id)+"'")
                        print "==============RAW ATTENDANCE CREATED===============",count,date2,"==================",date1
                        #raw_obj.create(cr, uid, {'name':date1,'employee_id':emp_id})
                        obj = cr.execute('insert into raw_attendance (name,employee_id,month,year,year_id,active,search_date) values (%s,%s,%s,%s,%s,%s,%s)', (date1,emp_id,str(month),str(year),str(year_id),True,date2))
                        count += 1
#                         print "==============RAW ATTENDANCE CREATED===============",count,date2,"==================",time.strftime('%M:%S')
                    except:
                        pass
                start_date += timedelta(days=1)
#             cursor.close()
        return True
    
    def run_attendance_jbs(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        raw_obj = self.pool.get('raw.attendance')
        year = time.strftime('%Y')
        month=''
        year_id=''
        for val in self.browse(cr, uid, ids):
            CARDNO = []
            count = 0
            conn = self.server_connect(val)
            cursor = conn.cursor() 
            start_date = datetime.strptime(val.date,'%Y-%m-%d')
            end_date = datetime.strptime(val.end_date,'%Y-%m-%d')
            end_tm_tuple = datetime.strptime(val.end_date,'%Y-%m-%d').timetuple()
            if val.employee_id:
                emp_data = emp_obj.read(cr, uid, [val.employee_id.id], ['paycode'])
            else:
                emp_data = emp_obj.read(cr, uid, emp_obj.search(cr, uid, [('active','=',True)]), ['paycode'])
            for data in emp_data:
                CARDNO.append(str(data['paycode']).upper())
            if CARDNO and len(CARDNO) == 1:
                CARDNO.append(CARDNO[0])
            CARDNO = tuple(CARDNO)
            while (start_date <= end_date):
                date2 = start_date.strftime('%Y-%m-%d')
                tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                    break
                if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                    break
                date1 = date2.replace('-','/')
                query = "select CARDNO,convert(varchar,OFFICEPUNCH,120) from Rawdata where convert(varchar,OFFICEPUNCH,111) = '"+str(date1)+"' and CARDNO in %s order by CARDNO,convert(varchar,OFFICEPUNCH,120)" % (CARDNO,)
                cursor.execute(query)
                result = cursor.fetchall()
                for line in result:
                    year = time.strftime('%Y')
                    try:           
                        code = line[0].strip()
                        code = code.upper()
                        date1 = line[1]
                        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
                        date1_real = date1
                        date1_real = date1_real.strftime("%Y-%m-%d %H:%M")
                        date1 = date1 - timedelta(hours=5,minutes=30)
                        date3 = date1.strftime("%Y-%m-%d")
                        date1 = date1.strftime("%Y-%m-%d %H:%M")
                        tm_tuple = datetime.strptime(str(date1),'%Y-%m-%d %H:%M').timetuple()
                        year = tm_tuple.tm_year
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                        if year_id:
                            year_id = year_id[0]
                        tm_tuple = datetime.strptime(str(date1),'%Y-%m-%d %H:%M').timetuple()
                        month = tm_tuple.tm_mon
                        cr.execute("select id from hr_employee where paycode = '"+str(code)+"'")
                        emp_id = cr.fetchone()[0]
                        cr.execute("delete from raw_attendance where name='"+str(date1)+"' and employee_id = '"+str(emp_id)+"'")
                        print "==============RAW ATTENDANCE CREATED===============",count,date3,"==================",date1
                        #raw_obj.create(cr, uid, {'name':date1,'employee_id':emp_id})
                        obj = cr.execute('insert into raw_attendance (name,employee_id,month,year,year_id,active,search_date,real_name) values (%s,%s,%s,%s,%s,%s,%s,%s)', (date1,emp_id,str(month),str(year),str(year_id),True,date3,date1_real))
                        count += 1
#                         print "==============RAW ATTENDANCE CREATED===============",count,date2,"==================",time.strftime('%M:%S')
                    except:
                        pass
                start_date += timedelta(days=1)                 
            cursor.close()             
        return True
    
    
    def run_attendance_141(self, cr, uid, ids, context=None):
        print "run attendence 141========================="
        emp_obj = self.pool.get('hr.employee')
        raw_obj = self.pool.get('raw.attendance')
        year = time.strftime('%Y')
        month=''
        year_id=''
        for val in self.browse(cr, uid, ids):
            CARDNO = []
            PAYCODE = []
            PAYCODE1 = []
            
            count = 0
            conn = self.server_connect_141(val)
            cursor = conn.cursor() 
            start_date = datetime.strptime(val.date,'%Y-%m-%d')
            end_date = datetime.strptime(val.end_date,'%Y-%m-%d')
            end_tm_tuple = datetime.strptime(val.end_date,'%Y-%m-%d').timetuple()
            if val.employee_id:
                emp_data = emp_obj.read(cr, uid, [val.employee_id.id], ['sinid'])
            else:
                emp_data = emp_obj.read(cr, uid, emp_obj.search(cr, uid, [('active','=',True)]), ['sinid'])
            for data in emp_data:
                CARDNO.append(str(data['sinid']).upper())
            if CARDNO and len(CARDNO) == 1:
                CARDNO.append(CARDNO[0])
            CARDNO = tuple(CARDNO)
                 
            while (start_date <= end_date):
                date2 = start_date.strftime('%Y-%m-%d')
                tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                    break
                if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                    break
                date1 = date2.replace('-','/')
                query = "select hr.sinid,raw.name from raw_attendance as raw left join hr_employee as hr on hr.id = raw.employee_id where cast(raw.name as date) = '"+str(date1)+"' and hr.sinid in %s order by raw.name" % (CARDNO,)
                cursor.execute(query)
                result = cursor.fetchall()
                
                for line in result:
                    year = time.strftime('%Y')
                    try:
                        code = line[0].strip()
                        code = code.upper()
                        date1 = line[1]
                        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
                        date1_real = date1 + timedelta(hours=5,minutes=30)
                        date1_real = date1_real.strftime("%Y-%m-%d %H:%M")                        
                        date3 = date1.strftime("%Y-%m-%d")
                        tm_tuple = datetime.strptime(str(date1),"%Y-%m-%d %H:%M:%S").timetuple()
                        year = tm_tuple.tm_year
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                        if year_id:
                            year_id = year_id[0]
                        tm_tuple = datetime.strptime(str(date1),"%Y-%m-%d %H:%M:%S").timetuple()
                        month = tm_tuple.tm_mon
                        cr.execute("select id from hr_employee where sinid = '"+str(code)+"'")
                        emp_id = cr.fetchone()[0]
                        cr.execute("delete from raw_attendance where name='"+str(date1)+"' and employee_id = '"+str(emp_id)+"'")
                        print "==============RAW ATTENDANCE CREATED===============",count,date3,"==================",date1
                        #raw_obj.create(cr, uid, {'name':date1,'employee_id':emp_id})
#                         print "dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",date1,emp_id,str(month),str(year),str(year_id),True,date3,a
                        print ("date3-----------",date3)
                        obj = cr.execute('insert into raw_attendance (name,employee_id,month,year,year_id,active,search_date,real_name) values (%s,%s,%s,%s,%s,%s,%s,%s)', (date1,emp_id,str(month),str(year),str(year_id),True,date3,date1_real))
                        count += 1
#                         print "==============RAW ATTENDANCE CREATED===============",count,date2,"==================",time.strftime('%M:%S')
                    except:
                        pass
                start_date += timedelta(days=1)                 
            cursor.close()             
        return True
    
      
       
    
    def run_attendance_contractor(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        raw_obj = self.pool.get('raw.attendance')
        year = time.strftime('%Y')
        month=''
        year_id=''
        for val in self.browse(cr, uid, ids):
            PAYCODE = []
            PAYCODE1 = []
            count = 0
            conn = self.server_connect_141(val)
            cursor = conn.cursor() 
            start_date = datetime.strptime(val.date,'%Y-%m-%d')
            end_date = datetime.strptime(val.end_date,'%Y-%m-%d')
            end_tm_tuple = datetime.strptime(val.end_date,'%Y-%m-%d').timetuple()
            if val.employee_id:
                contr_data = emp_obj.read(cr, uid, [val.employee_id.id], ['paycode'])
            else:
                contr_data = emp_obj.read(cr, uid, emp_obj.search(cr, uid, [('active','=',True)]), ['paycode'])
            for data1 in contr_data:
                 if data1['paycode']:
                     PAYCODE1.append(str(data1['paycode'].upper()))
                     data1['paycode'] = data1['paycode'].replace('-','').replace('C01','C1').replace('C02','C2').replace('C03','C3').replace('C04','C4').replace('C05','C5').replace('C06','C6').replace('C07','C7').replace('C08','C8').replace('C09','C9')                
                     PAYCODE.append(str(data1['paycode'].upper()))
            
            if PAYCODE and len(PAYCODE) == 1:
                PAYCODE.append(PAYCODE[0])
            PAYCODE = tuple(PAYCODE)
            if PAYCODE1 and len(PAYCODE1) == 1:
                PAYCODE1.append(PAYCODE1[0])
            PAYCODE1 = tuple(PAYCODE1)
            while (start_date <= end_date):
                date2 = start_date.strftime('%Y-%m-%d')
                tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                    break
                if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                    break
                date1 = date2.replace('-','/')
                query = "select hr.sinid,raw.name from contr_raw_attendance as raw left join hr_contractorp as hr on hr.id = raw.contractor_id where cast(raw.name as date) = '"+str(date1)+"' and hr.sinid in %s order by raw.name" % (PAYCODE,)  
                cursor.execute(query)
                result = cursor.fetchall()
                query1 = "select hr.sinid,raw.name from contr_raw_attendance as raw left join hr_contractorp as hr on hr.id = raw.contractor_id where cast(raw.name as date) = '"+str(date1)+"' and hr.sinid in %s order by raw.name" % (PAYCODE1,)  
                cursor.execute(query1)
                result1 = cursor.fetchall()
          
                for line in result:
                    year = time.strftime('%Y')
                    try:
                        code = line[0].strip()
                        code = code.upper()
                        date1 = line[1]
                        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
                        date1_real = date1 + timedelta(hours=5,minutes=30)
                        date1_real = date1_real.strftime("%Y-%m-%d %H:%M")                        
                        date3 = date1.strftime("%Y-%m-%d")
                        tm_tuple = datetime.strptime(str(date1),"%Y-%m-%d %H:%M:%S").timetuple()
                        year = tm_tuple.tm_year
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                        if year_id:
                            year_id = year_id[0]
                        tm_tuple = datetime.strptime(str(date1),"%Y-%m-%d %H:%M:%S").timetuple()
                        month = tm_tuple.tm_mon
                        cr.execute("select id from hr_employee where sinid = '"+str(code)+"'")
                        emp_id = cr.fetchone()[0]
                        cr.execute("delete from raw_attendance where name='"+str(date1)+"' and employee_id = '"+str(emp_id)+"'")
                        print "==============RAW ATTENDANCE CREATED===============",count,date3,"==================",date1
                        #raw_obj.create(cr, uid, {'name':date1,'employee_id':emp_id})
#                         print "dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",date1,emp_id,str(month),str(year),str(year_id),True,date3,a
                        obj = cr.execute('insert into raw_attendance (name,employee_id,month,year,year_id,active,search_date,real_name) values (%s,%s,%s,%s,%s,%s,%s,%s)', (date1,emp_id,str(month),str(year),str(year_id),True,date3,date1_real))
                        count += 1
#                         print "==============RAW ATTENDANCE CREATED===============",count,date2,"==================",time.strftime('%M:%S')
                    except:
                        pass
                    
                for line1 in result1:
                    year = time.strftime('%Y')
                    try:
                        code = line1[0].strip()
                        code = code.upper()
                        date1 = line1[1]
                        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
                        date1_real = date1 + timedelta(hours=5,minutes=30)
                        date1_real = date1_real.strftime("%Y-%m-%d %H:%M")                        
                        date3 = date1.strftime("%Y-%m-%d")
                        tm_tuple = datetime.strptime(str(date1),"%Y-%m-%d %H:%M:%S").timetuple()
                        year = tm_tuple.tm_year
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                       
                        if year_id:
                            year_id = year_id[0]
                        tm_tuple = datetime.strptime(str(date1),"%Y-%m-%d %H:%M:%S").timetuple()
                        month = tm_tuple.tm_mon
                        cr.execute("select id from hr_employee where paycode = '"+str(code)+"'")
                        emp_id = cr.fetchone()
                        cr.execute("delete from raw_attendance where name='"+str(date1)+"' and employee_id = '"+str(emp_id[0])+"'")
                        print "==============RAW ATTENDANCE CREATED===============",count,date3,"==================",date1
                        #raw_obj.create(cr, uid, {'name':date1,'employee_id':emp_id})
#                         print "dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",date1,emp_id,str(month),str(year),str(year_id),True,date3,a
                        obj = cr.execute('insert into raw_attendance (name,employee_id,month,year,year_id,active,search_date,real_name) values (%s,%s,%s,%s,%s,%s,%s,%s)', (date1,emp_id,str(month),str(year),str(year_id),True,date3,date1_real))
                        count += 1
#                         print "==============RAW ATTENDANCE CREATED===============",count,date2,"==================",time.strftime('%M:%S')
                    except:
                        pass
                    
                start_date += timedelta(days=1)                 
            cursor.close()             
        return True

    def run_attendance_matrix(self, cr, uid, ids, context=None):
        res = {}
        emp_obj = self.pool.get('hr.employee')
        exclude = barcode_ids = []
        year = time.strftime('%Y')
        month=''
        year_id=''
        for val in self.browse(cr, uid, ids):       
            CARDNO = []
            CARDNO1 = []
            CARDNO2 = []
            count = 0
            conn = self.server_connect(val)
            cursor = conn.cursor()
            print ("cursor-------------",cursor) 
            start_date =datetime.strptime(val.date,'%Y-%m-%d')
            end_date = datetime.strptime(val.end_date,'%Y-%m-%d')
            end_tm_tuple = datetime.strptime(val.end_date,'%Y-%m-%d').timetuple()    
            if val.employee_id:
                emp_data = emp_obj.read(cr, uid, [val.employee_id.id], ['sinid'])
            else:
                emp_data = emp_obj.read(cr, uid, emp_obj.search(cr, uid, [('active','=',True),('type','=','Contractor')]), ['sinid'])
            for data in emp_data:
                data['sinid'] = data['sinid'].replace('-','').replace('C01','C1')
                CARDNO.append(str(data['sinid']).upper())
            if CARDNO and len(CARDNO) == 1:
                CARDNO.append(CARDNO[0])
            CARDNO = tuple(CARDNO)
           
            print ("len of card no ---------",len(CARDNO))
            while (start_date <= end_date):
                date2 = start_date.strftime('%Y-%m-%d')
                tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                    break
                if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                    break
                date1 = date2.replace('-','/') 
                if  CARDNO :              
                    query = "select MA.UserID,convert(varchar,MA.Edatetime,120),DR.DoorName from Mx_ACSEventTrn as MA left join Mx_VEW_DoorDetail as DR on MA.MID=DR.MID where convert(varchar,MA.Edatetime,111) = '"+str(date1)+"' and (REPLACE(REPLACE(MA.UserID, '-', ''),'C01','C1') in "+str(CARDNO)+") and DR.DoorName  in ('UNIT4TURNSTILE1','UNIT4TURNSTILE2','UNIT4TURNSTILE3','UNIT4TURNSTILE4','UNIT4TURNSTILE5','UNIT4TURNSTILE6','UNIT4TURNSTILE7','UNIT4TURNSTILE8','UNIT4TURNSTILE9','UNIT4TURNSTILE10','UNIT4TURNSTILE11','UNIT4TURNSTILE12','UNIT4TURNSTILE13','UNIT4TURNSTILE14') order by MA.UserID,convert(varchar,MA.Edatetime,120)" 
                cursor.execute(query)
                result = cursor.fetchall() 
                print ("result----",len(result))               
                for line in result:
                    year = time.strftime('%Y')
                    try:           
                        code = line[0].strip()
                        code = code.replace('-','')
                        code = code.upper()
                        date1 = line[1]
                        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
                        date3 = date1.strftime("%Y-%m-%d")
                        date1_real = date1 + timedelta(hours=5,minutes=30)
                        date1_real = date1_real.strftime("%Y-%m-%d %H:%M")
                        date1 = date1 - timedelta(hours=5,minutes=30)
                        date1 = date1.strftime("%Y-%m-%d %H:%M")                                                
                        
                        
                        tm_tuple = datetime.strptime(str(date1),'%Y-%m-%d %H:%M').timetuple()
                        year = tm_tuple.tm_year
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                        m_id = line[2]
                        print ("m_id----------",m_id)
                        if year_id:
                            year_id = year_id[0]
                        tm_tuple = datetime.strptime(str(date1),'%Y-%m-%d %H:%M').timetuple()
                        month = tm_tuple.tm_mon
                        cr.execute("select id from hr_employee where REPLACE(sinid, '-', '') = '"+str(code)+"' or ltrim(ssnid,'0') = '"+str(code)+"' ")
                        emp_id = cr.fetchone()[0]
                        print ("emp_id----------",emp_id)
                        cr.execute("delete from raw_attendance where name='"+str(date1)+"' and employee_id = '"+str(emp_id)+"'")
                        print "==============RAW ATTENDANCE CREATED===============",count,date2,"==================",date1
                        #raw_obj.create(cr, uid, {'name':date1,'employee_id':emp_id})
                        obj = cr.execute('insert into raw_attendance (name,employee_id,month,year,year_id,active,m_id,search_date,real_name) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)', (date1,emp_id,str(month),str(year),str(year_id),True,m_id,date3,date1_real))
                    except:                                        
                        pass
                start_date += timedelta(days=1)                 
            cursor.close()             
        return True

    _columns = {
                'name':fields.char('Server Name',required=True,),
                'port':fields.char('Port',required=True,),
                'user':fields.char('User',required=True,),
                'password':fields.char('Password',required=True,),
                'database':fields.char('Database',required=True,),
                'date':fields.date('Start Date',required=True),
                'end_date':fields.date('End Date',required=True),
                'state':fields.selection([('draft','Draft'),('confirm','Confirm')],'State'),
                'employee_id': fields.many2one('hr.employee', "Employee"),
                }

    _defaults = {
                  'state':'draft',
                  }
     
    def confirm(self, cr, uid, ids, context=None):
         self.write(cr, uid, ids, {'state':'confirm'})
         return True
 
    def reset(self, cr, uid, ids, context=None):
         self.write(cr, uid, ids, {'state':'draft'})
         return True
     
      
class hr_attendance(osv.osv):
    _inherit = 'hr.attendance'
    _order = 'name desc,employee_id'

    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d %H:%M:%S').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                res[each.id] = year_id[0]  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res   
    
    _columns = {
                'department_id':fields.many2one('hr.department',string='Department'),
                'shift_id':fields.many2one('attendance.shift','Shift'),
                'day': fields.date('Day',),
                'name': fields.datetime('Date'),
                'sign':fields.selection([('Sign_in','Sign_in'),('Sign_out','Sign_out')],'Sign'),
                'employee_id': fields.many2one('hr.employee', "Employee's Name"),
                'month':fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),
                ('8','August'),('9','September'),('10','October'),('11','November'),('12','December'),],'Month'),
#                'year_id':fields.many2one('holiday.year','Year'),
                'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
                'action': fields.selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action'),
                'search_date':fields.date("Search Date"),
                'method':fields.selection([('Auto','Auto'),('Manual','Manual')],'Method'),
                'company_id':fields.many2one('res.company',string='Company'),
                'company_name':fields.related('company_id','name',relation='res.company',string='Company Name',type="char",readonly=True,store=True),
                'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),
                'year':fields.selection([('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),
                                                 ('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),
                                                 ('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),
                                                 ('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),
                                                 ('2030','2030'),('2031','2031'),('2032','2032'),('2033','2033'),
                                                 ('2034','2034'),('2035','2035'),],'YEAR'),
                }
    
    _defaults = {
                 'year':time.strftime('%Y'),
                 }
   
    def _altern_si_so(self, cr, uid, ids, context=None):
        return True

    _constraints = [(_altern_si_so, 'Error: Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]
    


    
class attendance_timing(osv.osv):
    _name = 'attendance.timing'
    _order = 'creation_date desc'
    
    def run_synchro_timing(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        holi_obj = self.pool.get('holiday.list.lines')
        shift_obj = self.pool.get('hr.shift.line')
        emp_list = []
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            if each.name:
                if each.employee_id and each.department_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('week','=','Sunday'),('doj', '<=',each.name)])
                elif each.employee_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('company_id','=',each.company_id.id),('week','=','Sunday'),('doj', '<=',each.name)])
                elif each.department_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('week','=','Sunday'),('doj', '<=',each.name)])
                elif each.company_id and each.employment_type:
                    print"1111111111111111"
                    list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('employment_type', '=', each.employment_type),('week','=','Sunday'),('doj', '<=',each.name)])
                elif each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('week','=','Sunday'),('doj', '<=',each.name)])
                elif each.employee_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('week','=','Sunday'),('doj', '<=',each.name)])
#                elif each.employment_type:
#                    list_ids = emp_obj.search(cr, uid, [('employment_type', '=', each.employment_type),('active','=',True),('week','=','Sunday'),('doj', '<=',each.name)])
                elif each.employee_id and each.department_id:
                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                elif each.department_id:
                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                else:
                    list_ids = emp_obj.search(cr, uid, [('active','=',True),('week','=','Sunday'),('doj', '<=',each.name)])
                
                if each.start_count>0 and each.to_count>0:
                    list_ids.sort()
                    list_ids = list_ids[each.start_count-1:each.to_count]

                if len(list_ids) == 1:
                    list_ids.append(list_ids[0])
                emp_list_ids = tuple(list_ids)
                if len(emp_list_ids) < 1:
                    raise osv.except_osv(_('Warning !'),_("No record found for this query."))                
               
                if each.name and not each.end_date:
                    count = 0
                    cr.execute("select employee_id from hr_attendance  where day='"+str(each.name)+"'  and employee_id in "+str(emp_list_ids)+" group by employee_id having count(id) % 2 = 0")
                    temp = cr.fetchall()
                    for val in temp:
                        emp_list.append(val[0])
                    emp_ids = emp_obj.browse(cr, uid, emp_list)
                    for emp in emp_ids:
                        print"========emp==========",emp.sinid,emp.name
                        count  += 1
                        emp_dict =  {}
                        cr.execute("select id from hr_shift_line  where name<='"+str(each.name)+"'  and employee_id = "+str(emp.id)+" and active=True order by name DESC")
                        qrys_shift_prev = cr.fetchall()
                        if qrys_shift_prev and qrys_shift_prev[0]:
                            prev_shift_ids = [qrys_shift_prev[0][0]]
                            print"====prev_shift_ids====",prev_shift_ids
                        else:
                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',each.name)], limit=1, order='name DESC')
                        
                        print"============---------prev_shift_ids==========",prev_shift_ids
                        next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',each.name)], limit=1, order='name ASC')
                        if prev_shift_ids:
                            shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                        elif next_shift_ids:
                            shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                        else:
                            raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                        if shift_data:
                            for line in shift_data.shift_id.shift_line:
                                sunday = return_back = False
                                timing = self.pool.get('wiz.attendance').calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                                
                                holiday_ids = holi_obj.search(cr, uid, [('leave_date','=',each.name),('week','=','Sunday')])
                                holiday_ids1 = holi_obj.search(cr, uid, [('leave_date','=',each.name),('week','<>','Sunday')])
                                if holiday_ids:
                                    sunday = True
                                    sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                    cr.execute(sunday_case)
                                    sunday_case_result = cr.fetchall()
                                    sun_oldpunch = False   
                                    sun_punch =  0.0     
                                    sun_count = 0      
                                    sun_mid = False  
                                    sun_total_punch = 0.0
                                    new_hrs = 0.0
                                    lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                    slunch = lunch + timedelta(hours=4)
                                    elunch = lunch + timedelta(hours=4,minutes=30)
                                    flunch = lunch + timedelta(hours=4,minutes=57)
                                    for case in sunday_case_result: 
                                        if len(case)>0 and case[0] != None:
                                            sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                            if sun_count == 0:
                                                if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                    sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                    sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                else:
                                                    new_time = case[0]
                                                if sun_newpunch > slunch and sun_newpunch < elunch:
                                                    sun_oldpunch = elunch
                                                else:
                                                    sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                            elif sun_count <> 0 and sun_count % 2 <> 0:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                
                                                sun_punch = sun_newpunch - sun_oldpunch
                                                sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                sun_total_punch = sun_total_punch + sun_punch_min
                                                sun_oldpunch = sun_newpunch
                                                
                                                sun_count += 1
                                            
                                            else:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                                        
                                    if sun_mid:
                                        sun_total_punch = sun_total_punch - line.lunch_time
                                            
                                    sun_punch_min = sun_total_punch
                                    new_hrs = sun_punch_min
                                    if emp_dict.get(str(emp.id),False):
                                        emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POW'})
                                    else:
                                        emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POW'}
                                        
                                elif holiday_ids1:
                                    sunday = True
                                    sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                    cr.execute(sunday_case)
                                    sunday_case_result = cr.fetchall()
                                    sun_oldpunch = False   
                                    sun_punch =  0.0     
                                    sun_count = 0      
                                    sun_mid = False  
                                    sun_total_punch = 0.0
                                    new_hrs = 0.0
                                    lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                    slunch = lunch + timedelta(hours=4)
                                    elunch = lunch + timedelta(hours=4,minutes=30)
                                    flunch = lunch + timedelta(hours=4,minutes=57)
                                    for case in sunday_case_result: 
                                        if len(case)>0 and case[0] != None:
                                            sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                            if sun_count == 0:
                                                if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                    sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                    sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                else:
                                                    new_time = case[0]
                                                if sun_newpunch > slunch and sun_newpunch < elunch:
                                                    sun_oldpunch = elunch
                                                else:
                                                    sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                            elif sun_count <> 0 and sun_count % 2 <> 0:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                
                                                sun_punch = sun_newpunch - sun_oldpunch
                                                sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                sun_total_punch = sun_total_punch + sun_punch_min
                                                sun_oldpunch = sun_newpunch
                                                
                                                sun_count += 1
                                            
                                            else:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                                        
                                    if sun_mid:
                                        sun_total_punch = sun_total_punch - line.lunch_time
                                            
                                    sun_punch_min = sun_total_punch
                                    new_hrs = sun_punch_min
                                    if emp_dict.get(str(emp.id),False):
                                        emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POH'})
                                    else:
                                        emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POH'}
                                    
        #=================================================================================================================================
                                else:  
                                    after_shift = "select min(name + interval '5 hours 30 minute') from hr_attendance where name + interval '5 hours 30 minute' > to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and name + interval '5 hours 30 minute' < to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and employee_id = '"+str(emp.id)+"'"
                                    cr.execute(after_shift)
                                    after_shift_result = cr.fetchall()  
                                    for data in after_shift_result:   
                                        if len(data)>0 and data[0] != None:
                                            if datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S') < datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S'):
                                                return_back = True
                                            else:
                                                if datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') > datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S') :
                                                    punch = datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') - datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
                                                    total_punch = (float(punch.total_seconds() / 60))
                                                    if total_punch > 15:
                                                        total_punch = float(punch.total_seconds() / 60) 
                                                    else:
                                                        total_punch = 0.0
                                                else:
                                                     total_punch = 0.0
                                                        
                                    punch_min1 = total_punch
                                    
                                    if not emp_dict.has_key(str(emp.id)):         
                                        query0 = "select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                 '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                 '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval \
                                                 '1 hours 30 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                                 )::timestamp + interval '10 minute'"
                                        
                                        cr.execute(query0)
                                        result0 = cr.fetchall()                                                
                                        for data in result0:
                                            if len(data)>0 and data[0] != None:
                                                if emp_dict.has_key(str(emp.id)):
                                                    emp_dict[str(emp.id)].update({'date':data[0]})
                                                else:
                                                    emp_dict[str(emp.id)] = {'date':data[0]} 
                                               
            #=========================================================================================================================================
                                    print "emp id===================",emp.id,after_shift_result[0][0]
                                    query8 = "select max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                             '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                             '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                              and to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp"
                                   
                                    cr.execute(query8)
                                    result8 = cr.fetchall() 

                                    if result8:
                                        if datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') > datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S'):
                                            punch = datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') - datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S')
                                            punch_min = float(punch.total_seconds() / 60)
                                            punch_hr = float(punch_min / 60)
                                            min = str(punch_hr)
                                            punch = min.split('.')
                                            a = int(punch[1])
                                            b = ((a * 60)/100)
                                            c = punch[0] + '.' + str(b)
                                            punch_hr1 = float(c)
                                            if punch_hr1 >= 5.45 :
                                                working = 'P'
                                            else:
                                                working = 'A'
                                                         
            #=========================================================================================================================================
                                    
                                    query090 = "select count(id) from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                    name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                    'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                    'YYYY-MM-DD HH24:MI:SS')::timestamp"
                                     
                                    cr.execute(query090)
                                    result090 = cr.fetchall()  
                                    cutt_off = timing['end_time'] 
                                    total_punch = 0.0
                                    for data090 in result090:
                                        if len(data090)>0 and data090[0] != None:
                                            query091 = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                            cr.execute(query091)
                                            result091 = cr.fetchall()  
                                            if int(data090[0]) % 2 <>  0:
                                                oldpunch = False   
                                                punch =  0.0     
                                                count = 0         
                                                for data091 in result091:  
                                                    if len(data091)>0 and data091[0] != None:
                                                        newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                        if count == 0:
                                                            oldpunch = datetime.strptime(cutt_off,'%Y-%m-%d %H:%M:%S')
                                                        if count <> 0 and count % 2 <> 0:
                                                            oldpunch = newpunch
                                                            count += 1
                                                            continue
                                                        if not oldpunch:
                                                            oldpunch = newpunch
                                                        else:
                                                            punch = newpunch - oldpunch
                                                            punch_min = float(punch.total_seconds() / 60)
                                                            total_punch = total_punch + punch_min
                                                            oldpunch = newpunch
                                                        count += 1
                                                                
                                            else:
                                                oldpunch = False   
                                                punch = 0.0              
                                                for data091 in result091:   
                                                    if len(data091)>0 and data091[0] != None:
                                                        newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                        if not oldpunch:
                                                            oldpunch = newpunch
                                                        else:
                                                            punch = newpunch - oldpunch
                                                            punch_min = float(punch.total_seconds() / 60)
                                                            total_punch = total_punch + punch_min
                                                            oldpunch = newpunch
                                                                        
                                    if total_punch > 5:
                                        punch_min = total_punch
                                    else:
                                        punch_min = 0.0
                                    
                                    punch =  punch_min
#                                    punch =  punch_min  + punch_min1          
                                    if  emp.ot_tick == True:      
                                         new_hrs = punch
                                    else:
                                         new_hrs = 0.0
                                     
                                    if emp_dict.has_key(str(emp.id)):
                                        if emp_dict[str(emp.id)].get('over_time',False):
                                            emp_dict[str(emp.id)]['over_time'] = emp_dict[str(emp.id)]['over_time'] + new_hrs
                                        else:
                                            emp_dict[str(emp.id)]['over_time'] = new_hrs
                                    else:
                                        if emp_dict.get(str(emp.id),False):
                                            emp_dict[str(emp.id)].update({'over_time': new_hrs})
                                        else:
                                            emp_dict[str(emp.id)] = {'over_time': new_hrs}
                                            
        #===================================================================================================================================
                                if return_back:
                                    continue
                                over_time = 0.0
                                penalty = 0.0
                                missing = 0.0
                                present = 0.0
                                missing = 0.0
                                new_over_time = 0.0
                                if emp_dict.get(str(emp.id),False):
                                    if emp_dict[str(emp.id)].get('over_time',False):
                                        over_time = emp_dict[str(emp.id)]['over_time']
                                        if over_time > 0:
                                            over_time =  round(over_time,2)
                                                
                                    if emp_dict[str(emp.id)].get('working',False):
                                        working = emp_dict[str(emp.id)].get('working')  
                                
                                    if emp_dict[str(emp.id)].get('present',False):
                                        present = emp_dict[str(emp.id)].get('present')   
                                    
                                    if sunday:    
                                        if emp_dict[str(emp.id)].get('sunday_time',False):
                                            over_time = emp_dict[str(emp.id)].get('sunday_time')
                                    
                                    tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                                    month = tm_tuple.tm_mon
                                    year = tm_tuple.tm_year        
                                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                                    
                                    if working == 'A':
                                        penalty = missing = over_time = 0.0
                                    
                                    over_time = over_time
                                    
                                    try:
                                        cr.execute("delete from attendance_timing where name='"+str(each.name)+"' and employee_id = '"+str(emp.id)+"' and method='Auto'")
                                        
                                        created_id = self.create(cr, uid, {'employee_id':emp.id,'name':each.name, 'working':working,'over_time':round(over_time,2),
                                                              'outside_time':0.0,'penalty':penalty,'sunday':sunday,'missing':missing,'present':present,
                                                              'month':str(month),'year_id':year_id and year_id[0] or False,'method':'Auto'})
                                        
                                         
                                        print "=========================NEW INDIVISIBLE WORKING RECORD IS CREATED==========================",created_id
                                    except:
                                        pass
                        else:
                            raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                else:
                    if each.name and each.end_date and each.employee_id:
                        count = 0
                        shift_data = []
                        start_date = datetime.strptime(each.name,'%Y-%m-%d')
                        end_date = datetime.strptime(each.end_date,'%Y-%m-%d')
                        end_tm_tuple = datetime.strptime(each.end_date,'%Y-%m-%d').timetuple()
                        while (start_date <= end_date):
                            emp_list=[]
                            cr.execute("select employee_id from hr_attendance  where day='"+str(start_date)+"' and employee_id in "+str(emp_list_ids)+" group by employee_id having count(id) % 2 = 0")
                            temp = cr.fetchall()
                            for val in temp:
                                emp_list.append(val[0])
                            emp_ids = emp_obj.browse(cr, uid, emp_list)
                            date1 = start_date.strftime('%Y-%m-%d')
                            tm_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()
                            if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                                break
                            if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                                break
                            for emp in emp_ids:
                                count  += 1
                                emp_dict =  {}
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',start_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',start_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        sunday = return_back = False
                                        timing = self.pool.get('wiz.attendance').calculate_time(cr, uid, ids, date1, line.from_time, line.to_time)
                                        
                                        holiday_ids = holi_obj.search(cr, uid, [('leave_date','=',start_date),('week','=','Sunday')])
                                        holiday_ids1 = holi_obj.search(cr, uid, [('leave_date','=',start_date),('week','<>','Sunday')])
                                        if holiday_ids:
                                            sunday = True
                                            sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                        name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                            cr.execute(sunday_case)
                                            sunday_case_result = cr.fetchall()
                                            sun_oldpunch = False   
                                            sun_punch =  0.0     
                                            sun_count = 0      
                                            sun_mid = False  
                                            sun_total_punch = 0.0
                                            new_hrs = 0.0
                                            lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                            slunch = lunch + timedelta(hours=4)
                                            elunch = lunch + timedelta(hours=4,minutes=30)
                                            flunch = lunch + timedelta(hours=4,minutes=57)
                                            for case in sunday_case_result: 
                                                if len(case)>0 and case[0] != None:
                                                    sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                                    if sun_count == 0:
                                                        if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                            sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                            sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        else:
                                                            new_time = case[0]
                                                        if sun_newpunch > slunch and sun_newpunch < elunch:
                                                            sun_oldpunch = elunch
                                                        else:
                                                            sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                    elif sun_count <> 0 and sun_count % 2 <> 0:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        
                                                        sun_punch = sun_newpunch - sun_oldpunch
                                                        sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                        sun_total_punch = sun_total_punch + sun_punch_min
                                                        sun_oldpunch = sun_newpunch
                                                        
                                                        sun_count += 1
                                                    
                                                    else:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                                
                                            if sun_mid:
                                                sun_total_punch = sun_total_punch - line.lunch_time
                                                    
                                            sun_punch_min = sun_total_punch
                                            new_hrs = sun_punch_min
                                            if emp_dict.get(str(emp.id),False):
                                                emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POW'})
                                            else:
                                                emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POW'}
                                        
                                        elif holiday_ids1:
                                            sunday = True
                                            sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                        name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                            cr.execute(sunday_case)
                                            sunday_case_result = cr.fetchall()
                                            sun_oldpunch = False   
                                            sun_punch =  0.0     
                                            sun_count = 0      
                                            sun_mid = False  
                                            sun_total_punch = 0.0
                                            new_hrs = 0.0
                                            lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                            slunch = lunch + timedelta(hours=4)
                                            elunch = lunch + timedelta(hours=4,minutes=30)
                                            flunch = lunch + timedelta(hours=4,minutes=57)
                                            for case in sunday_case_result: 
                                                if len(case)>0 and case[0] != None:
                                                    sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                                    if sun_count == 0:
                                                        if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                            sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                            sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        else:
                                                            new_time = case[0]
                                                        if sun_newpunch > slunch and sun_newpunch < elunch:
                                                            sun_oldpunch = elunch
                                                        else:
                                                            sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                    elif sun_count <> 0 and sun_count % 2 <> 0:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        
                                                        sun_punch = sun_newpunch - sun_oldpunch
                                                        sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                        sun_total_punch = sun_total_punch + sun_punch_min
                                                        sun_oldpunch = sun_newpunch
                                                        
                                                        sun_count += 1
                                                    
                                                    else:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                                
                                            if sun_mid:
                                                sun_total_punch = sun_total_punch - line.lunch_time
                                                    
                                            sun_punch_min = sun_total_punch
                                            new_hrs = sun_punch_min
                                            if emp_dict.get(str(emp.id),False):
                                                emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POH'})
                                            else:
                                                emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POH'}
                                            
                #=================================================================================================================================
                                        else:
                                            after_shift = "select min(name + interval '5 hours 30 minute') from hr_attendance where name + interval '5 hours 30 minute' > to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and name + interval '5 hours 30 minute' < to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and employee_id = '"+str(emp.id)+"'"
                                            cr.execute(after_shift)
                                            after_shift_result = cr.fetchall()   
                                            for data in after_shift_result:   
                                                if len(data)>0 and data[0] != None:
                                                    if datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S') < datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S'):
                                                        return_back = True
                                                    else:
                                                        if datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') > datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S') :
                                                            punch = datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') - datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
                                                            total_punch = (float(punch.total_seconds() / 60))
                                                            if total_punch > 15:
                                                                total_punch = float(punch.total_seconds() / 60) 
                                                            else:
                                                                total_punch = 0.0
                                                        else:
                                                             total_punch = 0.0
                                                                
                                            punch_min1 = total_punch
                                                        
                                            
                                            if not emp_dict.has_key(str(emp.id)):         
                                                query0 = "select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                         '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval \
                                                         '1 hours 30 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                                         )::timestamp + interval '10 minute'"
                                                
                                                cr.execute(query0)
                                                result0 = cr.fetchall()                                                
                                                for data in result0:
                                                    if len(data)>0 and data[0] != None:
                                                        if emp_dict.has_key(str(emp.id)):
                                                            emp_dict[str(emp.id)].update({'date':data[0]})
                                                        else:
                                                            emp_dict[str(emp.id)] = {'date':data[0]} 
                                                       
                                                        
                    #=========================================================================================================================================
            
                     
                                            query8 = "select max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                     '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                     '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                                      and to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp"
                                           
                                            
                                            cr.execute(query8)
                                            result8 = cr.fetchall()  
                                            if result8:
                                                if datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') > datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S'):
                                                    punch = datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') - datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S')
                                                    punch_min = float(punch.total_seconds() / 60)
                                                    punch_hr = float(punch_min / 60)
                                                    min = str(punch_hr)
                                                    punch = min.split('.')
                                                    a = int(punch[1])
                                                    b = ((a * 60)/100)
                                                    c = punch[0] + '.' + str(b)
                                                    punch_hr1 = float(c)
                                                    if punch_hr1 >= 5.45 :
                                                      working = 'P'
                                                    else:
                                                       working = 'A'
                                       
                    #=========================================================================================================================================
                                            
                                            query090 = "select count(id) from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                            name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp"
                                             
                                            cr.execute(query090)
                                            result090 = cr.fetchall()  
                                            cutt_off = timing['end_time'] 
                                            total_punch = 0.0
                                            for data090 in result090:  
                                                
                                                if len(data090)>0 and data090[0] != None:
                                                    query091 = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                        name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                                    cr.execute(query091)
                                                    result091 = cr.fetchall()  
                                                    if int(data090[0]) % 2 <>  0:
                                                        oldpunch = False   
                                                        punch =  0.0     
                                                        count = 0         
                                                        for data091 in result091:  
                                                            if len(data091)>0 and data091[0] != None:
                                                                newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                                if count == 0:
                                                                    oldpunch = datetime.strptime(cutt_off,'%Y-%m-%d %H:%M:%S')
                                                                if count <> 0 and count % 2 <> 0:
                                                                    oldpunch = newpunch
                                                                    count += 1
                                                                    continue
                                                                if not oldpunch:
                                                                    oldpunch = newpunch
                                                                else:
                                                                    punch = newpunch - oldpunch
                                                                    punch_min = float(punch.total_seconds() / 60)
                                                                    total_punch = total_punch + punch_min
                                                                    oldpunch = newpunch
                                                                count += 1
                                                                        
                                                    else:
                                                        oldpunch = False   
                                                        punch = 0.0              
                                                        for data091 in result091:   
                                                            if len(data091)>0 and data091[0] != None:
                                                                newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                                if not oldpunch:
                                                                    oldpunch = newpunch
                                                                else:
                                                                    punch = newpunch - oldpunch
                                                                    punch_min = float(punch.total_seconds() / 60)
                                                                    total_punch = total_punch + punch_min
                                                                    oldpunch = newpunch
                                                                                
                                            if total_punch > 5:
                                                punch_min = total_punch
                                            else:
                                                punch_min = 0.0
                                            
                                            punch =  punch_min
#                                            punch =  punch_min  + punch_min1     
                                            if  emp.ot_tick == True:      
                                                 new_hrs = punch
                                            else:
                                                 new_hrs = 0.0
                                                        
                                            if emp_dict.has_key(str(emp.id)):
                                                if emp_dict[str(emp.id)].get('over_time',False):
                                                    emp_dict[str(emp.id)]['over_time'] = emp_dict[str(emp.id)]['over_time'] + new_hrs
                                                else:
                                                    emp_dict[str(emp.id)]['over_time'] = new_hrs
                                            else:
                                                if emp_dict.get(str(emp.id),False):
                                                    emp_dict[str(emp.id)].update({'over_time': new_hrs})
                                                else:
                                                    emp_dict[str(emp.id)] = {'over_time': new_hrs}
                                                    
                #===================================================================================================================================
                                        if return_back:
                                            continue
                                        over_time = 0.0
                                        penalty = 0.0
                                        missing = 0.0
                                        present = 0.0
                                        missing = 0.0
                                        new_over_time = 0.0
                                        if emp_dict.get(str(emp.id),False):
                                            if emp_dict[str(emp.id)].get('over_time',False):
                                                over_time = emp_dict[str(emp.id)]['over_time']
                                                if over_time > 0:
                                                    over_time =  round(over_time,2)
                                                        
                                            if emp_dict[str(emp.id)].get('working',False):
                                                working = emp_dict[str(emp.id)].get('working')  
                                        
                                            if emp_dict[str(emp.id)].get('present',False):
                                                present = emp_dict[str(emp.id)].get('present')   
                                            
                                            if sunday:    
                                                if emp_dict[str(emp.id)].get('sunday_time',False):
                                                    over_time = emp_dict[str(emp.id)].get('sunday_time')
                                            
                                            tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                                            month = tm_tuple.tm_mon
                                            year = tm_tuple.tm_year        
                                            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                                              
                                            if working == 'A':
                                                penalty = missing = over_time = 0.0
                                                
                                            over_time = over_time
                                            try:
                                                cr.execute("delete from attendance_timing where name='"+str(start_date)+"' and employee_id = '"+str(emp.id)+"' and method='Auto'")
                                                
                                                created_id = self.create(cr, uid, {'employee_id':emp.id,'name':start_date, 'working':working,'over_time':round(over_time,2),
                                                                      'outside_time':0.0,'penalty':penalty,'sunday':sunday,'missing':missing,'present':present,
                                                                      'month':str(month),'year_id':year_id and year_id[0] or False,'method':'Auto'})
                                                
                                                 
                                                print "=========================NEW INDIVISIBLE WORKING RECORD IS CREATED=========================",created_id
                                            except:
                                                pass
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                            start_date += timedelta(days=1)
        return True
    

    def run_synchro_timing_comp(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        holi_obj = self.pool.get('holiday.list.lines')
        shift_obj = self.pool.get('hr.shift.line')
        emp_list = []
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            if each.name:
                if each.employee_id and each.department_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
                elif each.employee_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
                elif each.department_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
                elif each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
                elif each.employee_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('doj', '<=',each.name)])
                elif each.employee_id and each.department_id:
                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                elif each.department_id:
                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                else:
                    list_ids = emp_obj.search(cr, uid, [('active','=',True),('doj', '<=',each.name)])
                
                if len(list_ids) == 1:
                    list_ids.append(list_ids[0])
                emp_list_ids = tuple(list_ids)
                if len(emp_list_ids) < 1:
                    raise osv.except_osv(_('Warning !'),_("No record found for this query."))                
               
                if each.name and not each.end_date:
                    count = 0
                    cr.execute("select employee_id from hr_attendance  where day='"+str(each.name)+"'  and employee_id in "+str(emp_list_ids)+" group by employee_id having count(id) % 2 = 0")
                    temp = cr.fetchall()
                    for val in temp:
                        emp_list.append(val[0])
                    emp_ids = emp_obj.browse(cr, uid, emp_list)
                    for emp in emp_ids:
                        count  += 1
                        emp_dict =  {}
                        prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',each.name)], limit=1, order='name DESC')
                        next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',each.name)], limit=1, order='name ASC')
                        if prev_shift_ids:
                            shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                        elif next_shift_ids:
                            shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                        else:
                            raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                        if shift_data:
                            for line in shift_data.shift_id.shift_line:
                                sunday = return_back = False
                                timing = self.pool.get('wiz.attendance').calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                                
                                holiday_ids = holi_obj.search(cr, uid, [('leave_date','=',each.name),('week','=','Sunday')])
                                holiday_ids1 = holi_obj.search(cr, uid, [('leave_date','=',each.name),('week','<>','Sunday')])
                                if holiday_ids:
                                    sunday = True
                                    sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                    cr.execute(sunday_case)
                                    sunday_case_result = cr.fetchall()
                                    sun_oldpunch = False   
                                    sun_punch =  0.0     
                                    sun_count = 0      
                                    sun_mid = False  
                                    sun_total_punch = 0.0
                                    new_hrs = 0.0
                                    lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                    slunch = lunch + timedelta(hours=4)
                                    elunch = lunch + timedelta(hours=4,minutes=30)
                                    flunch = lunch + timedelta(hours=4,minutes=57)
                                    for case in sunday_case_result: 
                                        if len(case)>0 and case[0] != None:
                                            sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                            if sun_count == 0:
                                                if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                    sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                    sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                else:
                                                    new_time = case[0]
                                                if sun_newpunch > slunch and sun_newpunch < elunch:
                                                    sun_oldpunch = elunch
                                                else:
                                                    sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                            elif sun_count <> 0 and sun_count % 2 <> 0:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                
                                                sun_punch = sun_newpunch - sun_oldpunch
                                                sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                sun_total_punch = sun_total_punch + sun_punch_min
                                                sun_oldpunch = sun_newpunch
                                                
                                                sun_count += 1
                                            
                                            else:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                                        
                                    if sun_mid:
                                        sun_total_punch = sun_total_punch - line.lunch_time
                                            
                                    sun_punch_min = sun_total_punch
                                    new_hrs = sun_punch_min
                                    if emp_dict.get(str(emp.id),False):
                                        emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POW'})
                                    else:
                                        emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POW'}
                                        
                                elif holiday_ids1:
                                    sunday = True
                                    sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                    cr.execute(sunday_case)
                                    sunday_case_result = cr.fetchall()
                                    sun_oldpunch = False   
                                    sun_punch =  0.0     
                                    sun_count = 0      
                                    sun_mid = False  
                                    sun_total_punch = 0.0
                                    new_hrs = 0.0
                                    lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                    slunch = lunch + timedelta(hours=4)
                                    elunch = lunch + timedelta(hours=4,minutes=30)
                                    flunch = lunch + timedelta(hours=4,minutes=57)
                                    for case in sunday_case_result: 
                                        if len(case)>0 and case[0] != None:
                                            sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                            if sun_count == 0:
                                                if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                    sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                    sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                else:
                                                    new_time = case[0]
                                                if sun_newpunch > slunch and sun_newpunch < elunch:
                                                    sun_oldpunch = elunch
                                                else:
                                                    sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                            elif sun_count <> 0 and sun_count % 2 <> 0:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                
                                                sun_punch = sun_newpunch - sun_oldpunch
                                                sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                sun_total_punch = sun_total_punch + sun_punch_min
                                                sun_oldpunch = sun_newpunch
                                                
                                                sun_count += 1
                                            
                                            else:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                                        
                                    if sun_mid:
                                        sun_total_punch = sun_total_punch - line.lunch_time
                                            
                                    sun_punch_min = sun_total_punch
                                    new_hrs = sun_punch_min
                                    if emp_dict.get(str(emp.id),False):
                                        emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POH'})
                                    else:
                                        emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POH'}
                                    
        #=================================================================================================================================
                                else:  
                                    after_shift = "select min(name + interval '5 hours 30 minute') from hr_attendance where name + interval '5 hours 30 minute' > to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and name + interval '5 hours 30 minute' < to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and employee_id = '"+str(emp.id)+"'"
                                    cr.execute(after_shift)
                                    after_shift_result = cr.fetchall()  
                                    for data in after_shift_result:   
                                        if len(data)>0 and data[0] != None:
                                            if datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S') < datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S'):
                                                return_back = True
                                            else:
                                                if datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') > datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S') :
                                                    punch = datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') - datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
                                                    total_punch = (float(punch.total_seconds() / 60))
                                                    if total_punch > 15:
                                                        total_punch = float(punch.total_seconds() / 60) 
                                                    else:
                                                        total_punch = 0.0
                                                else:
                                                     total_punch = 0.0
                                                        
                                    punch_min1 = total_punch
                                    
                                    if not emp_dict.has_key(str(emp.id)):         
                                        query0 = "select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                 '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                 '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval \
                                                 '1 hours 30 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                                 )::timestamp + interval '10 minute'"
                                        
                                        cr.execute(query0)
                                        result0 = cr.fetchall()                                                
                                        for data in result0:
                                            if len(data)>0 and data[0] != None:
                                                if emp_dict.has_key(str(emp.id)):
                                                    emp_dict[str(emp.id)].update({'date':data[0]})
                                                else:
                                                    emp_dict[str(emp.id)] = {'date':data[0]} 
                                               
            #=========================================================================================================================================                                    
                                                
                                    if not emp_dict.has_key(str(emp.id)):         
                                        query1 = "select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                 '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                 '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                                 '11 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                                 )::timestamp + interval '15 minute'"
                                        
                                        cr.execute(query1)
                                        result1 = cr.fetchall()                                                
                                        for data in result1:
                                            if len(data)>0 and data[0] != None:
                                                if emp_dict.has_key(str(emp.id)):
                                                    emp_dict[str(emp.id)].update({'date':data[0]})
                                                else:
                                                    emp_dict[str(emp.id)] = {'date':data[0]} 
                                               
            #=========================================================================================================================================
             
                                    query8 = "select max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                             '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                             '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                              and to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp"
                                   
                                    cr.execute(query8)
                                    result8 = cr.fetchall()     
                                    if result8:
                                        if datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') > datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S'):
                                            punch = datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') - datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S')
                                            punch_min = float(punch.total_seconds() / 60)
                                            punch_hr = float(punch_min / 60)
                                            min = str(punch_hr)
                                            punch = min.split('.')
                                            a = int(punch[1])
                                            b = ((a * 60)/100)
                                            c = punch[0] + '.' + str(b)
                                            punch_hr1 = float(c)
                                            if punch_hr1 >= 5.45 :
                                                working = 'P'
                                            else:
                                                working = 'A'
                                                         
            #=========================================================================================================================================
                                    
                                    query090 = "select count(id) from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                    name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                    'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                    'YYYY-MM-DD HH24:MI:SS')::timestamp"
                                     
                                    cr.execute(query090)
                                    result090 = cr.fetchall()  
                                    cutt_off = timing['end_time'] 
                                    total_punch = 0.0
                                    for data090 in result090:
                                        if len(data090)>0 and data090[0] != None:
                                            query091 = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                            cr.execute(query091)
                                            result091 = cr.fetchall()  
                                            if int(data090[0]) % 2 <>  0:
                                                oldpunch = False   
                                                punch =  0.0     
                                                count = 0         
                                                for data091 in result091:  
                                                    if len(data091)>0 and data091[0] != None:
                                                        newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                        if count == 0:
                                                            oldpunch = datetime.strptime(cutt_off,'%Y-%m-%d %H:%M:%S')
                                                        if count <> 0 and count % 2 <> 0:
                                                            oldpunch = newpunch
                                                            count += 1
                                                            continue
                                                        if not oldpunch:
                                                            oldpunch = newpunch
                                                        else:
                                                            punch = newpunch - oldpunch
                                                            punch_min = float(punch.total_seconds() / 60)
                                                            total_punch = total_punch + punch_min
                                                            oldpunch = newpunch
                                                        count += 1
                                                                
                                            else:
                                                oldpunch = False   
                                                punch = 0.0              
                                                for data091 in result091:   
                                                    if len(data091)>0 and data091[0] != None:
                                                        newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                        if not oldpunch:
                                                            oldpunch = newpunch
                                                        else:
                                                            punch = newpunch - oldpunch
                                                            punch_min = float(punch.total_seconds() / 60)
                                                            total_punch = total_punch + punch_min
                                                            oldpunch = newpunch
                                                                        
                                    if total_punch > 5:
                                        punch_min = total_punch
                                    else:
                                        punch_min = 0.0
                                    
                                    punch =  punch_min
#                                    punch =  punch_min  + punch_min1          
                                    new_hrs = punch
                                     
                                    if emp_dict.has_key(str(emp.id)):
                                        if emp_dict[str(emp.id)].get('over_time',False):
                                            emp_dict[str(emp.id)]['over_time'] = emp_dict[str(emp.id)]['over_time'] + new_hrs
                                        else:
                                            emp_dict[str(emp.id)]['over_time'] = new_hrs
                                    else:
                                        if emp_dict.get(str(emp.id),False):
                                            emp_dict[str(emp.id)].update({'over_time': new_hrs})
                                        else:
                                            emp_dict[str(emp.id)] = {'over_time': new_hrs}
                                            
        #===================================================================================================================================
                                if return_back:
                                    continue
                                over_time = 0.0
                                penalty = 0.0
                                missing = 0.0
                                present = 0.0
                                missing = 0.0
                                new_over_time = 0.0
                                if emp_dict.get(str(emp.id),False):
                                    if emp_dict[str(emp.id)].get('over_time',False):
                                        over_time = emp_dict[str(emp.id)]['over_time']
                                        if over_time > 0:
                                            over_time =  round(over_time,2)
                                                
                                    if emp_dict[str(emp.id)].get('working',False):
                                        working = emp_dict[str(emp.id)].get('working')  
                                
                                    if emp_dict[str(emp.id)].get('present',False):
                                        present = emp_dict[str(emp.id)].get('present')   
                                    
                                    if sunday:    
                                        if emp_dict[str(emp.id)].get('sunday_time',False):
                                            over_time = emp_dict[str(emp.id)].get('sunday_time')
                                    
                                    tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                                    month = tm_tuple.tm_mon
                                    year = tm_tuple.tm_year        
                                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                                    
                                    if working == 'A':
                                        penalty = missing = over_time = 0.0
                                    
                                    over_time = over_time
                                    
                                    try:
                                        cr.execute("delete from attendance_timing where name='"+str(each.name)+"' and employee_id = '"+str(emp.id)+"' and method='Auto'")
                                        
                                        created_id = self.create(cr, uid, {'employee_id':emp.id,'name':each.name, 'working':working,'over_time':round(over_time,2),
                                                              'outside_time':0.0,'penalty':penalty,'sunday':sunday,'missing':missing,'present':present,
                                                              'month':str(month),'year_id':year_id and year_id[0] or False,'method':'Auto'})
                                        
                                         
                                        print "=========================NEW INDIVISIBLE WORKING RECORD IS CREATED==========================",created_id
                                    except:
                                        pass
                        else:
                            raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                else:
                    if each.name and each.end_date and each.employee_id:
                        count = 0
                        shift_data = []
                        start_date = datetime.strptime(each.name,'%Y-%m-%d')
                        end_date = datetime.strptime(each.end_date,'%Y-%m-%d')
                        end_tm_tuple = datetime.strptime(each.end_date,'%Y-%m-%d').timetuple()
                        while (start_date <= end_date):
                            emp_list=[]
                            cr.execute("select employee_id from hr_attendance  where day='"+str(start_date)+"' and employee_id in "+str(emp_list_ids)+" group by employee_id having count(id) % 2 = 0")
                            temp = cr.fetchall()
                            for val in temp:
                                emp_list.append(val[0])
                            emp_ids = emp_obj.browse(cr, uid, emp_list)
                            date1 = start_date.strftime('%Y-%m-%d')
                            tm_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()
                            if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                                break
                            if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                                break
                            for emp in emp_ids:
                                count  += 1
                                emp_dict =  {}
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',start_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',start_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        sunday = return_back = False
                                        timing = self.pool.get('wiz.attendance').calculate_time(cr, uid, ids, date1, line.from_time, line.to_time)
                                        
                                        holiday_ids = holi_obj.search(cr, uid, [('leave_date','=',start_date),('week','=','Sunday')])
                                        holiday_ids1 = holi_obj.search(cr, uid, [('leave_date','=',start_date),('week','<>','Sunday')])
                                        if holiday_ids:
                                            sunday = True
                                            sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                        name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                            cr.execute(sunday_case)
                                            sunday_case_result = cr.fetchall()
                                            sun_oldpunch = False   
                                            sun_punch =  0.0     
                                            sun_count = 0      
                                            sun_mid = False  
                                            sun_total_punch = 0.0
                                            new_hrs = 0.0
                                            lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                            slunch = lunch + timedelta(hours=4)
                                            elunch = lunch + timedelta(hours=4,minutes=30)
                                            flunch = lunch + timedelta(hours=4,minutes=57)
                                            for case in sunday_case_result: 
                                                if len(case)>0 and case[0] != None:
                                                    sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                                    if sun_count == 0:
                                                        if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                            sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                            sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        else:
                                                            new_time = case[0]
                                                        if sun_newpunch > slunch and sun_newpunch < elunch:
                                                            sun_oldpunch = elunch
                                                        else:
                                                            sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                    elif sun_count <> 0 and sun_count % 2 <> 0:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        
                                                        sun_punch = sun_newpunch - sun_oldpunch
                                                        sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                        sun_total_punch = sun_total_punch + sun_punch_min
                                                        sun_oldpunch = sun_newpunch
                                                        
                                                        sun_count += 1
                                                    
                                                    else:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                                
                                            if sun_mid:
                                                sun_total_punch = sun_total_punch - line.lunch_time
                                                    
                                            sun_punch_min = sun_total_punch
                                            new_hrs = sun_punch_min
                                            if emp_dict.get(str(emp.id),False):
                                                emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POW'})
                                            else:
                                                emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POW'}
                                        
                                        elif holiday_ids1:
                                            sunday = True
                                            sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                        name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                            cr.execute(sunday_case)
                                            sunday_case_result = cr.fetchall()
                                            sun_oldpunch = False   
                                            sun_punch =  0.0     
                                            sun_count = 0      
                                            sun_mid = False  
                                            sun_total_punch = 0.0
                                            new_hrs = 0.0
                                            lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                            slunch = lunch + timedelta(hours=4)
                                            elunch = lunch + timedelta(hours=4,minutes=30)
                                            flunch = lunch + timedelta(hours=4,minutes=57)
                                            for case in sunday_case_result: 
                                                if len(case)>0 and case[0] != None:
                                                    sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                                    if sun_count == 0:
                                                        if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                            sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                            sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        else:
                                                            new_time = case[0]
                                                        if sun_newpunch > slunch and sun_newpunch < elunch:
                                                            sun_oldpunch = elunch
                                                        else:
                                                            sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                    elif sun_count <> 0 and sun_count % 2 <> 0:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        
                                                        sun_punch = sun_newpunch - sun_oldpunch
                                                        sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                        sun_total_punch = sun_total_punch + sun_punch_min
                                                        sun_oldpunch = sun_newpunch
                                                        
                                                        sun_count += 1
                                                    
                                                    else:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                                
                                            if sun_mid:
                                                sun_total_punch = sun_total_punch - line.lunch_time
                                                    
                                            sun_punch_min = sun_total_punch
                                            new_hrs = sun_punch_min
                                            if emp_dict.get(str(emp.id),False):
                                                emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POH'})
                                            else:
                                                emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POH'}
                                            
                #=================================================================================================================================
                                        else:
                                            after_shift = "select min(name + interval '5 hours 30 minute') from hr_attendance where name + interval '5 hours 30 minute' > to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and name + interval '5 hours 30 minute' < to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and employee_id = '"+str(emp.id)+"'"
                                            cr.execute(after_shift)
                                            after_shift_result = cr.fetchall()   
                                            for data in after_shift_result:   
                                                if len(data)>0 and data[0] != None:
                                                    if datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S') < datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S'):
                                                        return_back = True
                                                    else:
                                                        if datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') > datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S') :
                                                            punch = datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') - datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
                                                            total_punch = (float(punch.total_seconds() / 60))
                                                            if total_punch > 15:
                                                                total_punch = float(punch.total_seconds() / 60) 
                                                            else:
                                                                total_punch = 0.0
                                                        else:
                                                             total_punch = 0.0
                                                                
                                            punch_min1 = total_punch
                                                        
                                            
                                            if not emp_dict.has_key(str(emp.id)):         
                                                query0 = "select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                         '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval \
                                                         '1 hours 30 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                                         )::timestamp + interval '10 minute'"
                                                
                                                cr.execute(query0)
                                                result0 = cr.fetchall()                                                
                                                for data in result0:
                                                    if len(data)>0 and data[0] != None:
                                                        if emp_dict.has_key(str(emp.id)):
                                                            emp_dict[str(emp.id)].update({'date':data[0]})
                                                        else:
                                                            emp_dict[str(emp.id)] = {'date':data[0]} 
                                                       
                                                        
                    #=========================================================================================================================================                                    
                                                        
                                            if not emp_dict.has_key(str(emp.id)):         
                                                query1 = "select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                         '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                                         '11 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                                         )::timestamp + interval '15 minute'"
                                                
                                                cr.execute(query1)
                                                result1 = cr.fetchall()                                                
                                                for data in result1:
                                                    if len(data)>0 and data[0] != None:
                                                        if emp_dict.has_key(str(emp.id)):
                                                            emp_dict[str(emp.id)].update({'date':data[0]})
                                                        else:
                                                            emp_dict[str(emp.id)] = {'date':data[0]} 
                                                       
                    #=========================================================================================================================================
            
                     
                                            query8 = "select max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                     '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                     '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                                      and to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp"
                                           
                                            
                                            cr.execute(query8)
                                            result8 = cr.fetchall()  
                                            if result8:
                                                if datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') > datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S'):
                                                    punch = datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') - datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S')
                                                    punch_min = float(punch.total_seconds() / 60)
                                                    punch_hr = float(punch_min / 60)
                                                    min = str(punch_hr)
                                                    punch = min.split('.')
                                                    a = int(punch[1])
                                                    b = ((a * 60)/100)
                                                    c = punch[0] + '.' + str(b)
                                                    punch_hr1 = float(c)
                                                    if punch_hr1 >= 5.45 :
                                                      working = 'P'
                                                    else:
                                                       working = 'A'
                                       
                    #=========================================================================================================================================
                                            
                                            query090 = "select count(id) from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                            name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp"
                                             
                                            cr.execute(query090)
                                            result090 = cr.fetchall()  
                                            cutt_off = timing['end_time'] 
                                            total_punch = 0.0
                                            for data090 in result090:  
                                                
                                                if len(data090)>0 and data090[0] != None:
                                                    query091 = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                        name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                                    cr.execute(query091)
                                                    result091 = cr.fetchall()  
                                                    if int(data090[0]) % 2 <>  0:
                                                        oldpunch = False   
                                                        punch =  0.0     
                                                        count = 0         
                                                        for data091 in result091:  
                                                            if len(data091)>0 and data091[0] != None:
                                                                newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                                if count == 0:
                                                                    oldpunch = datetime.strptime(cutt_off,'%Y-%m-%d %H:%M:%S')
                                                                if count <> 0 and count % 2 <> 0:
                                                                    oldpunch = newpunch
                                                                    count += 1
                                                                    continue
                                                                if not oldpunch:
                                                                    oldpunch = newpunch
                                                                else:
                                                                    punch = newpunch - oldpunch
                                                                    punch_min = float(punch.total_seconds() / 60)
                                                                    total_punch = total_punch + punch_min
                                                                    oldpunch = newpunch
                                                                count += 1
                                                                        
                                                    else:
                                                        oldpunch = False   
                                                        punch = 0.0              
                                                        for data091 in result091:   
                                                            if len(data091)>0 and data091[0] != None:
                                                                newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                                if not oldpunch:
                                                                    oldpunch = newpunch
                                                                else:
                                                                    punch = newpunch - oldpunch
                                                                    punch_min = float(punch.total_seconds() / 60)
                                                                    total_punch = total_punch + punch_min
                                                                    oldpunch = newpunch
                                                                                
                                            if total_punch > 5:
                                                punch_min = total_punch
                                            else:
                                                punch_min = 0.0
                                            
                                            punch =  punch_min
#                                            punch =  punch_min  + punch_min1    
                                            new_hrs = punch
                                                        
                                            if emp_dict.has_key(str(emp.id)):
                                                if emp_dict[str(emp.id)].get('over_time',False):
                                                    emp_dict[str(emp.id)]['over_time'] = emp_dict[str(emp.id)]['over_time'] + new_hrs
                                                else:
                                                    emp_dict[str(emp.id)]['over_time'] = new_hrs
                                            else:
                                                if emp_dict.get(str(emp.id),False):
                                                    emp_dict[str(emp.id)].update({'over_time': new_hrs})
                                                else:
                                                    emp_dict[str(emp.id)] = {'over_time': new_hrs}
                                                    
                #===================================================================================================================================
                                        if return_back:
                                            continue
                                        over_time = 0.0
                                        penalty = 0.0
                                        missing = 0.0
                                        present = 0.0
                                        missing = 0.0
                                        new_over_time = 0.0
                                        if emp_dict.get(str(emp.id),False):
                                            if emp_dict[str(emp.id)].get('over_time',False):
                                                over_time = emp_dict[str(emp.id)]['over_time']
                                                if over_time > 0:
                                                    over_time =  round(over_time,2)
                                                        
                                            if emp_dict[str(emp.id)].get('working',False):
                                                working = emp_dict[str(emp.id)].get('working')  
                                        
                                            if emp_dict[str(emp.id)].get('present',False):
                                                present = emp_dict[str(emp.id)].get('present')   
                                            
                                            if sunday:    
                                                if emp_dict[str(emp.id)].get('sunday_time',False):
                                                    over_time = emp_dict[str(emp.id)].get('sunday_time')
                                            
                                            tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                                            month = tm_tuple.tm_mon
                                            year = tm_tuple.tm_year        
                                            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                                              
                                            if working == 'A':
                                                penalty = missing = over_time = 0.0
                                                
                                            over_time = over_time
                                            try:
                                                cr.execute("delete from attendance_timing where name='"+str(start_date)+"' and employee_id = '"+str(emp.id)+"' and method='Auto'")
                                                
                                                created_id = self.create(cr, uid, {'employee_id':emp.id,'name':start_date, 'working':working,'over_time':round(over_time,2),
                                                                      'outside_time':0.0,'penalty':penalty,'sunday':sunday,'missing':missing,'present':present,
                                                                      'month':str(month),'year_id':year_id and year_id[0] or False,'method':'Auto'})
                                                
                                                 
                                                print "=========================NEW INDIVISIBLE WORKING RECORD IS CREATED=========================",created_id
                                            except:
                                                pass
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                            start_date += timedelta(days=1)
        return True


    def run_synchro_timing11(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        holi_obj = self.pool.get('holiday.list.lines')
        shift_obj = self.pool.get('hr.shift.line')
        emp_list = []
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            if each.name:
                if each.employee_id and each.department_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('week','<>','Sunday'),('doj', '<=',each.name)])
                elif each.employee_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('company_id','=',each.company_id.id),('week','<>','Sunday'),('doj', '<=',each.name)])
                elif each.department_id and each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('week','<>','Sunday'),('doj', '<=',each.name)])
                elif each.company_id and each.employment_type:
                    list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('employment_type', '=', each.employment_type),('week','<>','Sunday'),('doj', '<=',each.name)])
                elif each.company_id:
                    list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('week','<>','Sunday'),('doj', '<=',each.name)])
                elif each.employee_id:
                    list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('week','<>','Sunday'),('doj', '<=',each.name)])
#                elif each.employment_type:
#                    list_ids = emp_obj.search(cr, uid, [('employment_type', '=', each.employment_type),('active','=',True),('week','<>','Sunday'),('doj', '<=',each.name)])
                
                elif each.employee_id and each.department_id:
                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                elif each.department_id:
                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                else:
                    list_ids = emp_obj.search(cr, uid, [('active','=',True),('week','<>','Sunday'),('doj', '<=',each.name)])
                
                if len(list_ids) == 1:
                    list_ids.append(list_ids[0])
                emp_list_ids = tuple(list_ids)
                if len(emp_list_ids) < 1:
                    raise osv.except_osv(_('Warning !'),_("No record found for this query."))                
               
                if each.name and not each.end_date:
                    count = 0
                    cr.execute("select employee_id from hr_attendance  where day='"+str(each.name)+"'  and employee_id in "+str(emp_list_ids)+" group by employee_id having count(id) % 2 = 0")
                    temp = cr.fetchall()
                    for val in temp:
                        emp_list.append(val[0])
                    emp_ids = emp_obj.browse(cr, uid, emp_list)
                    for emp in emp_ids:
                        count  += 1
                        emp_dict =  {}
                        prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',each.name)], limit=1, order='name DESC')
                        next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',each.name)], limit=1, order='name ASC')
                        if prev_shift_ids:
                            shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                        elif next_shift_ids:
                            shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                        else:
                            raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                        if shift_data:
                            for line in shift_data.shift_id.shift_line:
                                sunday = return_back = False
                                timing = self.pool.get('wiz.attendance').calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                                
                                holiday_ids1 = holi_obj.search(cr, uid, [('leave_date','=',each.name),('week','<>','Sunday')])
                                if holiday_ids1:
                                    sunday = True
                                    sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                    cr.execute(sunday_case)
                                    sunday_case_result = cr.fetchall()
                                    sun_oldpunch = False   
                                    sun_punch =  0.0     
                                    sun_count = 0      
                                    sun_mid = False  
                                    sun_total_punch = 0.0
                                    new_hrs = 0.0
                                    lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                    slunch = lunch + timedelta(hours=4)
                                    elunch = lunch + timedelta(hours=4,minutes=30)
                                    flunch = lunch + timedelta(hours=4,minutes=57)
                                    for case in sunday_case_result: 
                                        if len(case)>0 and case[0] != None:
                                            sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                            if sun_count == 0:
                                                if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                    sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                    sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                else:
                                                    new_time = case[0]
                                                if sun_newpunch > slunch and sun_newpunch < elunch:
                                                    sun_oldpunch = elunch
                                                else:
                                                    sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                            elif sun_count <> 0 and sun_count % 2 <> 0:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                
                                                sun_punch = sun_newpunch - sun_oldpunch
                                                sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                sun_total_punch = sun_total_punch + sun_punch_min
                                                sun_oldpunch = sun_newpunch
                                                
                                                sun_count += 1
                                            
                                            else:
                                                if sun_newpunch > slunch and sun_newpunch < flunch:
                                                    sun_newpunch = slunch
                                                elif sun_newpunch > flunch:
                                                    sun_newpunch = sun_newpunch
                                                    sun_mid = True
                                                sun_oldpunch = sun_newpunch
                                                sun_count += 1
                                                        
                                    if sun_mid:
                                        sun_total_punch = sun_total_punch - line.lunch_time
                                            
                                    sun_punch_min = sun_total_punch
                                    new_hrs = sun_punch_min
                                    if emp_dict.get(str(emp.id),False):
                                        emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POH'})
                                    else:
                                        emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POH'}
                                    
        #=================================================================================================================================
                                else:  
                                    after_shift = "select min(name + interval '5 hours 30 minute') from hr_attendance where name + interval '5 hours 30 minute' > to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and name + interval '5 hours 30 minute' < to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and employee_id = '"+str(emp.id)+"'"
                                    cr.execute(after_shift)
                                    after_shift_result = cr.fetchall()  
                                    for data in after_shift_result:   
                                        if len(data)>0 and data[0] != None:
                                            if datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S') < datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S'):
                                                return_back = True
                                            else:
                                                if datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') > datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S') :
                                                    punch = datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') - datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
                                                    total_punch = (float(punch.total_seconds() / 60))
                                                    if total_punch > 15:
                                                        total_punch = float(punch.total_seconds() / 60) 
                                                    else:
                                                        total_punch = 0.0
                                                else:
                                                     total_punch = 0.0
                                                        
                                    punch_min1 = total_punch
                                    
                                    if not emp_dict.has_key(str(emp.id)):         
                                        query0 = "select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                 '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                 '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval \
                                                 '1 hours 30 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                                 )::timestamp + interval '10 minute'"
                                        
                                        cr.execute(query0)
                                        result0 = cr.fetchall()                                                
                                        for data in result0:
                                            if len(data)>0 and data[0] != None:
                                                if emp_dict.has_key(str(emp.id)):
                                                    emp_dict[str(emp.id)].update({'date':data[0]})
                                                else:
                                                    emp_dict[str(emp.id)] = {'date':data[0]} 
                                               
            #=========================================================================================================================================
             
                                    query8 = "select max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                             '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                             '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                              and to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp"
                                   
                                    cr.execute(query8)
                                    result8 = cr.fetchall()     
                                    if result8:
                                        if datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') > datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S'):
                                            punch = datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') - datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S')
                                            punch_min = float(punch.total_seconds() / 60)
                                            punch_hr = float(punch_min / 60)
                                            min = str(punch_hr)
                                            punch = min.split('.')
                                            a = int(punch[1])
                                            b = ((a * 60)/100)
                                            c = punch[0] + '.' + str(b)
                                            punch_hr1 = float(c)
                                            if punch_hr1 >= 5.45 :
                                                working = 'P'
                                            else:
                                                working = 'A'
                                                         
            #=========================================================================================================================================
                                    
                                    query090 = "select count(id) from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                    name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                    'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                    'YYYY-MM-DD HH24:MI:SS')::timestamp"
                                     
                                    cr.execute(query090)
                                    result090 = cr.fetchall()  
                                    cutt_off = timing['end_time'] 
                                    total_punch = 0.0
                                    for data090 in result090:
                                        if len(data090)>0 and data090[0] != None:
                                            query091 = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                                'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                            cr.execute(query091)
                                            result091 = cr.fetchall()  
                                            if int(data090[0]) % 2 <>  0:
                                                oldpunch = False   
                                                punch =  0.0     
                                                count = 0         
                                                for data091 in result091:  
                                                    if len(data091)>0 and data091[0] != None:
                                                        newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                        if count == 0:
                                                            oldpunch = datetime.strptime(cutt_off,'%Y-%m-%d %H:%M:%S')
                                                        if count <> 0 and count % 2 <> 0:
                                                            oldpunch = newpunch
                                                            count += 1
                                                            continue
                                                        if not oldpunch:
                                                            oldpunch = newpunch
                                                        else:
                                                            punch = newpunch - oldpunch
                                                            punch_min = float(punch.total_seconds() / 60)
                                                            total_punch = total_punch + punch_min
                                                            oldpunch = newpunch
                                                        count += 1
                                                                
                                            else:
                                                oldpunch = False   
                                                punch = 0.0              
                                                for data091 in result091:   
                                                    if len(data091)>0 and data091[0] != None:
                                                        newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                        if not oldpunch:
                                                            oldpunch = newpunch
                                                        else:
                                                            punch = newpunch - oldpunch
                                                            punch_min = float(punch.total_seconds() / 60)
                                                            total_punch = total_punch + punch_min
                                                            oldpunch = newpunch
                                                                        
                                    if total_punch > 5:
                                        punch_min = total_punch
                                    else:
                                        punch_min = 0.0
                                    
                                    punch =  punch_min
#                                    punch =  punch_min  + punch_min1          
                                    if  emp.ot_tick == True:      
                                         new_hrs = punch
                                    else:
                                         new_hrs = 0.0
                                     
                                    if emp_dict.has_key(str(emp.id)):
                                        if emp_dict[str(emp.id)].get('over_time',False):
                                            emp_dict[str(emp.id)]['over_time'] = emp_dict[str(emp.id)]['over_time'] + new_hrs
                                        else:
                                            emp_dict[str(emp.id)]['over_time'] = new_hrs
                                    else:
                                        if emp_dict.get(str(emp.id),False):
                                            emp_dict[str(emp.id)].update({'over_time': new_hrs})
                                        else:
                                            emp_dict[str(emp.id)] = {'over_time': new_hrs}
                                            
        #===================================================================================================================================
                                if return_back:
                                    continue
                                over_time = 0.0
                                penalty = 0.0
                                missing = 0.0
                                present = 0.0
                                missing = 0.0
                                new_over_time = 0.0
                                if emp_dict.get(str(emp.id),False):
                                    if emp_dict[str(emp.id)].get('over_time',False):
                                        over_time = emp_dict[str(emp.id)]['over_time']
                                        if over_time > 0:
                                            over_time =  round(over_time,2)
                                                
                                    if emp_dict[str(emp.id)].get('working',False):
                                        working = emp_dict[str(emp.id)].get('working')  
                                
                                    if emp_dict[str(emp.id)].get('present',False):
                                        present = emp_dict[str(emp.id)].get('present')   
                                    
                                    if sunday:    
                                        if emp_dict[str(emp.id)].get('sunday_time',False):
                                            over_time = emp_dict[str(emp.id)].get('sunday_time')
                                    
                                    tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                                    month = tm_tuple.tm_mon
                                    year = tm_tuple.tm_year        
                                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                                    
                                    if working == 'A':
                                        penalty = missing = over_time = 0.0
                                    
                                    over_time = over_time
                                    
                                    try:
                                        cr.execute("delete from attendance_timing where name='"+str(each.name)+"' and employee_id = '"+str(emp.id)+"' and method='Auto'")
                                        
                                        created_id = self.create(cr, uid, {'employee_id':emp.id,'name':each.name, 'working':working,'over_time':round(over_time,2),
                                                              'outside_time':0.0,'penalty':penalty,'sunday':sunday,'missing':missing,'present':present,
                                                              'month':str(month),'year_id':year_id and year_id[0] or False,'method':'Auto'})
                                        
                                         
                                        print "=========================NEW INDIVISIBLE WORKING RECORD IS CREATED==========================",created_id
                                    except:
                                        pass
                        else:
                            raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                else:
                    if each.name and each.end_date and each.employee_id:
                        count = 0
                        shift_data = []
                        start_date = datetime.strptime(each.name,'%Y-%m-%d')
                        end_date = datetime.strptime(each.end_date,'%Y-%m-%d')
                        end_tm_tuple = datetime.strptime(each.end_date,'%Y-%m-%d').timetuple()
                        while (start_date <= end_date):
                            emp_list=[]
                            cr.execute("select employee_id from hr_attendance  where day='"+str(start_date)+"' and employee_id in "+str(emp_list_ids)+" group by employee_id having count(id) % 2 = 0")
                            temp = cr.fetchall()
                            for val in temp:
                                emp_list.append(val[0])
                            emp_ids = emp_obj.browse(cr, uid, emp_list)
                            date1 = start_date.strftime('%Y-%m-%d')
                            tm_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()
                            if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                                break
                            if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                                break
                            for emp in emp_ids:
                                count  += 1
                                emp_dict =  {}
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',start_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',start_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        sunday = return_back = False
                                        timing = self.pool.get('wiz.attendance').calculate_time(cr, uid, ids, date1, line.from_time, line.to_time)
                                        
                                        holiday_ids1 = holi_obj.search(cr, uid, [('leave_date','=',start_date),('week','<>','Sunday')])
                                        if holiday_ids1:
                                            sunday = True
                                            sunday_case = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                        name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                            cr.execute(sunday_case)
                                            sunday_case_result = cr.fetchall()
                                            sun_oldpunch = False   
                                            sun_punch =  0.0     
                                            sun_count = 0      
                                            sun_mid = False  
                                            sun_total_punch = 0.0
                                            new_hrs = 0.0
                                            lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                            slunch = lunch + timedelta(hours=4)
                                            elunch = lunch + timedelta(hours=4,minutes=30)
                                            flunch = lunch + timedelta(hours=4,minutes=57)
                                            for case in sunday_case_result: 
                                                if len(case)>0 and case[0] != None:
                                                    sun_newpunch = datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S')
                                                    if sun_count == 0:
                                                        if datetime.strptime(case[0],'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                            sun_newpunch = datetime.strptime(str(case[0]),"%Y-%m-%d %H:%M:%S")
#                                                            sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        else:
                                                            new_time = case[0]
                                                        if sun_newpunch > slunch and sun_newpunch < elunch:
                                                            sun_oldpunch = elunch
                                                        else:
                                                            sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                    elif sun_count <> 0 and sun_count % 2 <> 0:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        
                                                        sun_punch = sun_newpunch - sun_oldpunch
                                                        sun_punch_min = float(sun_punch.total_seconds() / 60)
                                                        sun_total_punch = sun_total_punch + sun_punch_min
                                                        sun_oldpunch = sun_newpunch
                                                        
                                                        sun_count += 1
                                                    
                                                    else:
                                                        if sun_newpunch > slunch and sun_newpunch < flunch:
                                                            sun_newpunch = slunch
                                                        elif sun_newpunch > flunch:
                                                            sun_newpunch = sun_newpunch
                                                            sun_mid = True
                                                        sun_oldpunch = sun_newpunch
                                                        sun_count += 1
                                                                
                                            if sun_mid:
                                                sun_total_punch = sun_total_punch - line.lunch_time
                                                    
                                            sun_punch_min = sun_total_punch
                                            new_hrs = sun_punch_min
                                            if emp_dict.get(str(emp.id),False):
                                                emp_dict[str(emp.id)].update({'sunday_time': new_hrs,'working':'POH'})
                                            else:
                                                emp_dict[str(emp.id)] = {'sunday_time': new_hrs,'working':'POH'}
                                            
                #=================================================================================================================================
                                        else:
                                            after_shift = "select min(name + interval '5 hours 30 minute') from hr_attendance where name + interval '5 hours 30 minute' > to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and name + interval '5 hours 30 minute' < to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and employee_id = '"+str(emp.id)+"'"
                                            cr.execute(after_shift)
                                            after_shift_result = cr.fetchall()   
                                            for data in after_shift_result:   
                                                if len(data)>0 and data[0] != None:
                                                    if datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S') < datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S'):
                                                        return_back = True
                                                    else:
                                                        if datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') > datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S') :
                                                            punch = datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') - datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
                                                            total_punch = (float(punch.total_seconds() / 60))
                                                            if total_punch > 15:
                                                                total_punch = float(punch.total_seconds() / 60) 
                                                            else:
                                                                total_punch = 0.0
                                                        else:
                                                             total_punch = 0.0
                                                                
                                            punch_min1 = total_punch
                                                        
                                            
                                            if not emp_dict.has_key(str(emp.id)):         
                                                query0 = "select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                         '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval \
                                                         '1 hours 30 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                                         )::timestamp + interval '10 minute'"
                                                
                                                cr.execute(query0)
                                                result0 = cr.fetchall()                                                
                                                for data in result0:
                                                    if len(data)>0 and data[0] != None:
                                                        if emp_dict.has_key(str(emp.id)):
                                                            emp_dict[str(emp.id)].update({'date':data[0]})
                                                        else:
                                                            emp_dict[str(emp.id)] = {'date':data[0]} 
                                                       
                                                        
                    #=========================================================================================================================================
            
                     
                                            query8 = "select max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = \
                                                     '"+str(emp.id)+"' and name + interval '5 hours 30 minute' between to_timestamp( \
                                                     '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                                      and to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp"
                                           
                                            
                                            cr.execute(query8)
                                            result8 = cr.fetchall()  
                                            if result8:
                                                if datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') > datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S'):
                                                    punch = datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') - datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S')
                                                    punch_min = float(punch.total_seconds() / 60)
                                                    punch_hr = float(punch_min / 60)
                                                    min = str(punch_hr)
                                                    punch = min.split('.')
                                                    a = int(punch[1])
                                                    b = ((a * 60)/100)
                                                    c = punch[0] + '.' + str(b)
                                                    punch_hr1 = float(c)
                                                    if punch_hr1 >= 5.45 :
                                                      working = 'P'
                                                    else:
                                                       working = 'A'
                                       
                    #=========================================================================================================================================
                                            
                                            query090 = "select count(id) from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                            name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp"
                                             
                                            cr.execute(query090)
                                            result090 = cr.fetchall()  
                                            cutt_off = timing['end_time'] 
                                            total_punch = 0.0
                                            for data090 in result090:  
                                                
                                                if len(data090)>0 and data090[0] != None:
                                                    query091 = "select name + interval '5 hours 30 minute' from hr_attendance where employee_id =  '"+str(emp.id)+"' and \
                                                        name + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                                        'YYYY-MM-DD HH24:MI:SS')::timestamp order by name + interval '5 hours 30 minute'"
                                                    cr.execute(query091)
                                                    result091 = cr.fetchall()  
                                                    if int(data090[0]) % 2 <>  0:
                                                        oldpunch = False   
                                                        punch =  0.0     
                                                        count = 0         
                                                        for data091 in result091:  
                                                            if len(data091)>0 and data091[0] != None:
                                                                newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                                if count == 0:
                                                                    oldpunch = datetime.strptime(cutt_off,'%Y-%m-%d %H:%M:%S')
                                                                if count <> 0 and count % 2 <> 0:
                                                                    oldpunch = newpunch
                                                                    count += 1
                                                                    continue
                                                                if not oldpunch:
                                                                    oldpunch = newpunch
                                                                else:
                                                                    punch = newpunch - oldpunch
                                                                    punch_min = float(punch.total_seconds() / 60)
                                                                    total_punch = total_punch + punch_min
                                                                    oldpunch = newpunch
                                                                count += 1
                                                                        
                                                    else:
                                                        oldpunch = False   
                                                        punch = 0.0              
                                                        for data091 in result091:   
                                                            if len(data091)>0 and data091[0] != None:
                                                                newpunch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S')
                                                                if not oldpunch:
                                                                    oldpunch = newpunch
                                                                else:
                                                                    punch = newpunch - oldpunch
                                                                    punch_min = float(punch.total_seconds() / 60)
                                                                    total_punch = total_punch + punch_min
                                                                    oldpunch = newpunch
                                                                                
                                            if total_punch > 5:
                                                punch_min = total_punch
                                            else:
                                                punch_min = 0.0
                                            
                                            punch =  punch_min
#                                            punch =  punch_min  + punch_min1    
                                            if  emp.ot_tick == True:      
                                                 new_hrs = punch
                                            else:
                                                 new_hrs = 0.0
                                                        
                                            if emp_dict.has_key(str(emp.id)):
                                                if emp_dict[str(emp.id)].get('over_time',False):
                                                    emp_dict[str(emp.id)]['over_time'] = emp_dict[str(emp.id)]['over_time'] + new_hrs
                                                else:
                                                    emp_dict[str(emp.id)]['over_time'] = new_hrs
                                            else:
                                                if emp_dict.get(str(emp.id),False):
                                                    emp_dict[str(emp.id)].update({'over_time': new_hrs})
                                                else:
                                                    emp_dict[str(emp.id)] = {'over_time': new_hrs}
                                                    
                #===================================================================================================================================
                                        if return_back:
                                            continue
                                        over_time = 0.0
                                        penalty = 0.0
                                        missing = 0.0
                                        present = 0.0
                                        missing = 0.0
                                        new_over_time = 0.0
                                        if emp_dict.get(str(emp.id),False):
                                            if emp_dict[str(emp.id)].get('over_time',False):
                                                over_time = emp_dict[str(emp.id)]['over_time']
                                                if over_time > 0:
                                                    over_time =  round(over_time,2)
                                                        
                                            if emp_dict[str(emp.id)].get('working',False):
                                                working = emp_dict[str(emp.id)].get('working')  
                                        
                                            if emp_dict[str(emp.id)].get('present',False):
                                                present = emp_dict[str(emp.id)].get('present')   
                                            
                                            if sunday:    
                                                if emp_dict[str(emp.id)].get('sunday_time',False):
                                                    over_time = emp_dict[str(emp.id)].get('sunday_time')
                                            
                                            tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                                            month = tm_tuple.tm_mon
                                            year = tm_tuple.tm_year        
                                            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                                              
                                            if working == 'A':
                                                penalty = missing = over_time = 0.0
                                                
                                            over_time = over_time
                                            try:
                                                cr.execute("delete from attendance_timing where name='"+str(start_date)+"' and employee_id = '"+str(emp.id)+"' and method='Auto'")
                                                
                                                created_id = self.create(cr, uid, {'employee_id':emp.id,'name':start_date, 'working':working,'over_time':round(over_time,2),
                                                                      'outside_time':0.0,'penalty':penalty,'sunday':sunday,'missing':missing,'present':present,
                                                                      'month':str(month),'year_id':year_id and year_id[0] or False,'method':'Auto'})
                                                
                                                 
                                                print "=========================NEW INDIVISIBLE WORKING RECORD IS CREATED=========================",created_id
                                            except:
                                                pass
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                            start_date += timedelta(days=1)
        return True
    
    def _calculate_month_year(self, cr, uid, ids, name, arg, context=None):
        res = {}
        
        for each in self.browse(cr, uid, ids):
            res[each.id] = {
                            'month':1,
                            'year_id':False,
                            }
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            year = tm_tuple.tm_year        
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)]) 
            res[each.id]['month'] = month
            res[each.id]['year_id'] = year_id and year_id[0] or False
        return res
    
    
    _columns = {
                'name':fields.date('Punch Date',required=True),
                'creation_date':fields.date('Create Date', readonly=True),
                'employee_id':fields.many2one('hr.employee','Employee',required=True),
                'department_id':fields.related('employee_id','department_id',relation='hr.department',string='Department',type='many2one',readonly=True),
                'working':fields.selection([('A','A'),('P','P'),('POH','POH'),('POW','POW')],'Working Day'),
                'over_time':fields.float('Over Time(Min)'),
                'outside_time':fields.float('Outside Work'),
                'penalty':fields.float('Penalty'),
                'note':fields.char('Note'),
                'sunday':fields.boolean('Sunday'),
                'missing':fields.float('Missing'),
                'present':fields.float('working'),
                'month':fields.function(_calculate_month_year,method=True,store=True,type="integer",string="Month",multi='calc'),
                'year_id':fields.function(_calculate_month_year,method=True,store=True,relation="holiday.year",type="many2one",string="Year",multi='calc'),
                
#                'month':fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),
#                ('8','August'),('9','September'),('10','October'),('11','November'),('12','December'),],'Month',readonly=True),
#                'year_id':fields.many2one('holiday.year','Year',readonly=True),
#                'payment':fields.function(_calculate_payment,method=True,string="Payment",type="float"),
                'method':fields.selection([('Auto','Auto'),('Manual','Manual')],'Method'),
                'in_time': fields.datetime('IN Time'),
                'out_time': fields.datetime('OUT Time'),
                'state':fields.selection([('Draft','Draft'),('Editable','Editable')],'Status',readonly=True),
                'status':fields.selection([('A_OK','OK'),('B_Reduced','Reduced')],'Reduce state',readonly=True),
                'dept_status':fields.selection([('OK','OK'),('Dept_Absent','Dept. Absent')],'Dept. state',readonly=True),
                'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),
                'user_id':fields.many2one('res.users','Created By',readonly=True),
                'reason':fields.char('Reason'),
                'company_id':fields.related('employee_id','resource_id','company_id',relation='res.company',string='Company Name',type='many2one',store=True,method=True),
                'religion_id':fields.related('employee_id','religion',type="selection",selection=[('hindu', 'Hindu'),('muslim', 'Muslim'),('sikh', 'Sikh'),('isai', 'Isai'),('other', 'Other')],string='Religion', select=True,store=False),
                'year':fields.selection([('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),
                                         ('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),
                                         ('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),
                                         ('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),
                                         ('2030','2030'),('2031','2031'),('2032','2032'),('2033','2033'),
                                         ('2034','2034'),('2035','2035'),],'YEAR'),
                'active':fields.boolean('Active'),
                }
    
    _sql_constraints = [('unique_attendance','unique(employee_id,name,method)','Duplicate entries are not allowed')]
    
    _defaults = {
                 'method':'Manual',
                 'state':'Draft',
                 'creation_date':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                 'user_id': lambda obj, cr, uid, context: uid,
                 'working':'A',
                 'year':time.strftime('%Y'),
                 'active':True
                 }
    
    def write(self, cr, uid, ids, vals, context=None):
        vals['method'] = 'Manual'
        vals['state'] = 'Editable'
        vals['status'] = 'A_OK'
        vals['dept_status'] = 'OK'
        res = super(attendance_timing, self).write(cr, uid, ids, vals, context=context)
        return res
    
    def create(self, cr, uid, vals, context=None):
        if 'working' in vals and vals['working'] == 'POH':
            vals['dept_status'] = 'OK'
        if 'working' in vals and vals['working'] == 'POW':
            vals['dept_status'] = 'OK'
        if 'name' in vals and vals['name']:
            if 'method' in vals and vals['method'] == 'Manual':
                vals['status'] = 'A_OK'
                vals['dept_status'] = 'OK'
                att_id = self.search(cr, uid, [('name','=',vals['name']),('employee_id','=',vals['employee_id'])])
                if att_id:
                    self.unlink(cr, uid, att_id, context=context)
                    
        res_id = super(attendance_timing, self).create(cr, uid, vals, context=context)
        return res_id

    def unlink(self, cr, uid, ids, context=None):
        order = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for line in order:
            if line['state'] in ['Draft','Editable']:
                unlink_ids.append(line['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('You cannot delete editable Punch Card.'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
    
    def calculate_work_time(self, cr, uid, ids, context=None):
        holi_obj = self.pool.get('holiday.list.lines')
        shift_obj = self.pool.get('hr.shift.line')
        
        emp_dict =  {}
        for each in self.browse(cr, uid, ids):
            if each.name and each.in_time:
                intime = datetime.strptime(str(each.in_time),'%Y-%m-%d %H:%M:%S')
                intime = intime + timedelta(hours=5,minutes=30)
                in_time = intime.date()
                
                if datetime.strptime(str(each.name),'%Y-%m-%d').date() <> in_time:
                    raise osv.except_osv(_('Warning !'),_("Attendance Date and In Time Date is not equal."))
                    
                if datetime.strptime(str(each.in_time),'%Y-%m-%d %H:%M:%S') > datetime.strptime(str(each.out_time),'%Y-%m-%d %H:%M:%S'):
                    raise osv.except_osv(_('Warning !'),_("In Time cannot be greater than Out Time."))
                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', each.employee_id.id),('name', '<=',each.name)], limit=1, order='name DESC')
                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', each.employee_id.id),('name', '>',each.name)], limit=1, order='name ASC')
                
                if prev_shift_ids:
                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                elif next_shift_ids:
                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                else:
                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (each.employee_id.sinid)))
                if shift_data:
                    for line in shift_data.shift_id.shift_line:
                        sunday = return_back = False
                        timing = self.pool.get('wiz.attendance').calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                        allow_time = (datetime.strptime(str(timing['final_time']),"%Y-%m-%d %H:%M:%S") - datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")).total_seconds()/3600
                        
                        out_time = datetime.strptime(str(each.out_time),'%Y-%m-%d %H:%M:%S') + timedelta(hours=5,minutes=30)
                        out_time = out_time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        if datetime.strptime(str(out_time),"%Y-%m-%d %H:%M:%S") > datetime.strptime(str(timing['final_time']),"%Y-%m-%d %H:%M:%S"):
                            raise osv.except_osv(_('Warning !'),_("Allowed working time is %s hours, Create another attendance for time more than %s .") % (allow_time,timing['final_time']))
                        holiday_ids = holi_obj.search(cr, uid, [('leave_date','=',each.name),('week','=','Sunday')])
                        holiday_ids1 = holi_obj.search(cr, uid, [('leave_date','=',each.name),('week','<>','Sunday')])
                        if holiday_ids:
                            sunday = True
                            sunday_case = "select in_time + interval '5 hours 30 minute' , out_time + interval '5 hours 30 minute' from attendance_timing where id = '"+str(each.id)+"' and employee_id =  '"+str(each.employee_id.id)+"' and \
                                            in_time + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp"
                            cr.execute(sunday_case)
                            sunday_case_result = cr.fetchone()
                            if sunday_case_result:
                                sunday_case_result = list(sunday_case_result)
                                sun_oldpunch = False   
                                sun_punch =  0.0     
                                sun_count = 0      
                                sun_mid = False  
                                sun_total_punch = 0.0
                                new_hrs = 0.0
                                lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                slunch = lunch + timedelta(hours=4)
                                elunch = lunch + timedelta(hours=4,minutes=30)
                                flunch = lunch + timedelta(hours=4,minutes=57)
                                for case in sunday_case_result: 
                                    if len(case)>0 and case != None:
                                        sun_newpunch = datetime.strptime(case,'%Y-%m-%d %H:%M:%S')
                                        if sun_count == 0:
                                            if datetime.strptime(case,'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                sun_newpunch = datetime.strptime(str(case),"%Y-%m-%d %H:%M:%S")
#                                                sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                            if sun_newpunch > slunch and sun_newpunch < elunch:
                                                sun_oldpunch = elunch
                                            else:
                                                sun_oldpunch = sun_newpunch
                                            sun_count += 1
                                        elif sun_count <> 0 and sun_count % 2 <> 0:
                                            if sun_newpunch > slunch and sun_newpunch < flunch:
                                                sun_newpunch = slunch
                                            elif sun_newpunch > flunch:
                                                sun_newpunch = sun_newpunch
                                                sun_mid = True
                                            sun_punch = sun_newpunch - sun_oldpunch
                                            sun_punch_min = float(sun_punch.total_seconds() / 60)
                                            sun_total_punch = sun_total_punch + sun_punch_min
                                            sun_oldpunch = sun_newpunch
                                            
                                            sun_count += 1
                                        
                                        else:
                                            if sun_newpunch > slunch and sun_newpunch < flunch:
                                                sun_newpunch = slunch
                                            elif sun_newpunch > flunch:
                                                sun_newpunch = sun_newpunch
                                                sun_mid = True
                                            sun_oldpunch = sun_newpunch
                                            sun_count += 1
                                                    
                                if sun_mid:
                                    sun_total_punch = sun_total_punch - line.lunch_time
                                        
                                sun_punch_min = sun_total_punch
                                new_hrs = sun_punch_min
                                if emp_dict.get(str(each.employee_id.id),False):
                                    emp_dict[str(each.employee_id.id)].update({'sunday_time': new_hrs,'working':'POW'})
                                else:
                                    emp_dict[str(each.employee_id.id)] = {'sunday_time': new_hrs,'working':'POW'}

                        elif holiday_ids1:
                            sunday = True
                            sunday_case = "select in_time + interval '5 hours 30 minute' , out_time + interval '5 hours 30 minute' from attendance_timing where id = '"+str(each.id)+"' and employee_id =  '"+str(each.employee_id.id)+"' and \
                                            in_time + interval '5 hours 30 minute' between to_timestamp('"+str(timing['start_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and to_timestamp('"+str(timing['final_time'])+"',\
                                            'YYYY-MM-DD HH24:MI:SS')::timestamp"
                            cr.execute(sunday_case)
                            sunday_case_result = cr.fetchone()
                            if sunday_case_result:
                                sunday_case_result = list(sunday_case_result)
                                sun_oldpunch = False   
                                sun_punch =  0.0     
                                sun_count = 0      
                                sun_mid = False  
                                sun_total_punch = 0.0
                                new_hrs = 0.0
                                lunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                slunch = lunch + timedelta(hours=4)
                                elunch = lunch + timedelta(hours=4,minutes=30)
                                flunch = lunch + timedelta(hours=4,minutes=57)
                                for case in sunday_case_result: 
                                    if len(case)>0 and case != None:
                                        sun_newpunch = datetime.strptime(case,'%Y-%m-%d %H:%M:%S')
                                        if sun_count == 0:
                                            if datetime.strptime(case,'%Y-%m-%d %H:%M:%S') < datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S'):
                                                sun_newpunch = datetime.strptime(str(case),"%Y-%m-%d %H:%M:%S")
#                                                sun_newpunch = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                            if sun_newpunch > slunch and sun_newpunch < elunch:
                                                sun_oldpunch = elunch
                                            else:
                                                sun_oldpunch = sun_newpunch
                                            sun_count += 1
                                        elif sun_count <> 0 and sun_count % 2 <> 0:
                                            if sun_newpunch > slunch and sun_newpunch < flunch:
                                                sun_newpunch = slunch
                                            elif sun_newpunch > flunch:
                                                sun_newpunch = sun_newpunch
                                                sun_mid = True
                                            sun_punch = sun_newpunch - sun_oldpunch
                                            sun_punch_min = float(sun_punch.total_seconds() / 60)
                                            sun_total_punch = sun_total_punch + sun_punch_min
                                            sun_oldpunch = sun_newpunch
                                            
                                            sun_count += 1
                                        
                                        else:
                                            if sun_newpunch > slunch and sun_newpunch < flunch:
                                                sun_newpunch = slunch
                                            elif sun_newpunch > flunch:
                                                sun_newpunch = sun_newpunch
                                                sun_mid = True
                                            sun_oldpunch = sun_newpunch
                                            sun_count += 1
                                                    
                                if sun_mid:
                                    sun_total_punch = sun_total_punch - line.lunch_time
                                        
                                sun_punch_min = sun_total_punch
                                new_hrs = sun_punch_min
                                if emp_dict.get(str(each.employee_id.id),False):
                                    emp_dict[str(each.employee_id.id)].update({'sunday_time': new_hrs,'working':'POH'})
                                else:
                                    emp_dict[str(each.employee_id.id)] = {'sunday_time': new_hrs,'working':'POH'}
                                
#=================================================================================================================================
                        else:   
                            after_shift = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and " \
                            "in_time + interval '5 hours 30 minute' > to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' and " \
                            "out_time + interval '5 hours 30 minute' < to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp " \
                            "and employee_id = '"+str(each.employee_id.id)+"'"
                            cr.execute(after_shift)
                            after_shift_result = cr.fetchall()   
                            for data in after_shift_result:   
                                if len(data)>0 and data[0] != None:
                                    if datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S') < datetime.strptime(str(data[0]),'%Y-%m-%d %H:%M:%S'):
                                        return_back = True
                                    else:
                                        if datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') > datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S') :
                                            punch = datetime.strptime(str(timing['start_time']),'%Y-%m-%d %H:%M:%S') - datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S')
                                            total_punch = (float(punch.total_seconds() / 60))
                                            if total_punch > 15:
                                                total_punch = float(punch.total_seconds() / 60) 
                                            else:
                                                total_punch = 0.0
                                        else:
                                             total_punch = 0.0
                                                    
                            punch_min1 = total_punch
##=========================================================================================================================================
                                                    
                            if not emp_dict.has_key(str(each.employee_id.id)):  
                                query0 = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                         '"+str(each.employee_id.id)+"' and in_time + interval '5 hours 30 minute' between to_timestamp( \
                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval \
                                         '1 hours 30 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                         )::timestamp + interval '10 minute'"
                                
                                cr.execute(query0)
                                result0 = cr.fetchall()                                                
                                for data in result0:
                                    if len(data)>0 and data[0] != None:
                                        if emp_dict.has_key(str(each.employee_id.id)):
                                            emp_dict[str(each.employee_id.id)].update({'date':data[0]})
                                        else:
                                            emp_dict[str(each.employee_id.id)] = {'date':data[0]} 
    #=========================================================================================================================================                                    
                                        
                            if not emp_dict.has_key(str(each.employee_id.id)): 
                                query1 = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                         '"+str(each.employee_id.id)+"' and in_time + interval '5 hours 30 minute' between to_timestamp( \
                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                         '11 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                         )::timestamp + interval '15 minute'"
                                
                                cr.execute(query1)
                                result1 = cr.fetchall()                                                
                                for data in result1:
                                    if len(data)>0 and data[0] != None:
                                        if emp_dict.has_key(str(each.employee_id.id)):
                                            emp_dict[str(each.employee_id.id)].update({'date':data[0]})
                                        else:
                                            emp_dict[str(each.employee_id.id)] = {'date':data[0]} 
    ##=========================================================================================================================================
    #                       
                            if not emp_dict.has_key(str(each.employee_id.id)):   
                                query2 = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                         '"+str(each.employee_id.id)+"' and in_time + interval '5 hours 30 minute' between to_timestamp( \
                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                         '16 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                         )::timestamp + interval '35 minute'"
                                
                                                        
                                cr.execute(query2)
                                result2 = cr.fetchall()                                                  
                                for data in result2:
                                    if len(data)>0 and data[0] != None:
                                        if emp_dict.has_key(str(each.employee_id.id)):
                                            emp_dict[str(each.employee_id.id)].update({'date':data[0]})
                                        else:
                                            emp_dict[str(each.employee_id.id)] = {'date':data[0]} 
    ##=========================================================================================================================================
    #
                            if not emp_dict.has_key(str(each.employee_id.id)):  
                                query3 = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                         '"+str(each.employee_id.id)+"' and in_time + interval '5 hours 30 minute' between to_timestamp( \
                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                         '36 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                         )::timestamp + interval '1 hours 5 minute'"
                                
                                                      
                                cr.execute(query3)
                                result3 = cr.fetchall()                                                  
                                for data in result3:
                                    if len(data)>0 and data[0] != None:
                                        if emp_dict.has_key(str(each.employee_id.id)):
                                            emp_dict[str(each.employee_id.id)].update({'date':data[0]})
                                        else:
                                            emp_dict[str(each.employee_id.id)] = {'date':data[0]}              
    
    ##=========================================================================================================================================
    #
                            if not emp_dict.has_key(str(each.employee_id.id)):   
                                query4 = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                         '"+str(each.employee_id.id)+"' and in_time + interval '5 hours 30 minute' between to_timestamp( \
                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                         '1 hours 6 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                         )::timestamp + interval '1 hours 32 minute'"
                                
                                                        
                                cr.execute(query4)
                                result4 = cr.fetchall()                                                  
                                for data in result4:
                                    if len(data)>0 and data[0] != None:
                                        if emp_dict.has_key(str(each.employee_id.id)):
                                            emp_dict[str(each.employee_id.id)].update({'date':data[0]})
                                        else:
                                            emp_dict[str(each.employee_id.id)] = {'date':data[0]}
    #=========================================================================================================================================
    
                            if not emp_dict.has_key(str(each.employee_id.id)): 
                                query41 = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                         '"+str(each.employee_id.id)+"' and in_time + interval '5 hours 30 minute' between to_timestamp( \
                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                         '1 hours 33 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                         )::timestamp + interval '2 hours 2 minute'"
                                
                                                
                                cr.execute(query41)
                                result41 = cr.fetchall()                                                  
                                for data in result41:
                                    if len(data)>0 and data[0] != None:
                                        if emp_dict.has_key(str(each.employee_id.id)):
                                            emp_dict[str(each.employee_id.id)].update({'date':data[0]})
                                        else:
                                            emp_dict[str(each.employee_id.id)] = {'date':data[0]}
    #=========================================================================================================================================
    
                            if not emp_dict.has_key(str(each.employee_id.id)): 
                                query42 = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                         '"+str(each.employee_id.id)+"' and in_time + interval '5 hours 30 minute' between to_timestamp( \
                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                         '2 hours 3 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                         )::timestamp + interval '2 hours 32 minute'"
                                
                                                        
                                cr.execute(query42)
                                result42 = cr.fetchall()                                                  
                                for data in result42:
                                    if len(data)>0 and data[0] != None:
                                        if emp_dict.has_key(str(each.employee_id.id)):
                                            emp_dict[str(each.employee_id.id)].update({'date':data[0]})
                                        else:
                                            emp_dict[str(each.employee_id.id)] = {'date':data[0]}
    #=========================================================================================================================================
    
    
                            if not emp_dict.has_key(str(each.employee_id.id)):
                                query43 = "select min(in_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                         '"+str(each.employee_id.id)+"' and in_time + interval '5 hours 30 minute' between to_timestamp( \
                                         '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp + interval \
                                         '2 hours 33 minute' and to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS' \
                                         )::timestamp + interval '3 hours 2 minute '"
                                
                                                        
                                cr.execute(query43)
                                result43 = cr.fetchall()                                                  
                                for data in result43:
                                    if len(data)>0 and data[0] != None:
                                        if emp_dict.has_key(str(each.employee_id.id)):
                                            emp_dict[str(each.employee_id.id)].update({'date':data[0]})
                                        else:
                                            emp_dict[str(each.employee_id.id)] = {'date':data[0]}
                                       
    #=========================================================================================================================================

     
                            query8 = "select max(out_time + interval '5 hours 30 minute') from attendance_timing where id = '"+str(each.id)+"' and employee_id = \
                                     '"+str(each.employee_id.id)+"' and out_time + interval '5 hours 30 minute' between to_timestamp( \
                                     '"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                      and to_timestamp('"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp"
                           
                            
                            cr.execute(query8)
                            result8 = cr.fetchall() 
                            if result8:
                                if datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') > datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S'):
                                   punch = datetime.strptime(result8[0][0],'%Y-%m-%d %H:%M:%S') - datetime.strptime(after_shift_result[0][0],'%Y-%m-%d %H:%M:%S')
                                   punch_min = float(punch.total_seconds() / 60)
                                   punch_hr = float(punch_min / 60)
                                   min = str(punch_hr)
                                   punch = min.split('.')
                                   a = int(punch[1])
                                   b = ((a * 60)/100)
                                   c = punch[0] + '.' + str(b)
                                   punch_hr1 = float(c)
                                   if punch_hr1 >= 5.45 :
                                      working = 'P'
                                   else:
                                       working = 'A'
                                       
    #=========================================================================================================================================
                            
                            total_punch = 0.0
                            query091 = "select out_time + interval '5 hours 30 minute' from attendance_timing where id = '"+str(each.id)+"' and employee_id =  '"+str(each.employee_id.id)+"' and \
                                out_time + interval '5 hours 30 minute' between to_timestamp('"+str(timing['end_time'])+"',\
                                'YYYY-MM-DD HH24:MI:SS')::timestamp and to_timestamp('"+str(timing['final_time'])+"',\
                                'YYYY-MM-DD HH24:MI:SS')::timestamp"
                            cr.execute(query091)
                            result091 = cr.fetchall()   
                            for data091 in result091:  
                                if len(data091)>0 and data091[0] != None:
                                    if datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S') > datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S'):
                                        punch = datetime.strptime(data091[0],'%Y-%m-%d %H:%M:%S') - datetime.strptime(str(timing['end_time']),'%Y-%m-%d %H:%M:%S')
                                        total_punch = float(punch.total_seconds() / 60)
                                        if total_punch > 10:
                                            total_punch = float(punch.total_seconds() / 60) 
                                        else:
                                            total_punch = 0.0
                                        
                            punch_min = total_punch
                            punch =  punch_min  + punch_min1   
                            new_hrs = punch
                                        
                            if emp_dict.has_key(str(each.employee_id.id)):
                                emp_dict[str(each.employee_id.id)].update({'over_time': new_hrs})
                            else:
                                emp_dict[str(each.employee_id.id)] = {'over_time': new_hrs}

#===================================================================================================================================
                        if return_back:
                            continue
#                        working = 'A'
                        over_time = 0.0
                        penalty = 0.0
                        missing = 0.0
                        present = 0.0
                        missing = 0.0
                        new_over_time = 0.0
                        if emp_dict.get(str(each.employee_id.id),False):
                            if emp_dict[str(each.employee_id.id)].get('over_time',False):
                                over_time = emp_dict[str(each.employee_id.id)]['over_time']
                                if over_time > 0:
                                    over_time =  round(over_time,2)
                                    
                            if emp_dict[str(each.employee_id.id)].get('penalty1',False):
                                penalty = emp_dict[str(each.employee_id.id)].get('penalty1')
                            if emp_dict[str(each.employee_id.id)].get('penalty2',False):
                                penalty = emp_dict[str(each.employee_id.id)].get('penalty2')
                            if emp_dict[str(each.employee_id.id)].get('penalty3',False):
                                penalty = emp_dict[str(each.employee_id.id)].get('penalty3')
                            if emp_dict[str(each.employee_id.id)].get('penalty4',False):
                                penalty = emp_dict[str(each.employee_id.id)].get('penalty4')
                            if emp_dict[str(each.employee_id.id)].get('penalty41',False):
                                penalty = emp_dict[str(each.employee_id.id)].get('penalty41')
                            if emp_dict[str(each.employee_id.id)].get('penalty42',False):
                                penalty = emp_dict[str(each.employee_id.id)].get('penalty42')
                            if emp_dict[str(each.employee_id.id)].get('penalty43',False):
                                penalty = emp_dict[str(each.employee_id.id)].get('penalty43')
                                
                            if emp_dict[str(each.employee_id.id)].get('working',False):
                                working = emp_dict[str(each.employee_id.id)].get('working') 
                              
                            if emp_dict[str(each.employee_id.id)].get('present',False):
                                present = emp_dict[str(each.employee_id.id)].get('present')   
                            
                            if sunday:
                                if emp_dict[str(each.employee_id.id)].get('sunday_time',False):
                                    over_time = emp_dict[str(each.employee_id.id)].get('sunday_time')
                            
                            tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                            month = tm_tuple.tm_mon
                            year = tm_tuple.tm_year        
                            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                            
                            if working == 'A':
                                penalty = missing = over_time = 0.0
                            
                            over_time = over_time
                            try:
                                
#                                cr.execute("select id from department_attendance_line where att_date='"+str(each.name)+"' and employee_id = '"+str(each.employee_id.id)+"' limit 1" )
#                                temp_state2 = cr.fetchall()
#                                state2 = 'Dept_Absent'
#                                for st2 in temp_state2:
#                                    if st2 and st2[0] != None:
#                                        state2 = 'OK'

                                cr.execute("delete from attendance_timing where name='"+str(each.name)+"' and employee_id = '"+str(each.employee_id.id)+"' and method='Auto'" )
                               
                                created_id = self.write(cr, uid, [each.id],{ 'working':working,'over_time':round(over_time,2),
                                                      'outside_time':0.0,'penalty':penalty,'sunday':sunday,'missing':missing,'present':present,
                                                      'month':str(month),'year_id':year_id and year_id[0] or False,'method':"Manual"}) 
                                print "=========================NEW INDIVISIBLE WORKING RECORD IS CREATED===========================",created_id
                            except:
                                pass
                        
        return True
    
    
class wiz_attendance(osv.osv_memory):
    _name = 'wiz.attendance'
    
    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False

    _columns = {
                'name':fields.date('Start Date'),
                'end_date':fields.date('End Date'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'department_id':fields.many2one('hr.department','Department'),
#                'month':fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),
#                ('8','August'),('9','September'),('10','October'),('11','November'),('12','December'),],'Month'),
#                'year_id':fields.many2one('holiday.year','Year'),
                'type':fields.selection([('Wood','Wood'),('Metal','Metal'),('Lohia','Lohia'),('Kashipur','Kashipur'),('Lodhipur','Lodhipur'),('Prabhat Market','Prabhat Market'),('Galshahid','Galshahid'),('Rajan','Rajan ENC'),('LB Unit-III','LB Unit-III')],'Working AT'),
                'company_id': fields.many2one('res.company',string="Company"),
                'user_id': fields.many2one('res.users',string="User"),
                'employment_type':fields.selection([('Employee','Employee'),('Labor','Labor'),('Trainee','Trainee')],'Employment Type'),
                'type':fields.selection([('Employee','Employee'),('Contractor','Contractor')],'Type'),
                'start_count':fields.integer("From"),
                'to_count':fields.integer("To")
                }
    
    _defaults = {
                 'company_id' : _get_company_id,
                 'user_id' : lambda obj, cr, uid, context: uid,
                 }
    
    def earned_leave(self, cr, uid, ids,context=None):
        count = []
        emp_obj = self.pool.get('hr.employee')
        hol_obj = self.pool.get('hr.holidays')
        punch_obj = self.pool.get('attendance.timing')
        hol_status_obj = self.pool.get('hr.holidays.status')
        earned_id = hol_status_obj.search(cr, uid, [('name','=','Earned Leaves')])
        rec = self.browse(cr, uid, ids)
        if rec.name and rec.end_date :
            from_date = datetime.strptime(rec.name,'%Y-%m-%d') 
            end_date = datetime.strptime(rec.end_date,'%Y-%m-%d')
            tm_tuple = datetime.strptime(rec.name,'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name', '=',year)])
            month_id = str(tm_tuple.tm_mon)
            if rec.employee_id and rec.department_id and rec.company_id and rec.employment_type:                
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('department_id', '=', rec.department_id.id),('active','=',True),('company_id','=',rec.company_id.id),('employment_type','=',rec.employment_type)])          
            
            elif rec.employee_id and rec.department_id and rec.company_id:                
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('department_id', '=', rec.department_id.id),('active','=',True),('company_id','=',rec.company_id.id)])
            
            elif rec.employee_id and rec.department_id and rec.employment_type:                
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('department_id', '=', rec.department_id.id),('active','=',True),('employment_type','=',rec.employment_type)])
            
            elif rec.employee_id and rec.employment_type and rec.company_id:                
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('employment_type','=',rec.employment_type),('active','=',True),('company_id','=',rec.company_id.id)])   
            
            elif rec.department_id and rec.employment_type and rec.company_id:                
                emp_ids = emp_obj.search(cr, uid, [('employment_type','=',rec.employment_type),('department_id', '=', rec.department_id.id),('active','=',True),('company_id','=',rec.company_id.id)])
            
            elif rec.employee_id and rec.company_id:
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('active','=',True),('company_id','=',rec.company_id.id)])
           
            elif rec.department_id and rec.company_id:
                emp_ids = emp_obj.search(cr, uid, [('department_id', '=', rec.department_id.id),('active','=',True),('company_id','=',rec.company_id.id)])
            
            elif rec.department_id and rec.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('department_id', '=', rec.department_id.id),('active','=',True),('employment_type','=',rec.employment_type)])
            
            elif rec.company_id and rec.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('employment_type','=',rec.employment_type),('active','=',True),('company_id','=',rec.company_id.id)])
            
            elif rec.employee_id and rec.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('active','=',True),('employment_type','=',rec.employment_type)])
            
            elif rec.company_id:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',rec.company_id.id)])
            elif rec.employee_id:
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('active','=',True)])
            elif rec.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('employment_type', '=', rec.employment_type),('active','=',True)])    
            elif rec.department_id:
                 emp_ids = emp_obj.search(cr, uid, [('department_id', '=', rec.department_id.id),('active','=',True)])
            else:
                emp_ids =  emp_obj.search(cr, uid, [('active','=',True)])
                 
                 
                 
                 
                 
                 
                 
            for val in emp_obj.browse(cr, uid, emp_ids):
                print"val ===============",val,val.sinid
                prev_earn = val.earn_leave
                doj = datetime.strptime(val.doj,'%Y-%m-%d')
                e_date = datetime.strptime(val.earn_date,'%Y-%m-%d')
                worked_days = (from_date - doj).days
                if e_date < end_date:
                    data = punch_obj.search(cr, uid, [('name','>',val.earn_date),('name','<=',end_date),('employee_id','=',val.id),('working','in',['P','POH','POW'])] ,order='name asc')
                    if len(data) >= 20  and len(data) < 40:
                        value_id = data[19]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn < 30:
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                    
                    elif len(data) >= 40  and len(data) < 60:
                        value_id = data[39]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 28:
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29:
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                                
                    elif len(data) >= 60  and len(data) < 80:
                        value_id = data[59]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 27 :
                                earn = rec.number_of_days + 3
                                hr_earn = prev_earn + 3
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 28:
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29:
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)                        

                    elif len(data) >= 80  and len(data) < 100:
                        value_id = data[79]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 26 :
                                earn = rec.number_of_days + 4
                                hr_earn = prev_earn + 4
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 27:
                                earn = rec.number_of_days + 3
                                hr_earn = prev_earn + 3
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 28:
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29:
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)                        

                    elif len(data) >= 100  and len(data) < 120:
                        value_id = data[99]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 25 :
                                earn = rec.number_of_days + 5
                                hr_earn = prev_earn + 5
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 26 :
                                earn = rec.number_of_days + 4
                                hr_earn = prev_earn + 4
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 27 :
                                earn = rec.number_of_days + 3
                                hr_earn = prev_earn + 3
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 28 :
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29 :
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)                        

                    elif len(data) >= 120  and len(data) < 140:
                        value_id = data[119]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 24 :
                                earn = rec.number_of_days + 6
                                hr_earn = prev_earn + 6
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 25 :
                                earn = rec.number_of_days + 5
                                hr_earn = prev_earn + 5
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 26 :
                                earn = rec.number_of_days + 4
                                hr_earn = prev_earn + 4
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 27 :
                                earn = rec.number_of_days + 3
                                hr_earn = prev_earn + 3
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 28 :
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29 :
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)                        

                    elif len(data) >= 140  and len(data) < 160:
                        value_id = data[139]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 23 :
                                earn = rec.number_of_days + 7
                                hr_earn = prev_earn + 7
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 24 :
                                earn = rec.number_of_days + 6
                                hr_earn = prev_earn + 6
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 25 :
                                earn = rec.number_of_days + 5
                                hr_earn = prev_earn + 5
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 26 :
                                earn = rec.number_of_days + 4
                                hr_earn = prev_earn + 4
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 27 :
                                earn = rec.number_of_days + 3
                                hr_earn = prev_earn + 3
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 28 :
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29 :
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)                        

                    elif len(data) >= 160  and len(data) < 180:
                        value_id = data[159]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 22 :
                                earn = rec.number_of_days + 8
                                hr_earn = prev_earn + 8
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 23 :
                                earn = rec.number_of_days + 7
                                hr_earn = prev_earn + 7
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 24 :
                                earn = rec.number_of_days + 6
                                hr_earn = prev_earn + 6
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 25 :
                                earn = rec.number_of_days + 5
                                hr_earn = prev_earn + 5
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 26 :
                                earn = rec.number_of_days + 4
                                hr_earn = prev_earn + 4
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 27 :
                                earn = rec.number_of_days + 3
                                hr_earn = prev_earn + 3
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 28 :
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29 :
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)                        

                    elif len(data) >= 180  and len(data) < 200:
                        value_id = data[179]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 21 :
                                earn = rec.number_of_days + 9
                                hr_earn = prev_earn + 9
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 22 :
                                earn = rec.number_of_days + 8
                                hr_earn = prev_earn + 8
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 23 :
                                earn = rec.number_of_days + 7
                                hr_earn = prev_earn + 7
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 24 :
                                earn = rec.number_of_days + 6
                                hr_earn = prev_earn + 6
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 25 :
                                earn = rec.number_of_days + 5
                                hr_earn = prev_earn + 5
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 26 :
                                earn = rec.number_of_days + 4
                                hr_earn = prev_earn + 4
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 27 :
                                earn = rec.number_of_days + 3
                                hr_earn = prev_earn + 3
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 28 :
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29 :
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)                        

                    elif len(data) >= 200  and len(data) < 220:
                        value_id = data[199]
                        earn_date = punch_obj.browse(cr, uid, value_id).name
                        hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                        if hol_id:
                            rec = hol_obj.browse(cr, uid, hol_id)
                            if  prev_earn <= 20 :
                                earn = rec.number_of_days + 10
                                hr_earn = prev_earn + 10
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 21 :
                                earn = rec.number_of_days + 9
                                hr_earn = prev_earn + 9
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 22 :
                                earn = rec.number_of_days + 8
                                hr_earn = prev_earn + 8
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 23 :
                                earn = rec.number_of_days + 7
                                hr_earn = prev_earn + 7
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 24 :
                                earn = rec.number_of_days + 6
                                hr_earn = prev_earn + 6
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 25 :
                                earn = rec.number_of_days + 5
                                hr_earn = prev_earn + 5
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 26 :
                                earn = rec.number_of_days + 4
                                hr_earn = prev_earn + 4
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 27 :
                                earn = rec.number_of_days + 3
                                hr_earn = prev_earn + 3
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 28 :
                                earn = rec.number_of_days + 2
                                hr_earn = prev_earn + 2
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)
                            elif  prev_earn == 29 :
                                earn = rec.number_of_days + 1
                                hr_earn = prev_earn + 1
                                hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':earn,'number_of_days':earn})
                                a=emp_obj.write(cr, uid, [val.id],{'earn_leave':hr_earn,'earn_date':earn_date,'history_earn_ids':[(0,False,{'name':earn_date,'prev_earn':prev_earn,'curr_earn':hr_earn,'user_id':uid,'employee_id':val.id,})]})
                                count.append(val.id)                        
                                                        
                else :
                    earn_left=val.earn_leave
                    if  earn_left > 0  :
                        emp_obj.write(cr, uid, [val.id],{'earn_leave':earn_left})
                    else:
                       hol_id = hol_obj.search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',val.id),('type','=','add'),('state','=','validate'),('holiday_status_id','=',earned_id[0])])
                       hol_obj.write(cr, uid, hol_id,{'number_of_days_temp':0 ,'number_of_days':0})
                       emp_obj.write(cr, uid, [val.id],{'earn_leave':0})

        else :
            raise osv.except_osv(_('Warning !'),_("Please enter the First Day of the Month in From Date and Last day of month in End Date Field only..!!!"))
        return True
    
    ####======================[[ Automatic Scheduler of Leave ]] =========================================   
    
    def automatic_leave_posting(self,cr,uid,ids,context=None):
        print "====== in leave Posting Scheduler ========="
#        print "=========== leave setting ========"
        month_day=[]
        holiday_list=[]      
        emp_obj = self.pool.get('hr.employee')
        hol_obj = self.pool.get('hr.holidays')
        punch_obj = self.pool.get('attendance.timing')
        hol_status_obj = self.pool.get('hr.holidays.status')
        hol_list_obj=self.pool.get('holiday.list')
        rec = self.browse(cr, uid, ids)
        
        if rec.name and rec.end_date :
            start_date=rec.name
            end_date=rec.end_date
            from_date = datetime.strptime(rec.name,'%Y-%m-%d') 
            till_date = datetime.strptime(rec.end_date,'%Y-%m-%d')
            from_month=from_date.strftime("%m")
            till_month=till_date.strftime("%m")
            from_year=from_date.strftime("%Y")
            till_year=till_date.strftime("%Y")
            if int(from_year)!=int(till_year):
                raise osv.except_osv(_('Warning !'),_("Please enter the Same Year In From Date and End Date "))
            if int(from_month)!=int(till_month):
                raise osv.except_osv(_('Warning !'),_("Please enter the Same Month In From Date and End Date "))          
            tm_tuple = datetime.strptime(rec.name,'%Y-%m-%d').timetuple()
            
            
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name', '=',year)])
            month_id = str(tm_tuple.tm_mon)
            sick_comp_date_month_id = self.pool.get('holiday.list').search(cr, uid, [('month','=',month_id),('year_id','=',year_id[0])])
            month_search_id=hol_list_obj.search(cr,uid,[('month','=',month_id),('year_id','=',year_id[0])])
            month_browse=hol_list_obj.browse(cr,uid,month_search_id)
            month_name=month_browse.id
            month_id_int=int(month_id)
            from_first_day=from_date.strftime("%d")
            till_last_day=till_date.strftime("%d")
            total_last_month_day = calendar.monthrange(int(year),int(month_id))[1]
            total_first_month_day = '0'+ str(calendar.monthrange(int(year),int(month_id))[0])
            if int(till_last_day)!=int(total_last_month_day) :
                raise osv.except_osv(_('Warning !'),_("Please enter the Last Date of the Month in End Date"))
            year_val = from_date.strftime("%Y")
            casual_val = 'Casual Leaves' + ' ' +str(year_val)
            sick_val = 'Sick Leaves' + ' ' +str(year_val) 
            
            if rec.employee_id and rec.department_id and rec.company_id and rec.employment_type:                
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('department_id', '=', rec.department_id.id),('active','=',True),('company_id','=',rec.company_id.id),('employment_type','=',rec.employment_type)])          
            
            elif rec.employee_id and rec.department_id and rec.company_id:                
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('department_id', '=', rec.department_id.id),('active','=',True),('company_id','=',rec.company_id.id)])
            
            elif rec.employee_id and rec.department_id and rec.employment_type:                
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('department_id', '=', rec.department_id.id),('active','=',True),('employment_type','=',rec.employment_type)])
            
            elif rec.employee_id and rec.employment_type and rec.company_id:                
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('employment_type','=',rec.employment_type),('active','=',True),('company_id','=',rec.company_id.id)])   
            
            elif rec.department_id and rec.employment_type and rec.company_id:                
                emp_ids = emp_obj.search(cr, uid, [('employment_type','=',rec.employment_type),('department_id', '=', rec.department_id.id),('active','=',True),('company_id','=',rec.company_id.id)])
            
            elif rec.employee_id and rec.company_id:
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('active','=',True),('company_id','=',rec.company_id.id)])
           
            elif rec.department_id and rec.company_id:
                emp_ids = emp_obj.search(cr, uid, [('department_id', '=', rec.department_id.id),('active','=',True),('company_id','=',rec.company_id.id)])
            
            elif rec.department_id and rec.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('department_id', '=', rec.department_id.id),('active','=',True),('employment_type','=',rec.employment_type)])
            
            elif rec.company_id and rec.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('employment_type','=',rec.employment_type),('active','=',True),('company_id','=',rec.company_id.id)])
            
            elif rec.employee_id and rec.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('active','=',True),('employment_type','=',rec.employment_type)])
            
            elif rec.company_id:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',rec.company_id.id)])
            elif rec.employee_id:
                emp_ids = emp_obj.search(cr, uid, [('id', '=', rec.employee_id.id),('active','=',True)])
            elif rec.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('employment_type', '=', rec.employment_type),('active','=',True)])    
            elif rec.department_id:
                 emp_ids = emp_obj.search(cr, uid, [('department_id', '=', rec.department_id.id),('active','=',True)])
            else:
                emp_ids =  emp_obj.search(cr, uid, [('active','=',True)])
                
                
            print ("len of emp_ids------------",len(emp_ids))    
            cr.execute(" select leave_date from holiday_list_lines as hll left join holiday_list as hl on hll.holiday_id =hl.id  where  hl.month='"+str(month_id)+"' and year_id='"+str(year_id[0])+"'  ") 
            holiday_list_line = cr.fetchall()
            if holiday_list_line :
                for hol_list in holiday_list_line:
                    holiday_list.append(hol_list[0])    
            for val in emp_ids:
                full_date_month=[] 
                cl_total=0
                sl_total=0
                sl_leave=0
                cl_leave=0
                earn_total=0 
                e_leave=0
                cl_left=0
                el_left=0
                sl_left=0
                wrk_day=0
                join_val=0
                emp_browse=emp_obj.browse(cr,uid,val)
                emp_sinid=emp_browse.sinid
                emp_doj = emp_browse.doj
 
                print "emp_doj=================",emp_doj,emp_sinid
                if emp_doj :
                    emp_join_month = datetime.strptime(emp_doj,'%Y-%m-%d').strftime("%m")
                    emp_join_month =int(emp_join_month)
                    emp_join_year =datetime.strptime(emp_doj,'%Y-%m-%d').strftime("%Y")
                    emp_join_year =int(emp_join_year)
                    leave_post_month =datetime.strptime(rec.name,'%Y-%m-%d').strftime("%m")
                    leave_post_month =int(leave_post_month)
                    leave_post_year = datetime.strptime(rec.name,'%Y-%m-%d').strftime("%Y")
                    leave_post_year = int(leave_post_year)
                    if leave_post_year == emp_join_year :
                        join_val = leave_post_month - emp_join_month
                        join_val = join_val + 1
                    #For Same month Joining In which we want to allocate leaves
                    if leave_post_month == emp_join_month and emp_join_year == leave_post_year:
        			   for month_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(emp_doj,'%Y-%m-%d'),until=datetime.strptime(end_date,'%Y-%m-%d')):
                        		month_date = datetime.strftime(month_date,"%Y-%m-%d")
                        		full_date_month.append(month_date)

                    #For others
                    else:
        			     for month_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(start_date,'%Y-%m-%d'),until=datetime.strptime(end_date,'%Y-%m-%d')):
                        		month_date = datetime.strftime(month_date,"%Y-%m-%d")
                        		full_date_month.append(month_date)	
                                                            
                    query =cr.execute("select hh.number_of_days_temp from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where "
                                            " employee_id = '"+str(val)+"' and hh.type = 'add' and hhs.name = '"+str(casual_val)+"'  and state = 'validate'  ")
                    casual_allocate = cr.fetchall()
                    if casual_allocate :    
                        if casual_allocate[0][0] != None:
                            for temp in casual_allocate:
                                cl_total = temp[0]
                    query=cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where "
                                            " employee_id = '"+str(val)+"' and hh.type = 'remove' and hhs.name = '"+str(casual_val)+"'  and state = 'validate'  ")
                    casual_leave = cr.fetchall()
                    if casual_leave :
                        if casual_leave[0][0] != None:
                            for temp in casual_leave:
                                cl_leave = temp[0]
                    if cl_total > cl_leave :
                         cl_left= cl_total - cl_leave
                    query = cr.execute("select hh.number_of_days_temp from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where "
                                            " employee_id = '"+str(val)+"' and hh.type = 'add' and hhs.name = 'Earned Leaves'  and state = 'validate'  ")
                    earned_allocate = cr.fetchall()
                    if earned_allocate :
                        if earned_allocate[0][0] != None:
                            for temp in earned_allocate:
                                earn_total = temp[0]
                    query = cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where "
                                            " employee_id = '"+str(val)+"' and hh.type = 'remove' and hhs.name = 'Earned Leaves'  and state = 'validate'  ")
                    earn_leave = cr.fetchall()
                    if earn_leave:
                        if earn_leave[0][0] != None:
                            for temp in earn_leave:
                                e_leave = temp[0]                                                         
                    if earn_total >= e_leave :
                         el_left= earn_total - e_leave
                    present_day=[]
                    q2 = cr.execute("select name from attendance_timing where employee_id='"+str(val)+"' and month='"+str(month_id)+"' and year_id='"+str(year_id[0])+"'  ")
                    punch_day = cr.fetchall()
                    if len(punch_day) < 1  :
                        continue
                    if punch_day :
                        for p_day in punch_day:
                            present_day.append(p_day[0])
                    if len(holiday_list) > 0 and total_last_month_day:
                        wrk_day = total_last_month_day - len(holiday_list)
#                    print "wrk_day=============",wrk_day,punch_day 
                    if wrk_day :
                        if wrk_day > len(punch_day) :
                            comp_work_day=''
                            comp_work_day = present_day + holiday_list
                            actual_left_day = list(set(full_date_month)-set(comp_work_day))
                            sick_date_list = []
                            comp_date_list = []
                            factory_work_list=[]
#                            print "actual_left_day=============",actual_left_day
                            if actual_left_day:
                                query_sick = cr.execute("select hol.from_date,hol.date_to from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(val)+"' and  hol1.name = '"+str(sick_val)+"' and state='validate' and month = "+str(sick_comp_date_month_id[0])+" and type='remove' ")
                                sick_date = cr.fetchall()
                                query_comp = cr.execute("select hol.from_date,hol.date_to from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(val)+"' and  hol1.name = 'Compensatory Days' and state='validate' and month = "+str(sick_comp_date_month_id[0])+" and type='remove' ")
                                comp_date = cr.fetchall()
                                query_factory = cr.execute("select hol.from_date,hol.date_to from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(val)+"' and  hol1.name = 'Factory Work' and state='validate' and month = "+str(month_name)+" and type='remove' ")
                                factory_date = cr.fetchall()
                                if sick_date :
                                    for temp in actual_left_day:    
                                        for val1 in sick_date :
                                            for sick_leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                                sick_leave_date = datetime.strftime(sick_leave_date,"%Y-%m-%d")
                                                if sick_leave_date == temp :
                                                    sick_date_list.append(sick_leave_date)
                                    actual_left_day = list(set(actual_left_day)-set(sick_date_list))
                                if comp_date :
                                     for temp1 in actual_left_day:    
                                        for val2 in comp_date :
                                            for comp_leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val2[0],'%Y-%m-%d'),until=datetime.strptime(val2[1],'%Y-%m-%d %H:%M:%S')):
                                                comp_leave_date = datetime.strftime(comp_leave_date,"%Y-%m-%d")
                                                if comp_leave_date == temp1 :
                                                    comp_date_list.append(comp_leave_date)
                                     actual_left_day = list(set(actual_left_day)-set(comp_date_list))
                                     
                                if  factory_date : 
                                    for temp2 in  actual_left_day :
                                        for val3 in factory_date :
                                             for fac_work_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val3[0],'%Y-%m-%d'),until=datetime.strptime(val3[1],'%Y-%m-%d %H:%M:%S')):
                                                fac_work_date = datetime.strftime(fac_work_date,"%Y-%m-%d")
                                                if fac_work_date == temp2 :
                                                    factory_work_list.append(fac_work_date)
                                    actual_left_day = list(set(actual_left_day)-set(factory_work_list)) 
#                                print "in actual_left_day=====222=========",actual_left_day                
                                if actual_left_day :
                                     actual_left_day = sorted(actual_left_day, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
                                     casual_allocate_leave=[]
                                     total_casual_check_list=[]
#                                     print "cl_left=================",cl_left                                  
                                     if cl_left:
                                        max_allow_cl_leave = 0
                                        max_allocated_cl_leave=7
                                        count=0
                                        casual_id = hol_status_obj.search(cr, uid, [('name','=',casual_val)])
                                        earned_id = hol_status_obj.search(cr, uid, [('name','=','Earned Leaves')])
                                        if casual_id :
                                            leave_month = month_id_int
                                            create_list=[]
                                            exist_cas_leave_list=[]
                                            exist_leave_casual_list=[]
                                            exist_earned_leave=[]                                         
                                            #### Check Already given Casual & Earned leave in same month ##### 
                                            if casual_id :
                                                for month_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(start_date,'%Y-%m-%d'),until=datetime.strptime(end_date,'%Y-%m-%d')):
                                                          month_date = datetime.strftime(month_date,"%Y-%m-%d")
                                                          exist_casual_leave_already=hol_obj.search(cr,uid,[('from_date','=',month_date),('holiday_status_id','=',casual_id[0]),('employee_id','=',val),('type','=','remove'),('state','=','validate')])                                                               
                                                          if exist_casual_leave_already :
                                                               exist_leave_casual_list.append(month_date)
                                                               
                                            if earned_id : 
                                                 for month_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(start_date,'%Y-%m-%d'),until=datetime.strptime(end_date,'%Y-%m-%d')):
                                                      month_date = datetime.strftime(month_date,"%Y-%m-%d")
                                                      exist_earned_leave_already=hol_obj.search(cr,uid,[('from_date','=',month_date),('holiday_status_id','=',earned_id[0]),('employee_id','=',val),('type','=','remove'),('state','=','validate')])                                                               
                                                      if exist_earned_leave_already :
                                                           exist_earned_leave.append(month_date)                                                          
                                            total_casual_check_list = exist_leave_casual_list + exist_earned_leave  
                                            
                                            ######  First  Max Casual Leave Allowed Calculation  #####                                           
                                            if join_val : 
                                                if join_val >= 7 :
                                                    join_val = 7

                                                casual_count_query = cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where "
                                                                                         " employee_id = '"+str(val)+"' and hh.type = 'remove' and hhs.name = '"+str(casual_val)+"'  and state = 'validate'  ")
                                                total_allocate_cl_leave = cr.fetchall()
#                                                print "total_allocate_cl_leave==============",total_allocate_cl_leave
                                                if total_allocate_cl_leave[0][0] !=None :
#                                                    print "in if============="
                                                    max_allow_cl_leave = join_val - int(total_allocate_cl_leave[0][0])
                                                else:
#                                                    print "in else============="
                                                    max_allow_cl_leave = join_val 
                                                    
                                                if exist_leave_casual_list:
                                                    if len(exist_leave_casual_list) >= max_allow_cl_leave :
                                                        max_allow_cl_leave = 0
                                                    else:
                                                        max_allow_cl_leave = max_allow_cl_leave - len(exist_leave_casual_list)
                                                         
                                                if join_val==1 :
                                                    punch_query = cr.execute("select name from attendance_timing where employee_id='"+str(val)+"' and month='"+str(month_id)+"' and year_id='"+str(year_id[0])+"'  ")
                                                    punch_day = cr.fetchall()
                                                    if len(punch_day) < 15  : 
                                                        max_allow_cl_leave = 0  

                                                for leave_allocate_day in actual_left_day :
                                                    if  leave_allocate_day in total_casual_check_list :
                                                       continue
                                                    if cl_left == 0:
                                                        break
                                                    if max_allow_cl_leave == 0 :
                                                        break
                                                    if max_allow_cl_leave > 0 :
                                                        till_date = leave_allocate_day+' '+'11:30:00' 
                                                        from_date = leave_allocate_day+' '+'3:30:00'
                                                        create_id = hol_obj.create(cr, uid,{'employee_id':val,'holiday_status_id':casual_id[0],'month':month_name,'date_from':from_date,'from_date':leave_allocate_day,'date_to':till_date,'state':'validate','number_of_days_temp':1,'leave_mode':'Automatic'})
                                                        button = hol_obj.holidays_validate(cr, uid, create_id, context=None)
                                                        casual_allocate_leave.append(leave_allocate_day)
                                                        cl_left = cl_left - 1
                                                        max_allow_cl_leave = max_allow_cl_leave - 1
                                                    else:
                                                        break    
                                            else: 
                                                casual_count_query = cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where "
                                                                                             " employee_id = '"+str(val)+"' and hh.type = 'remove' and hhs.name = '"+str(casual_val)+"'  and state = 'validate'  ")
                                                total_allocate_cl_leave = cr.fetchall()
                                                if total_allocate_cl_leave[0][0] !=None  :
                                                    if int(total_allocate_cl_leave[0][0]) < 7 :
                                                        if leave_month > 7 :
                                                            max_allow_cl_leave = max_allocated_cl_leave - int(total_allocate_cl_leave[0][0])
                                                        else:
                                                            max_allow_cl_leave = leave_month - int(total_allocate_cl_leave[0][0])
                                                    else:
                                                        max_allow_cl_leave=0
                                                else:
                                                     if leave_month > 7 :
                                                         max_allow_cl_leave = max_allocated_cl_leave
                                                     else:
                                                         max_allow_cl_leave = leave_month   
                                                    
                                                #### Second Maximum Leave Allowed Calculation  #### 
                                                
                                                if exist_leave_casual_list:
                                                    if len(exist_leave_casual_list) >= max_allow_cl_leave :
                                                        max_allow_cl_leave = 0
                                                    else:
                                                        max_allow_cl_leave = max_allow_cl_leave - len(exist_leave_casual_list)
                                                            
                                                #### Casual Leave Allocation ####        
                                                for leave_allocate_day in actual_left_day :
                                                    if  leave_allocate_day in total_casual_check_list :
                                                       continue
                                                    if cl_left == 0:
                                                        break
                                                    if max_allow_cl_leave == 0 :
                                                        break
                                                    if  max_allow_cl_leave > 0 :
                                                        if cl_left > 0 :
                                                            till_date=leave_allocate_day+' '+'11:30:00' 
                                                            from_date=leave_allocate_day+' '+'3:30:00'
                                                            create_id=hol_obj.create(cr, uid,{'employee_id':val,'holiday_status_id':casual_id[0],'month':month_name,'date_from':from_date,'from_date':leave_allocate_day,'date_to':till_date,'state':'validate','number_of_days_temp':1,'leave_mode':'Automatic'})
                                                            button=hol_obj.holidays_validate(cr, uid, create_id, context=None)
                                                            casual_allocate_leave.append(leave_allocate_day)
                                                            cl_left=cl_left-1
                                                            max_allow_cl_leave = max_allow_cl_leave - 1
                                                    else:
                                                        break
#                                     print "el_left=============",el_left
                                     if el_left :
                                           earn_left_day=list(set(actual_left_day)-set(casual_allocate_leave))
                                           earn_left_day= sorted(earn_left_day, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
                                           if len(earn_left_day) >=1:
                                               earned_id = hol_status_obj.search(cr, uid, [('name','=','Earned Leaves')])
                                               casual_id = hol_status_obj.search(cr, uid, [('name','=',casual_val)])
                                               exist_leave_casual_list1=[]
                                               exist_leave_earned_list=[]
                                               total_exist_leave=[]
                                               if casual_id :
                                                    for month_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(start_date,'%Y-%m-%d'),until=datetime.strptime(end_date,'%Y-%m-%d')):
                                                          month_date = datetime.strftime(month_date,"%Y-%m-%d")
                                                          exist_casual_leave_already=hol_obj.search(cr,uid,[('from_date','=',month_date),('holiday_status_id','=',casual_id[0]),('employee_id','=',val),('type','=','remove'),('state','=','validate')])                                                               
                                                          if exist_casual_leave_already :
                                                               exist_leave_casual_list1.append(month_date)
                                               if earned_id :                
                                                    for month_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(start_date,'%Y-%m-%d'),until=datetime.strptime(end_date,'%Y-%m-%d')):
                                                          month_date = datetime.strftime(month_date,"%Y-%m-%d")
                                                          exist_earned_leave_already = hol_obj.search(cr,uid,[('from_date','=',month_date),('holiday_status_id','=',earned_id[0]),('employee_id','=',val),('type','=','remove'),('state','=','validate')])                                                               
                                                          if exist_earned_leave_already :
                                                               exist_leave_earned_list.append(month_date)  
                                               total_exist_leave= exist_leave_casual_list1 + exist_leave_earned_list 
                                               for leave_allocate_day in earn_left_day :
                                                   if leave_allocate_day in total_exist_leave :
                                                       continue 
                                                   if el_left==0:
                                                        break 
                                                   till_date=leave_allocate_day+' '+'11:30:00' 
                                                   from_date=leave_allocate_day+' '+'3:30:00'
                                                   er_id=hol_obj.create(cr, uid,{'employee_id':val,'holiday_status_id':earned_id[0],'month':month_name,'date_from':from_date,'from_date':leave_allocate_day,'date_to':till_date,'state':'validate','number_of_days_temp':1,'leave_mode':'Automatic'})
                                                   button=hol_obj.holidays_validate(cr, uid, er_id, context=None)
            #                                        if emp_browse.earn_leave >=1 :
            #                                            emp_obj.write(cr,uid,[val],{'earn_leave':emp_browse.earn_leave-1})
                                                   el_left=el_left-1

        else :
            raise osv.except_osv(_('Warning !'),_("Please enter the First Day of the Month in From Date and Last day of month in End Date Field only..!!!"))        

        return True 



#                                         Start this is use for temparary bases

#    def update_el(self, cr, uid, ids,context=None):
#        count = []
#        emp_obj = self.pool.get('hr.employee')
#        rec = self.browse(cr, uid, ids)
#            
#        if rec.company_id:  
#             emp_ids = emp_obj.search(cr, uid,[('company_id','=',rec.company_id.id),('active','=',True)])
#        elif rec.employee_id:  
#             emp_ids = emp_obj.search(cr, uid,[('id','=',rec.employee_id.id),('active','=',True)])     
#        else:
#             emp_ids = emp_obj.search(cr, uid,[('active','=',True)])

#        for val in emp_obj.browse(cr, uid, emp_ids):
#        cr.execute("select hr.id from hr_employee as hr left join resource_resource as rr on hr.resource_id = rr.id where rr.active = 'True' and hr.doj <= '2015-05-01' and hr.id = '"+str(val.id)+"' order by hr.id")
#        temp = cr.fetchall()
#        for line in temp:
#            pro = cr.execute("""update hr_employee set earn_date=%s where id=%s""", ('2015-12-31',line))   
            
#        cr.execute("select hr.id, hr.doj from hr_employee as hr left join resource_resource as rr on hr.resource_id = rr.id where rr.active = 'True' and hr.doj>='2017-01-01' and hr.earn_date = hr.doj order by hr.id")
#        temp1 = cr.fetchall()
#        for l in temp1:
#            doj = datetime.strptime(l[1],'%Y-%m-%d')
#            earn_date = doj + timedelta(days=240)
#            earn_date = earn_date.strftime("%Y-%m-%d")
#            pro1 = cr.execute("""update hr_employee set earn_date=%s where id=%s""", (earn_date,l[0]))
#
#        cr.execute("select hr.id, hr.doj from hr_employee as hr left join resource_resource as rr on hr.resource_id = rr.id where rr.active = 'True' and hr.doj>='2017-01-01' and hr.earn_date <> hr.doj order by hr.id")
#        temp1 = cr.fetchall()
#        for l1 in temp1:
#            doj = datetime.strptime(l1[1],'%Y-%m-%d')
#            earn_date = doj + timedelta(days=240)
#            earn_date = earn_date.strftime("%Y-%m-%d")
#            pro1 = cr.execute("""update hr_employee set earn_date=%s where id=%s""", (earn_date,l1[0]))
#            
#            cr.execute("delete from earn_leave_history where employee_id = '"+str(l1[0])+"' ")
#            emp_obj.write(cr, uid, [l1[0]],{'earn_leave':0,'earn_open':0})
#            
#            hol_id = self.pool.get('hr.holidays').search(cr, uid, [('holiday_type','=','employee'),('employee_id','=',l1[0]),('type','=','add'),('state','=','validate'),('holiday_status_id','=',5)])
#            if hol_id:
#                rec = self.pool.get('hr.holidays').browse(cr, uid, hol_id)
#                self.pool.get('hr.holidays').write(cr, uid, hol_id,{'number_of_days_temp':0,'number_of_days':0})

#        count.append(val.id)
                        
#        return True

#                                                    End this is use for temparary bases

    def float_time_convert(self,float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return (factor * int(math.floor(val)), int(round((val % 1) * 60)))
    
    def calculate_time(self, cr, uid, ids, date, start, end):
        time1 = time2 = '00:00'
        val1 = self.float_time_convert(start)
        if val1 and len(str(val1[1])) == 1:
            time1 = str(val1[0]) +':'+'0'+str(val1[1])
        
        if val1 and len(str(val1[1])) == 2:
            time1 = str(val1[0]) +':'+str(val1[1])
        
        start_hr = val1[0]
        start_time = str(date) +' '+ str(time1) + ':00'
        
        val2 = self.float_time_convert(end)
        if val2 and len(str(val2[1])) == 1:
            time2 = str(val2[0]) +':'+'0'+str(val2[1])
        
        if val2 and len(str(val2[1])) == 2:
            time2 = str(val2[0]) +':'+str(val2[1])
        
        end_hr = val2[0]
        
#        min1 = str(start).split('.')
#        if len(min1) > 1:
#            if int(min1[1]) > 0: 
#                if len(min1[1]) == 1:
#                    time1 = min1[0] +':'+ str(int(min1[1]) * 6)
#                    
#                if len(min1[1]) == 2:
#                    time1 = min1[0] +':'+ str(int(int(min1[1]) * 0.6))
#                
#            else:
#                time1 = min1[0] +':'+ str('00')
#        else:
#            time1 = min1[0] +':'+ str('00')
#        start_hr = min1[0]
#        start_time = str(date) +' '+ str(time1) + ':00'
#        
#        min2 = str(end).split('.')
#        if len(min2) > 1:
#            if int(min2[1]) > 0: 
#                if len(min2[1]) == 1:
#                    time2 = min2[0] +':'+ str(int(min2[1]) * 6)
#                    
#                if len(min2[1]) == 2:
#                    time2 = min2[0] +':'+ str(int(int(min2[1]) * 0.6))
#                
#            else:
#                time2 = min2[0] +':'+ str('00')
#        else:
#            time2 = min2[0] +':'+ str('00')
#        end_hr = min2[0]
        
        start_time1 = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S').timetuple()
        year = start_time1.tm_year
        mon = start_time1.tm_mon
        day = start_time1.tm_mday
        hour = start_time1.tm_hour
        min  = start_time1.tm_min
        sec = start_time1.tm_sec
#        if hour == 0 and min > 0:
#            hour1 = 23
#            day1 = day - 1
#            if day1 == 0:
#                if mon == 1:
#                    mon1 = 12
#                    year1 = year -1
#                elif mon == 3:
#                    if year % 4 == 0:
#                        day = 29
#                        mon1 = mon - 1
#                    else:
#                        day = 28
#                        mon1 = mon - 1
#                    year1 = year
#                elif mon == 8:
#                    day1 = 31
#                    mon1 = mon - 1
#                    year1 = year
#                    
#                elif mon in [5,7,10,12]:
#                    day1 = 30
#                    mon1 = mon - 1
#                    year1 = year
#                    
#                elif mon in [4,6,9,11]:
#                    day1 = 31
#                    mon1 = mon - 1
#                    year1 = year
#        else:
        hour1 = hour
        mon1 = mon
        day1 = day
        year1 = year
            
#===========================================================================
        if int(start_hr) > int(end_hr):
            day2 = day + 1
            if mon in [1,3,5,7,8,10,12]:
                if day >= 31:
                    day2 = 1
                    mon2 = mon + 1
                    year2 = year
                    if mon2 > 12:
                        year2 = year + 1
                        mon2 = 1
                else:
                    mon2 = mon
                    year2 = year
                
            elif mon in [4,6,9,11]:
                if day >= 30:
                    day2 = 1
                    mon2 = mon + 1
                    year2 = year
                else:
                    mon2 = mon
                    year2 = year
            elif mon == 2:
                if year % 4 == 0:
                    if day >= 29:
                        day2 = 1
                        mon2 = mon + 1
                        year2 = year
                    else:
                        mon2 = mon
                        year2 = year
                else:
                    if day >= 28:
                        day2 = 1
                        mon2 = mon + 1
                        year2 = year
                    else:
                        mon2 = mon
                        year2 = year
            time2_split = time2.split(':')
            hour2 = int(end_hr)
            min2 = int(time2_split[1])
        else:
            time2_split = time2.split(':')
            hour2 = int(end_hr)
            min2 = int(time2_split[1])
            mon2 = mon
            day2 = day
            year2 = year            
#        =========================================================================
        
        
        if (hour + 22) > 24:
            hour = abs(24 - (hour + 22))
            day = day + 1
                                    
            if mon in [1,3,5,7,8,10,12]:
                if day > 31:
                    day = 1
                    mon = mon + 1
                if mon > 12:
                    year = year + 1
                    mon = 1
            elif mon in [4,6,9,11]:
                if day > 30:
                    day = 1
                    mon = mon + 1
            elif mon == 2:
                if year % 4 == 0:
                    if day > 29:
                        day = 1
                        mon = mon + 1
                else:
                    if day > 28:
                        day = 1
                        mon = mon + 1
        else:
            hour = hour + 22
            
        if len(str(mon1)) < 2:
            mon1 = '0'+str(mon1)
        if len(str(day1)) < 2:
            day1 = '0'+str(day1)
        if len(str(mon2)) < 2:
            mon2 = '0'+str(mon2)
        if len(str(day2)) < 2:
            day2 = '0'+str(day2)
        if len(str(mon)) < 2:
            mon = '0'+str(mon)
        if len(str(day)) < 2:
            day = '0'+str(day)

                
        start_time = str(year1) +'-'+str(mon1)+'-'+str(day1) +' '+ str(hour1)+':'+str(min)+':'+str(sec)
        end_time = str(year2) +'-'+str(mon2)+'-'+str(day2) +' '+ str(hour2)+':'+str(min2)+':'+str('00')
        final_time = str(year) +'-'+str(mon)+'-'+str(day) +' '+ str(hour)+':'+str(min)+':'+str(sec)
        working_time = (datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
        working_hour = working_time.total_seconds()/3600
        timing = {
                  'start_time':start_time,
                  'end_time':end_time,
                  'final_time':final_time,
                  'working_hour':working_hour,
                  }
        
        return timing
    
    def run_synchro_attendance(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        att_obj = self.pool.get('hr.attendance')
        shift_obj = self.pool.get('hr.shift.line')
        count = 0
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            
            if each.employee_id and each.department_id and each.type:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True),('type','=',each.type)])
            elif each.employee_id and each.type:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('type','=',each.type)])
            elif each.department_id and each.type:
                list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True),('type','=',each.type)])
            elif each.type:
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('type','=',each.type)])                
            elif each.employee_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True)])
            elif each.department_id:
                list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True)])
            else:
                list_ids = emp_obj.search(cr, uid, [('active','=',True)])
            if each.start_count>0 and each.to_count>0:
                list_ids.sort()
                list_ids = list_ids[each.start_count-1:each.to_count]
            emp_ids = emp_obj.browse(cr, uid, list_ids)

            if each.name and not each.end_date:
                for emp in emp_ids:
                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',each.name)], limit=1, order='name DESC')
                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',each.name)], limit=1, order='name ASC')
                    if prev_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    elif next_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    else:
                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    if shift_data:
                        for line in shift_data.shift_id.shift_line:
                            timing = self.calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                            query = "select name from raw_attendance where name > (select min(name + interval '15 minute')\
                            from hr_attendance where name + interval '5 hours 30 minute' > \
                            to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp \
                            - interval '1 hours 30 minute' and employee_id = '"+str(emp.id)+"') and name < \
                            (select max(name - interval '15 minute') from hr_attendance where name + interval '5 hours 30 minute' < \
                            '"+str(timing['final_time'])+"' and employee_id = '"+str(emp.id)+"') and employee_id = \
                            '"+str(emp.id)+"' order by  name"
                            cr.execute(query)
                            mid_result = cr.fetchall()
                            tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                            month = tm_tuple.tm_mon
                            year = tm_tuple.tm_year        
                            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)]) 
                            
                            for mid_data in mid_result:
                                if mid_data and len(mid_data[0])>0 and mid_data[0] != None:
                                    cr.execute("delete from hr_attendance where name = '"+str(mid_data[0])+"' and employee_id = '"+str(emp.id)+"'")
                                    att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':each.name,
                                    'name':mid_data[0],'employee_id':emp.id,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                    count += 1
                                    print "=========================NEW INDIVISIBLE MID RECORD IS CREATED===========================",count,each.name
                    else:
                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    
            else:
                if each.name and each.end_date and each.employee_id:
                    start_date = datetime.strptime(each.name,'%Y-%m-%d')
                    end_date = datetime.strptime(each.end_date,'%Y-%m-%d')
                    end_tm_tuple = datetime.strptime(each.end_date,'%Y-%m-%d').timetuple()
                    while (start_date <= end_date):
                        date1 = start_date.strftime('%Y-%m-%d')
                        tm_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()
                        if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                            break
                        if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                            break
                        
                        for emp in emp_ids:
                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',date1)], limit=1, order='name DESC')
                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',date1)], limit=1, order='name ASC')
                            if prev_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                            elif next_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                            if shift_data:
                                for line in shift_data.shift_id.shift_line:
                                    timing = self.calculate_time(cr, uid, ids, date1, line.from_time, line.to_time)
                                    query = "select name from raw_attendance where name > (select min(name + interval '15 minute')\
                                    from hr_attendance where name + interval '5 hours 30 minute' > \
                                    to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp \
                                    - interval '1 hours 30 minute' and employee_id = '"+str(emp.id)+"') and name < \
                                    (select max(name - interval '15 minute') from hr_attendance where name + interval '5 hours 30 minute' < \
                                    '"+str(timing['final_time'])+"' and employee_id = '"+str(emp.id)+"') and employee_id = \
                                    '"+str(emp.id)+"' order by  name"
                                    cr.execute(query)
                                    mid_result = cr.fetchall()
                                    tm_tuple = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S').timetuple()
                                    month = tm_tuple.tm_mon
                                    year = tm_tuple.tm_year        
                                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)]) 
                                    
                                    for mid_data in mid_result:
                                        if mid_data and len(mid_data[0])>0 and mid_data[0] != None:
                                            cr.execute("delete from hr_attendance where name = '"+str(mid_data[0])+"' and employee_id = '"+str(emp.id)+"'")
                                            att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':date1,
                                            'name':mid_data[0],'employee_id':emp.id,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                            count += 1
                                            print "=========================NEW INDIVISIBLE MID RECORD IS CREATED===========================",count,date1
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    
                        start_date += timedelta(days=1)
                    
        return True
    
    def run_synchro(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        att_obj = self.pool.get('hr.attendance')
        shift_obj = self.pool.get('hr.shift.line')
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            if each.employee_id and each.department_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
            elif each.employee_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
            elif each.department_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
            elif each.company_id and each.employment_type:
                print"1111111111111"
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('employment_type', '=', each.employment_type),('doj', '<=',each.name)])
                print"--------------list_ids---------",len(list_ids)
            elif each.company_id:
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
            elif each.employee_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('doj', '<=',each.name)])
#            elif each.employment_type:
#                list_ids = emp_obj.search(cr, uid, [('employment_type', '=', each.employment_type),('active','=',True),('doj', '<=',each.name)])
            elif each.employee_id and each.department_id:
                raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
            elif each.department_id:
                raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
            else:
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('doj', '<=',each.name)])
            if each.start_count>0 and each.to_count>0:
                list_ids.sort()
                list_ids = list_ids[each.start_count-1:each.to_count]
            emp_ids = emp_obj.browse(cr, uid, list_ids)
            if each.name and not each.end_date:
                count = 0
                for emp in emp_ids:
                    count+= 1
                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',each.name)], limit=1, order='name DESC')
                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',each.name)], limit=1, order='name ASC')
                    if prev_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    elif next_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    else:
                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    if shift_data:
                        for line in shift_data.shift_id.shift_line:
                            timing = self.calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                            query = "select min(raw.name) , max(raw.name) from raw_attendance as raw left join hr_employee as hr on (raw.employee_id=hr.id) where raw.name + interval '5 hours 30 minute' > \
                            to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                            and raw.name + interval '5 hours 30 minute' <= '"+str(timing['final_time'])+"' and raw.employee_id = '"+str(emp.id)+"' and hr.doj <= '"+str(each.name)+"'"      
                            cr.execute(query)
                            result = cr.fetchall()
                            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
                            month = tm_tuple.tm_mon
                            year = tm_tuple.tm_year        
                            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                            
                            raw_in_punch = raw_out_punch = False
#                            in_punch = out_punch = False

                            if result and len(result[0])>0 and result[0][0] != None:
                                raw_in_punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                
                            if result and len(result[0])>1 and result[0][1] != None:
                                raw_out_punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                            
                            if raw_in_punch and raw_out_punch and raw_in_punch == raw_out_punch:
                                continue
                            
                            if result :
                                if result[0] and result[0][0] != None and result[0][1] != None:
                                    punch_min = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                    punch_max=datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                    punch_diff=punch_max-punch_min
                                    punch_diff=str(punch_diff)
                                    punch_diff=punch_diff.split(':')
                                    punch_diff=float(punch_diff[0]+'.'+punch_diff[1])
                                    if  punch_diff >= 0.15 :
                                        if result[0] and result[0][0] != None:
                                            if len(result[0])>0 and result[0][0] != None:
                                                punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                                actual = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                to_delete_actual = timing['start_time']
                                                punch = punch + timedelta(hours=5,minutes=30)
                                                old_punch = result[0][0]
                                                punch_tuple =punch.timetuple()
                                                year = punch_tuple.tm_year
                                                mon = punch_tuple.tm_mon
                                                day = punch_tuple.tm_mday

                                                start_time = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                if punch > start_time:
                                                    temp_punch = start_time
                                                    temp = random.randrange(0,10)
                                                    punch = temp_punch + timedelta(hours=0,minutes=temp) 
                                                elif punch < start_time:
                                                    temp_punch = start_time
                                                    temp = random.randrange(0,10)
                                                    punch = temp_punch - timedelta(hours=0,minutes=temp)
                                                elif punch == start_time:
                                                    temp_punch = start_time
                                                    punch = temp_punch + timedelta(hours=0,minutes=0)
                                                
                                                punch = punch - timedelta(hours=5,minutes=30)
                                                search_date1 = punch.strftime("%Y-%m-%d")
                                                punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                
                                                punch_time = datetime.strptime(punch,"%Y-%m-%d %H:%M:%S")
                                                punch_in_time = punch_time.strftime("%Y-%m-%d 00:00:00")
                                                punch_out_time = punch_time.strftime("%Y-%m-%d 23:59:59")
                                                
                                                cr.execute("delete from hr_attendance where search_date = '"+str(search_date1)+"' and employee_id = '"+str(emp.id)+"' and method = 'Auto'")
                                                
                                                min_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':each.name,'search_date':search_date1,
                                                'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                
                                                print "=========================NEW INDIVISIBLE MINIMUM RECORD IS CREATED===========================",min_id,count,each.name
                                            
                                        if result[0] and result[0][1] != None:
                                            if len(result[0])>1 and result[0][1] != None:
                                                punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                                to_delete_punch = result[0][1]
                                                punch = punch + timedelta(hours=5,minutes=30)
                                                shift_timing = datetime.strptime(timing['end_time'],"%Y-%m-%d %H:%M:%S")
                                                if punch >= shift_timing:
                                                    temp_punch = shift_timing
                                                    temp = random.randrange(0,5)
                                                    punch = temp_punch + timedelta(hours=0,minutes=temp) 
                                                elif punch < shift_timing:
                                                    temp_punch = shift_timing
                                                    temp = random.randrange(0,5)
                                                    punch = temp_punch + timedelta(hours=0,minutes=temp) 
                                                    
                                                    
                                                punch = punch - timedelta(hours=5,minutes=30)
                                                search_date2 = punch.strftime("%Y-%m-%d")
                                                punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                
#                                                cr.execute("delete from hr_attendance where search_date = '"+str(search_date2)+"' and employee_id = '"+str(emp.id)+"' and method = 'Auto'")
                                                
                                                max_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':each.name,'search_date':search_date1,
                                                'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                
                                                print "=========================NEW INDIVISIBLE MAXIMUM RECORD IS CREATED===========================",max_id,count,each.name
                                        
                    else:
                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
        
            else:
                if each.name and each.end_date and each.employee_id:
                    count = 0
                    shift_data = []
                    start_date = datetime.strptime(each.name,'%Y-%m-%d')
                    end_date = datetime.strptime(each.end_date,'%Y-%m-%d')
                    end_tm_tuple = datetime.strptime(each.end_date,'%Y-%m-%d').timetuple()
                    while (start_date <= end_date):
                        date1 = start_date.strftime('%Y-%m-%d')
                        tm_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()
                        if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                            break
                        if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                            break
                        for emp in emp_ids:
                            count += 1
                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',date1)], limit=1, order='name DESC')
                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',date1)], limit=1, order='name ASC')
                            if prev_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                            elif next_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                            if shift_data:
                                for line in shift_data.shift_id.shift_line:
                                    timing = self.calculate_time(cr, uid, ids, date1, line.from_time, line.to_time)
                                    query = "select min(raw.name) , max(raw.name) from raw_attendance as raw left join hr_employee as hr on (raw.employee_id=hr.id) where raw.name + interval '5 hours 30 minute' > \
                                                to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                                and raw.name + interval '5 hours 30 minute' <= '"+str(timing['final_time'])+"' and raw.employee_id = '"+str(emp.id)+"' and hr.doj <= '"+str(date1)+"' "
                                    cr.execute(query)
                                    result = cr.fetchall()
                                    tm_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()
                                    month = tm_tuple.tm_mon
                                    year = tm_tuple.tm_year        
                                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])  
                                    raw_in_punch = raw_out_punch = in_punch = out_punch = False
                                    if result and len(result[0])>0 and result[0][0] != None:
                                        raw_in_punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                        
                                    if result and len(result[0])>1 and result[0][1] != None:
                                        raw_out_punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                    
                                    if raw_in_punch and raw_out_punch and raw_in_punch == raw_out_punch:
                                        continue
                                    if result :
                                        if result[0][0] and result[0][1] :
                                            punch_min = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                            punch_max=datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                            punch_diff=punch_max-punch_min
                                            punch_diff=str(punch_diff)
                                            punch_diff=punch_diff.split(':')
                                            punch_diff=float(punch_diff[0]+'.'+punch_diff[1])
                                            if  punch_diff >= 0.15 :
                                                if result[0] and result[0][0] != None:
                                                    if len(result[0])>0 and result[0][0] != None:
                                                        punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                                        actual = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        to_delete_actual = timing['start_time']
                                                        punch = punch + timedelta(hours=5,minutes=30)
                                                        old_punch = result[0][0]
                                                        punch_tuple =punch.timetuple()
                                                        year = punch_tuple.tm_year
                                                        mon = punch_tuple.tm_mon
                                                        day = punch_tuple.tm_mday
#                                                        val1 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'07:45:00'
#                                                        val1 = datetime.strptime(val1,'%Y-%m-%d %H:%M:%S')
#                                                        val2 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'08:40:00'
#                                                        val2 = datetime.strptime(val2,'%Y-%m-%d %H:%M:%S')
#                                                        val3 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'09:08:00'
#                                                        val3 = datetime.strptime(val3,'%Y-%m-%d %H:%M:%S')
#                                                        val4 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'10:00:00'
#                                                        val4 = datetime.strptime(val4,'%Y-%m-%d %H:%M:%S')
#                                                        val5 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'11:00:00'
#                                                        val5 = datetime.strptime(val5,'%Y-%m-%d %H:%M:%S')
#                                                        val6 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'12:00:00'
#                                                        val6 = datetime.strptime(val6,'%Y-%m-%d %H:%M:%S')

                                                        start_time = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        if punch > start_time:
                                                            temp_punch = start_time
                                                            temp = random.randrange(0,10)
                                                            punch = temp_punch + timedelta(hours=0,minutes=temp) 
                                                        elif punch < start_time:
                                                            temp_punch = start_time
                                                            temp = random.randrange(0,10)
                                                            punch = temp_punch - timedelta(hours=0,minutes=temp)
                                                        elif punch == start_time:
                                                            temp_punch = start_time
                                                            punch = temp_punch + timedelta(hours=0,minutes=0)
                                                        
#                                                        if punch > val1 and punch <= val2:
#                                                            temp_punch = str(year) +'-'+str(mon)+'-'+str(day) +' '+'08:45:00'
#                                                            temp_punch = datetime.strptime(temp_punch,'%Y-%m-%d %H:%M:%S')
#                                                            temp = random.randrange(1,30)
#                                                            punch = temp_punch + timedelta(hours=0,minutes=temp) 
#                                                        elif punch > val2 and punch <= val3:
#                                                            temp_punch = str(year) +'-'+str(mon)+'-'+str(day) +' '+'09:09:00'
#                                                            temp_punch = datetime.strptime(temp_punch,'%Y-%m-%d %H:%M:%S')
#                                                            temp = random.randrange(0,6)
#                                                            punch = temp_punch + timedelta(hours=0,minutes=temp)
#                                                        elif punch > val3 and punch <= val4:
#                                                            punch = punch
#                                                        elif punch > val4 and punch <= val5:
#                                                            temp_punch = str(year) +'-'+str(mon)+'-'+str(day) +' '+'09:15:00'
#                                                            temp_punch = datetime.strptime(temp_punch,'%Y-%m-%d %H:%M:%S')
#                                                            temp = random.randrange(0,15)
#                                                            punch = temp_punch + timedelta(hours=0,minutes=temp)
#                                                        elif punch > val5 and punch <= val6:
#                                                            temp_punch = str(year) +'-'+str(mon)+'-'+str(day) +' '+'09:30:00'
#                                                            temp_punch = datetime.strptime(temp_punch,'%Y-%m-%d %H:%M:%S')
#                                                            temp = random.randrange(0,30)
#                                                            punch = temp_punch + timedelta(hours=0,minutes=temp)
#                                                            
#                                                        else:
#                                                            continue
                                                        
                                                        punch = punch - timedelta(hours=5,minutes=30)
                                                        search_date1 = punch.strftime("%Y-%m-%d")
                                                        punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                        punch_time = datetime.strptime(punch,"%Y-%m-%d %H:%M:%S")
                                                        punch_in_time = punch_time.strftime("%Y-%m-%d 00:00:00")
                                                        punch_out_time = punch_time.strftime("%Y-%m-%d 23:59:59")
                                                        
                                                        cr.execute("delete from hr_attendance where search_date = '"+str(search_date1)+"' and employee_id = '"+str(emp.id)+"' and method = 'Auto'")
            
                                                        min_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':date1,'search_date':search_date1,
                                                        'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                        
                                                        
                                                        print "=========================NEW INDIVISIBLE MINIMUM RECORD IS CREATED===========================",min_id,count,date1              
                                                    
                                                if result[0] and result[0][1] != None:
                                                    if len(result[0])>1 and result[0][1] != None:
                                                        punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                                        to_delete_punch = result[0][1]
                                                        punch = punch + timedelta(hours=5,minutes=30)
                                                        shift_timing = datetime.strptime(timing['end_time'],"%Y-%m-%d %H:%M:%S")
                                                        if punch >= shift_timing:
                                                            temp_punch = shift_timing
                                                            temp = random.randrange(0,5)
                                                            punch = temp_punch + timedelta(hours=0,minutes=temp) 
                                                        elif punch < shift_timing:
                                                            temp_punch = shift_timing
                                                            temp = random.randrange(0,5)
                                                            punch = temp_punch + timedelta(hours=0,minutes=temp) 
                                                            
#                                                            ot_time = punch - shift_timing
#                                                            ot_min = ot_time.seconds/60
#                                                            total_ot_min = ot_min/4           # This is for reducing the OT, 4 times
#                                                            if total_ot_min <= 120 :
#                                                                final_ot_hr = total_ot_min/60
#                                                                final_ot_min = total_ot_min%60
#                                                                punch = shift_timing + timedelta(hours=final_ot_hr,minutes=final_ot_min)
#                                                            else :
#                                                                final_ot_hr = 2
#                                                                final_ot_min = 0
#                                                                punch = shift_timing + timedelta(hours=final_ot_hr,minutes=final_ot_min)

                                                        punch = punch - timedelta(hours=5,minutes=30)
                                                        search_date2 = punch.strftime("%Y-%m-%d")
                                                        punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                        
#                                                        cr.execute("delete from hr_attendance where search_date = '"+str(search_date2)+"' and employee_id = '"+str(emp.id)+"' and method = 'Auto'")
                                                        max_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':date1,'search_date':search_date1,
                                                        'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto',})
                                                        
                                                        print "=========================NEW INDIVISIBLE MAXIMUM RECORD IS CREATED===========================",max_id,count,date1
                                                
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                        start_date += timedelta(days=1)

        return True
    
    def run_synchro_comp(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        att_obj = self.pool.get('hr.attendance')
        shift_obj = self.pool.get('hr.shift.line')
        
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            if each.employee_id and each.department_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
            elif each.employee_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
            elif each.department_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
            elif each.company_id:
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('doj', '<=',each.name)])
            elif each.employee_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('doj', '<=',each.name)])
            elif each.employee_id and each.department_id:
                raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
            elif each.department_id:
                raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
            else:
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('doj', '<=',each.name)])
            if each.start_count>0 and each.to_count>0:
                list_ids.sort()
                list_ids = list_ids[each.start_count-1:each.to_count]
            emp_ids = emp_obj.browse(cr, uid, list_ids)
            if each.name and not each.end_date:
                count = 0
                for emp in emp_ids:
                    count  += 1
                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',each.name)], limit=1, order='name DESC')
                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',each.name)], limit=1, order='name ASC')
                    if prev_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    elif next_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    else:
                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    if shift_data:
                        for line in shift_data.shift_id.shift_line:
                            
                            timing = self.calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                            query = "select min(raw.name) , max(raw.name) from raw_attendance as raw left join hr_employee as hr on (raw.employee_id=hr.id) where raw.name + interval '5 hours 30 minute' > \
                                    to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                    and raw.name + interval '5 hours 30 minute' <= '"+str(timing['final_time'])+"' and raw.employee_id = '"+str(emp.id)+"' and hr.doj <= '"+str(each.name)+"'"
                            cr.execute(query)
                            result = cr.fetchall()
                            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
                            month = tm_tuple.tm_mon
                            year = tm_tuple.tm_year        
                            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])  
                            raw_in_punch = raw_out_punch = in_punch = out_punch = False
                            in_punch = out_punch = False
                            if result and len(result[0])>0 and result[0][0] != None:
                                raw_in_punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                
                            if result and len(result[0])>1 and result[0][1] != None:
                                raw_out_punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                            
                            if raw_in_punch and raw_out_punch and raw_in_punch == raw_out_punch:
                                raw_in_punch = result[0][0]
#                                continue
                            if result :
                                if result[0][0] and result[0][1] :
                                    punch_min = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                    punch_max=datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                    punch_diff=punch_max-punch_min
                                    punch_diff=str(punch_diff)
                                    punch_diff=punch_diff.split(':')
                                    punch_diff=float(punch_diff[0]+'.'+punch_diff[1])
                                    if  punch_diff >= 0.15 :
                                        if result[0] and result[0][0] != None:
                                            if len(result[0])>0 and result[0][0] != None:
                                                punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                                actual = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                to_delete_actual = timing['start_time']
                                                punch = punch + timedelta(hours=5,minutes=30)
                                                old_punch = result[0][0]
                                                punch = punch - timedelta(hours=5,minutes=30)
                                                search_date1 = punch.strftime("%Y-%m-%d")
                                                punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                if to_delete_actual == old_punch == punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                elif to_delete_actual == old_punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(old_punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                elif to_delete_actual == punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                elif old_punch == punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                else:
                                                    cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                min_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':each.name,'search_date':search_date1,
                                                'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                print "=========================NEW INDIVISIBLE MINIMUM RECORD IS CREATED===========================",min_id,count,each.name
                                            
                                        if result[0] and result[0][1] != None:
                                            if len(result[0])>1 and result[0][1] != None:
                                                punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                                to_delete_punch = result[0][1]
                                                search_date2 = punch.strftime("%Y-%m-%d")
                                                punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                if to_delete_actual == punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                else:
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                    cr.execute("delete from hr_attendance where name = '"+str(to_delete_punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                
                                                max_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':each.name,'search_date':search_date1,
                                                'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                print "=========================NEW INDIVISIBLE MAXIMUM RECORD IS CREATED===========================",max_id,count,each.name

                                    elif  punch_diff < 0.15 :
                                        if result[0] and result[0][0] != None:
                                            if len(result[0])>0 and result[0][0] != None:
                                                punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                                actual = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                to_delete_actual = timing['start_time']
                                                punch = punch + timedelta(hours=5,minutes=30)
                                                old_punch = result[0][0]
                                                punch = punch - timedelta(hours=5,minutes=30)
                                                search_date1 = punch.strftime("%Y-%m-%d")
                                                punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                if to_delete_actual == old_punch == punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                elif to_delete_actual == old_punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(old_punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                elif to_delete_actual == punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                elif old_punch == punch:
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                else:
                                                    cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                    cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                min_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':each.name,'search_date':search_date1,
                                                'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                print "===FOR===SINGLE===PUNCH===NEW INDIVISIBLE MAXIMUM RECORD IS CREATED===",min_id,count,each.name
                                        
                    else:
                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
        
            else:
                if each.name and each.end_date and each.employee_id:
                    count = 0
                    shift_data = []
                    start_date = datetime.strptime(each.name,'%Y-%m-%d')
                    end_date = datetime.strptime(each.end_date,'%Y-%m-%d')
                    end_tm_tuple = datetime.strptime(each.end_date,'%Y-%m-%d').timetuple()
                    while (start_date <= end_date):
                        date1 = start_date.strftime('%Y-%m-%d')
                        tm_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()
                        if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                            break
                        if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                            break
                        for emp in emp_ids:
                            count += 1
                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',date1)], limit=1, order='name DESC')
                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',date1)], limit=1, order='name ASC')
                            if prev_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                            elif next_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                            if shift_data:
                                for line in shift_data.shift_id.shift_line:
                                    
                                    timing = self.calculate_time(cr, uid, ids, date1, line.from_time, line.to_time)
                                    query = "select min(raw.name) , max(raw.name) from raw_attendance as raw left join hr_employee as hr on (raw.employee_id=hr.id) where raw.name + interval '5 hours 30 minute' > \
                                                to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                                and raw.name + interval '5 hours 30 minute' <= '"+str(timing['final_time'])+"' and raw.employee_id = '"+str(emp.id)+"' and hr.doj <= '"+str(date1)+"'"
                                    cr.execute(query)
                                    result = cr.fetchall()
                                    tm_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()
                                    month = tm_tuple.tm_mon
                                    year = tm_tuple.tm_year        
                                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])  
                                    raw_in_punch = raw_out_punch = in_punch = out_punch = False
                                    
                                    if result and len(result[0])>0 and result[0][0] != None:
                                        raw_in_punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                        
                                    if result and len(result[0])>1 and result[0][1] != None:
                                        raw_out_punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                    
                                    if raw_in_punch and raw_out_punch and raw_in_punch == raw_out_punch:
                                        raw_in_punch = result[0][0]
#                                        continue
                                    if result :
                                        if result[0][0] and result[0][1] :
                                            punch_min = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                            punch_max=datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                            punch_diff=punch_max-punch_min
                                            punch_diff=str(punch_diff)
                                            punch_diff=punch_diff.split(':')
                                            punch_diff=float(punch_diff[0]+'.'+punch_diff[1])
                                            if  punch_diff >= 0.15 :
                                                if result[0] and result[0][0] != None:
                                                    if len(result[0])>0 and result[0][0] != None:
                                                        punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                                        actual = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        to_delete_actual = timing['start_time']
                                                        punch = punch + timedelta(hours=5,minutes=30)
                                                        old_punch = result[0][0]
                                                        punch = punch - timedelta(hours=5,minutes=30)
                                                        search_date1 = punch.strftime("%Y-%m-%d")
                                                        punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                        
                                                        if to_delete_actual == old_punch == punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                        elif to_delete_actual == old_punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(old_punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                        elif to_delete_actual == punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                        elif old_punch == punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                        else:
                                                            cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                        min_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':date1,'search_date':search_date1,
                                                        'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                        print "=========================NEW INDIVISIBLE MINIMUM RECORD IS CREATED===========================",min_id,count,date1
                                                
                                                if result[0] and result[0][1] != None:
                                                    if len(result[0])>1 and result[0][1] != None:
                                                        punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                                        to_delete_punch = result[0][1]
                                                        search_date2 = punch.strftime("%Y-%m-%d")
                                                        punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                        if to_delete_actual == punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                        else:
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                            cr.execute("delete from hr_attendance where name = '"+str(to_delete_punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                
                                                        max_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':date1,'search_date':search_date1,
                                                        'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                        print "=========================NEW INDIVISIBLE MAXIMUM RECORD IS CREATED===========================",max_id,count,date1

                                            elif  punch_diff < 0.15 :
                                                if result[0] and result[0][0] != None:
                                                    if len(result[0])>0 and result[0][0] != None:
                                                        punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                                        actual = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")
                                                        to_delete_actual = timing['start_time']
                                                        punch = punch + timedelta(hours=5,minutes=30)
                                                        old_punch = result[0][0]
                                                        punch = punch - timedelta(hours=5,minutes=30)
                                                        search_date1 = punch.strftime("%Y-%m-%d")
                                                        punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                        
                                                        if to_delete_actual == old_punch == punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                        elif to_delete_actual == old_punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(old_punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                        elif to_delete_actual == punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                        elif old_punch == punch:
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                        else:
                                                            cr.execute("delete from hr_attendance where name = '"+str(to_delete_actual)+"' and employee_id = '"+str(emp.id)+"'")
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                            cr.execute("delete from hr_attendance where name = '"+str(punch)+"' and employee_id = '"+str(emp.id)+"'")
                                                        
                                                        min_id = att_obj.create(cr, uid, {'month':str(month),'year_id':year_id and year_id[0] or False,'day':date1,'search_date':search_date1,
                                                        'name':punch,'employee_id':emp.id,'company_id':emp.company_id and emp.company_id.id or False,'department_id':emp.department_id and emp.department_id.id or False,'method':'Auto'})
                                                        print "=======FOR===SINGLE===PUNCH============NEW INDIVISIBLE MINIMUM RECORD IS CREATED===========================",min_id,count,date1
                                                
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                        start_date += timedelta(days=1)

        return True

    def run_synch(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        att_obj = self.pool.get('hr.attendance')
        shift_obj = self.pool.get('hr.shift.line')
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            if each.employee_id and each.department_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),
                                                    ('department_id', '=', each.department_id.id),
                                                    ('active', '=', True), ('company_id', '=', each.company_id.id),
                                                    ('doj', '<=', each.name)])
            elif each.employee_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id), ('active', '=', True),
                                                    ('company_id', '=', each.company_id.id), ('doj', '<=', each.name)])
            elif each.department_id and each.company_id:
                list_ids = emp_obj.search(cr, uid,
                                          [('department_id', '=', each.department_id.id), ('active', '=', True),
                                           ('company_id', '=', each.company_id.id), ('doj', '<=', each.name)])
            elif each.company_id and each.employment_type:
                print"1111111111111"
                list_ids = emp_obj.search(cr, uid, [('active', '=', True), ('company_id', '=', each.company_id.id),
                                                    ('employment_type', '=', each.employment_type),
                                                    ('doj', '<=', each.name)])
                print"--------------list_ids---------", len(list_ids)
            elif each.company_id:
                list_ids = emp_obj.search(cr, uid, [('active', '=', True), ('company_id', '=', each.company_id.id),
                                                    ('doj', '<=', each.name)])
            elif each.employee_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id), ('active', '=', True),
                                                    ('doj', '<=', each.name)])
            # elif each.employment_type:
            #                list_ids = emp_obj.search(cr, uid, [('employment_type', '=', each.employment_type),('active','=',True),('doj', '<=',each.name)])
            elif each.employee_id and each.department_id:
                raise osv.except_osv(_('Warning !'), _("Please select Department along with Company"))
            elif each.department_id:
                raise osv.except_osv(_('Warning !'), _("Please select Department along with Company"))
            else:
                list_ids = emp_obj.search(cr, uid, [('active', '=', True), ('doj', '<=', each.name)])
            if each.start_count > 0 and each.to_count > 0:
                list_ids.sort()
                list_ids = list_ids[each.start_count - 1:each.to_count]
            emp_ids = emp_obj.browse(cr, uid, list_ids)
            if each.name and not each.end_date:
                count = 0
                for emp in emp_ids:
                    count += 1
                    prev_shift_ids = shift_obj.search(cr, uid,
                                                      [('employee_id', '=', emp.id), ('name', '<=', each.name)],
                                                      limit=1, order='name DESC')
                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id), ('name', '>', each.name)],
                                                      limit=1, order='name ASC')
                    if prev_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    elif next_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    else:
                        raise osv.except_osv(_('Warning !'), _(
                            "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                emp.sinid)))
                    if shift_data:
                        for line in shift_data.shift_id.shift_line:
                            timing = self.calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                            query = "select min(raw.name) , max(raw.name) from raw_attendance as raw left join hr_employee as hr on (raw.employee_id=hr.id) where raw.name + interval '5 hours 30 minute' > \
                            to_timestamp('" + str(timing['start_time']) + "','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                            and raw.name + interval '5 hours 30 minute' <= '" + str(
                                timing['final_time']) + "' and raw.employee_id = '" + str(
                                emp.id) + "' and hr.doj <= '" + str(each.name) + "'"
                            cr.execute(query)
                            result = cr.fetchall()
                            tm_tuple = datetime.strptime(each.name, '%Y-%m-%d').timetuple()
                            month = tm_tuple.tm_mon
                            year = tm_tuple.tm_year
                            year_id = self.pool.get('holiday.year').search(cr, uid, [('name', '=', year)])

                            raw_in_punch = raw_out_punch = False
                            #                            in_punch = out_punch = False

                            if result and len(result[0]) > 0 and result[0][0] != None:
                                raw_in_punch = datetime.strptime(result[0][0], "%Y-%m-%d %H:%M:%S")

                            if result and len(result[0]) > 1 and result[0][1] != None:
                                raw_out_punch = datetime.strptime(result[0][1], "%Y-%m-%d %H:%M:%S")

                            if raw_in_punch and raw_out_punch and raw_in_punch == raw_out_punch:
                                continue

                            if result:
                                if result[0] and result[0][0] != None and result[0][1] != None:
                                    punch_min = datetime.strptime(result[0][0], "%Y-%m-%d %H:%M:%S")
                                    punch_max = datetime.strptime(result[0][1], "%Y-%m-%d %H:%M:%S")
                                    punch_diff = punch_max - punch_min
                                    punch_diff = str(punch_diff)
                                    punch_diff = punch_diff.split(':')
                                    punch_diff = float(punch_diff[0] + '.' + punch_diff[1])
                                    if punch_diff >= 0.15:
                                        if result[0] and result[0][0] != None:
                                            if len(result[0]) > 0 and result[0][0] != None:
                                                punch = datetime.strptime(result[0][0], "%Y-%m-%d %H:%M:%S")
                                                actual = datetime.strptime(str(timing['start_time']),
                                                                           "%Y-%m-%d %H:%M:%S")
                                                to_delete_actual = timing['start_time']
                                                punch = punch + timedelta(hours=5, minutes=30)
                                                old_punch = result[0][0]
                                                punch_tuple = punch.timetuple()
                                                year = punch_tuple.tm_year
                                                mon = punch_tuple.tm_mon
                                                day = punch_tuple.tm_mday

                                                start_time = datetime.strptime(str(timing['start_time']),"%Y-%m-%d %H:%M:%S")

                                                print"============", punch, start_time
                                                if punch < start_time:
                                                    start_time = start_time -timedelta(hours=0, minutes=10)
                                                    temp_punch = start_time
                                                    temp = random.randrange(0, 10)
                                                    punch = temp_punch + timedelta(hours=0, minutes=temp)

                                                elif punch >= start_time:
                                                    punch = punch + timedelta(hours=0, minutes=0)

                                                punch = punch - timedelta(hours=5, minutes=30)
                                                search_date1 = punch.strftime("%Y-%m-%d")
                                                punch = punch.strftime("%Y-%m-%d %H:%M:%S")

                                                punch_time = datetime.strptime(punch, "%Y-%m-%d %H:%M:%S")
                                                punch_in_time = punch_time.strftime("%Y-%m-%d 00:00:00")
                                                punch_out_time = punch_time.strftime("%Y-%m-%d 23:59:59")

                                                cr.execute("delete from hr_attendance where search_date = '" + str(search_date1) + "' and employee_id = '" + str(
                                                    emp.id) + "' and method = 'Auto'")


                                                min_id = att_obj.create(cr, uid, {'month': str(month),
                                                                                  'year_id': year_id and year_id[
                                                                                      0] or False, 'day': each.name,
                                                                                  'search_date': search_date1,
                                                                                  'name': punch, 'employee_id': emp.id,
                                                                                  'company_id': emp.company_id and emp.company_id.id or False,
                                                                                  'department_id': emp.department_id and emp.department_id.id or False,
                                                                                  'method': 'Auto'})

                                                print "=========================NEW INDIVISIBLE MINIMUM RECORD IS CREATED===========================", min_id, count, each.name,tm_tuple,year

                                        if result[0] and result[0][1] != None:
                                            if len(result[0]) > 1 and result[0][1] != None:
                                                punch = datetime.strptime(result[0][1], "%Y-%m-%d %H:%M:%S")
                                                to_delete_punch = result[0][1]
                                                punch = punch + timedelta(hours=5, minutes=30)
                                                shift_timing = datetime.strptime(timing['end_time'],"%Y-%m-%d %H:%M:%S")

                                                print"===============", punch, shift_timing
                                                if punch > shift_timing:
                                                    temp_punch = shift_timing
                                                    temp = random.randrange(0, 10)
                                                    punch = temp_punch + timedelta(hours=0, minutes=temp)

                                                elif punch <= shift_timing:
                                                    punch = punch + timedelta(hours=0, minutes=0)

                                                punch = punch - timedelta(hours=5, minutes=30)
                                                search_date2 = punch.strftime("%Y-%m-%d")
                                                punch = punch.strftime("%Y-%m-%d %H:%M:%S")

                                                #                                                cr.execute("delete from hr_attendance where search_date = '"+str(search_date2)+"' and employee_id = '"+str(emp.id)+"' and method = 'Auto'")

                                                max_id = att_obj.create(cr, uid, {'month': str(month),
                                                                                  'year_id': year_id and year_id[
                                                                                      0] or False, 'day': each.name,
                                                                                  'search_date': search_date1,
                                                                                  'name': punch, 'employee_id': emp.id,
                                                                                  'company_id': emp.company_id and emp.company_id.id or False,
                                                                                  'department_id': emp.department_id and emp.department_id.id or False,
                                                                                  'method': 'Auto'})

                                                print "=========================NEW INDIVISIBLE MAXIMUM RECORD IS CREATED===========================", max_id, count, each.name

                    else:
                        raise osv.except_osv(_('Warning !'), _(
                            "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                emp.sinid)))

            else:
                if each.name and each.end_date and each.employee_id:
                    count = 0
                    shift_data = []
                    start_date = datetime.strptime(each.name, '%Y-%m-%d')
                    end_date = datetime.strptime(each.end_date, '%Y-%m-%d')
                    end_tm_tuple = datetime.strptime(each.end_date, '%Y-%m-%d').timetuple()
                    while (start_date <= end_date):
                        date1 = start_date.strftime('%Y-%m-%d')
                        tm_tuple = datetime.strptime(date1, '%Y-%m-%d').timetuple()
                        if tm_tuple.tm_mon != int(end_tm_tuple.tm_mon):
                            break
                        if tm_tuple.tm_year != int(end_tm_tuple.tm_year):
                            break
                        for emp in emp_ids:
                            count += 1
                            prev_shift_ids = shift_obj.search(cr, uid,
                                                              [('employee_id', '=', emp.id), ('name', '<=', date1)],
                                                              limit=1, order='name DESC')
                            next_shift_ids = shift_obj.search(cr, uid,
                                                              [('employee_id', '=', emp.id), ('name', '>', date1)],
                                                              limit=1, order='name ASC')
                            if prev_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                            elif next_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                            else:
                                raise osv.except_osv(_('Warning !'), _(
                                    "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                        emp.sinid)))
                            if shift_data:
                                for line in shift_data.shift_id.shift_line:
                                    timing = self.calculate_time(cr, uid, ids, date1, line.from_time, line.to_time)
                                    query = "select min(raw.name) , max(raw.name) from raw_attendance as raw left join hr_employee as hr on (raw.employee_id=hr.id) where raw.name + interval '5 hours 30 minute' > \
                                                to_timestamp('" + str(timing['start_time']) + "','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                                                and raw.name + interval '5 hours 30 minute' <= '" + str(
                                        timing['final_time']) + "' and raw.employee_id = '" + str(
                                        emp.id) + "' and hr.doj <= '" + str(date1) + "' "
                                    cr.execute(query)
                                    result = cr.fetchall()
                                    tm_tuple = datetime.strptime(date1, '%Y-%m-%d').timetuple()
                                    month = tm_tuple.tm_mon
                                    year = tm_tuple.tm_year
                                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name', '=', year)])
                                    raw_in_punch = raw_out_punch = in_punch = out_punch = False
                                    if result and len(result[0]) > 0 and result[0][0] != None:
                                        raw_in_punch = datetime.strptime(result[0][0], "%Y-%m-%d %H:%M:%S")
                                    if result and len(result[0]) > 1 and result[0][1] != None:
                                        raw_out_punch = datetime.strptime(result[0][1], "%Y-%m-%d %H:%M:%S")

                                    if raw_in_punch and raw_out_punch and raw_in_punch == raw_out_punch:
                                        continue
                                    if result:
                                        if result[0][0] and result[0][1]:
                                            punch_min = datetime.strptime(result[0][0], "%Y-%m-%d %H:%M:%S")
                                            punch_max = datetime.strptime(result[0][1], "%Y-%m-%d %H:%M:%S")
                                            punch_diff = punch_max - punch_min
                                            punch_diff = str(punch_diff)
                                            punch_diff = punch_diff.split(':')
                                            punch_diff = float(punch_diff[0] + '.' + punch_diff[1])
                                            if punch_diff >= 0.15:
                                                if result[0] and result[0][0] != None:
                                                    if len(result[0]) > 0 and result[0][0] != None:
                                                        punch = datetime.strptime(result[0][0], "%Y-%m-%d %H:%M:%S")
                                                        actual = datetime.strptime(str(timing['start_time']),
                                                                                   "%Y-%m-%d %H:%M:%S")
                                                        to_delete_actual = timing['start_time']
                                                        punch = punch + timedelta(hours=5, minutes=30)
                                                        old_punch = result[0][0]
                                                        punch_tuple = punch.timetuple()
                                                        year = punch_tuple.tm_year
                                                        mon = punch_tuple.tm_mon
                                                        day = punch_tuple.tm_mday
                                                        #                                                        val1 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'07:45:00'
                                                        #                                                        val1 = datetime.strptime(val1,'%Y-%m-%d %H:%M:%S')
                                                        #                                                        val2 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'08:40:00'
                                                        #                                                        val2 = datetime.strptime(val2,'%Y-%m-%d %H:%M:%S')
                                                        #                                                        val3 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'09:08:00'
                                                        #                                                        val3 = datetime.strptime(val3,'%Y-%m-%d %H:%M:%S')
                                                        #                                                        val4 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'10:00:00'
                                                        #                                                        val4 = datetime.strptime(val4,'%Y-%m-%d %H:%M:%S')
                                                        #                                                        val5 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'11:00:00'
                                                        #                                                        val5 = datetime.strptime(val5,'%Y-%m-%d %H:%M:%S')
                                                        #                                                        val6 = str(year) +'-'+str(mon)+'-'+str(day) +' ' +'12:00:00'
                                                        #                                                        val6 = datetime.strptime(val6,'%Y-%m-%d %H:%M:%S')

                                                        start_time = datetime.strptime(str(timing['start_time']),
                                                                                       "%Y-%m-%d %H:%M:%S")
                                                        print"============", punch, start_time
                                                        if punch < start_time:
                                                            start_time = start_time - timedelta(hours=0, minutes=10)
                                                            print'SSSSSSSSSSS',start_time
                                                            temp_punch = start_time
                                                            temp = random.randrange(0, 10)
                                                            punch = temp_punch + timedelta(hours=0, minutes=temp)

                                                        elif punch >= start_time:
                                                            punch = punch + timedelta(hours=0, minutes=0)
                                                        # if punch > val1 and punch <= val2:
                                                        #                                                            temp_punch = str(year) +'-'+str(mon)+'-'+str(day) +' '+'08:45:00'
                                                        #                                                            temp_punch = datetime.strptime(temp_punch,'%Y-%m-%d %H:%M:%S')
                                                        #                                                            temp = random.randrange(1,30)
                                                        #                                                            punch = temp_punch + timedelta(hours=0,minutes=temp)
                                                        #                                                        elif punch > val2 and punch <= val3:
                                                        #                                                            temp_punch = str(year) +'-'+str(mon)+'-'+str(day) +' '+'09:09:00'
                                                        #                                                            temp_punch = datetime.strptime(temp_punch,'%Y-%m-%d %H:%M:%S')
                                                        #                                                            temp = random.randrange(0,6)
                                                        #                                                            punch = temp_punch + timedelta(hours=0,minutes=temp)
                                                        #                                                        elif punch > val3 and punch <= val4:
                                                        #                                                            punch = punch
                                                        #                                                        elif punch > val4 and punch <= val5:
                                                        #                                                            temp_punch = str(year) +'-'+str(mon)+'-'+str(day) +' '+'09:15:00'
                                                        #                                                            temp_punch = datetime.strptime(temp_punch,'%Y-%m-%d %H:%M:%S')
                                                        #                                                            temp = random.randrange(0,15)
                                                        #                                                            punch = temp_punch + timedelta(hours=0,minutes=temp)
                                                        #                                                        elif punch > val5 and punch <= val6:
                                                        #                                                            temp_punch = str(year) +'-'+str(mon)+'-'+str(day) +' '+'09:30:00'
                                                        #                                                            temp_punch = datetime.strptime(temp_punch,'%Y-%m-%d %H:%M:%S')
                                                        #                                                            temp = random.randrange(0,30)
                                                        #                                                            punch = temp_punch + timedelta(hours=0,minutes=temp)
                                                        #
                                                        #                                                        else:
                                                        #                                                            continue

                                                        punch = punch - timedelta(hours=5, minutes=30)
                                                        search_date1 = punch.strftime("%Y-%m-%d")
                                                        punch = punch.strftime("%Y-%m-%d %H:%M:%S")
                                                        punch_time = datetime.strptime(punch, "%Y-%m-%d %H:%M:%S")
                                                        punch_in_time = punch_time.strftime("%Y-%m-%d 00:00:00")
                                                        punch_out_time = punch_time.strftime("%Y-%m-%d 23:59:59")

                                                        cr.execute(
                                                            "delete from hr_attendance where search_date = '" + str(
                                                                search_date1) + "' and employee_id = '" + str(
                                                                emp.id) + "' and method = 'Auto'")

                                                        min_id = att_obj.create(cr, uid, {'month': str(month),
                                                                                          'year_id': year_id and
                                                                                                     year_id[
                                                                                                         0] or False,
                                                                                          'day': date1,
                                                                                          'search_date': search_date1,
                                                                                          'name': punch,
                                                                                          'employee_id': emp.id,
                                                                                          'company_id': emp.company_id and emp.company_id.id or False,
                                                                                          'department_id': emp.department_id and emp.department_id.id or False,
                                                                                          'method': 'Auto'})

                                                        print "=========================NEW INDIVISIBLE MINIMUM RECORD IS CREATED===========================", min_id, count, date1

                                                if result[0] and result[0][1] != None:
                                                    if len(result[0]) > 1 and result[0][1] != None:
                                                        punch = datetime.strptime(result[0][1], "%Y-%m-%d %H:%M:%S")
                                                        to_delete_punch = result[0][1]
                                                        punch = punch + timedelta(hours=5, minutes=30)
                                                        shift_timing = datetime.strptime(timing['end_time'],
                                                                                         "%Y-%m-%d %H:%M:%S")
                                                        print"===============",punch,shift_timing
                                                        if punch > shift_timing:
                                                            temp_punch=shift_timing
                                                            temp = random.randrange(0, 10)
                                                            punch = temp_punch + timedelta(hours=0, minutes=temp)

                                                        elif punch <= shift_timing:
                                                            punch = punch + timedelta(hours=0, minutes=0)


                                                        # ot_time = punch - shift_timing
                                                        #ot_min = ot_time.seconds/60
                                                        #total_ot_min = ot_min/4           # This is for reducing the OT, 4 times
                                                        #if total_ot_min <= 120 :
                                                        #final_ot_hr = total_ot_min/60
                                                        #final_ot_min = total_ot_min%60
                                                        #punch = shift_timing + timedelta(hours=final_ot_hr,minutes=final_ot_min)
                                                        #else :
                                                        #final_ot_hr = 2
                                                        #final_ot_min = 0
                                                        #punch = shift_timing + timedelta(hours=final_ot_hr,minutes=final_ot_min)

                                                        punch = punch - timedelta(hours=5, minutes=30)
                                                        search_date2 = punch.strftime("%Y-%m-%d")
                                                        punch = punch.strftime("%Y-%m-%d %H:%M:%S")

                                                        #                                                        cr.execute("delete from hr_attendance where search_date = '"+str(search_date2)+"' and employee_id = '"+str(emp.id)+"' and method = 'Auto'")
                                                        max_id = att_obj.create(cr, uid, {'month': str(month),
                                                                                          'year_id': year_id and
                                                                                                     year_id[
                                                                                                         0] or False,
                                                                                          'day': date1,
                                                                                          'search_date': search_date1,
                                                                                          'name': punch,
                                                                                          'employee_id': emp.id,
                                                                                          'company_id': emp.company_id and emp.company_id.id or False,
                                                                                          'department_id': emp.department_id and emp.department_id.id or False,
                                                                                          'method': 'Auto', })

                                                        print "=========================NEW INDIVISIBLE MAXIMUM RECORD IS CREATED===========================", max_id, count, date1

                            else:
                                raise osv.except_osv(_('Warning !'), _(
                                    "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                        emp.sinid)))
                        start_date += timedelta(days=1)

        return True
    
    def run_synchro1(self, cr, uid, ids, context=None):
        self.run_synchro(cr,uid, ids, context=context)
#        self.run_synchro_attendance(cr,uid, ids, context=context)        
        return True

    def run_synchro11(self, cr, uid, ids, context=None):
        self.run_synch(cr, uid, ids, context=context)
        return True


    def run_synchro2(self, cr, uid, ids, context=None):
        self.pool.get('attendance.timing').run_synchro_timing(cr, uid, ids, context=context)               
        return True
    
    def run_synchro_att(self, cr, uid, ids, context=None):
        self.run_synchro_comp(cr,uid, ids, context=context)
        return True
    
    def run_synchro_punch(self, cr, uid, ids, context=None):
        self.pool.get('attendance.timing').run_synchro_timing_comp(cr, uid, ids, context=context)               
        return True
    
    def run_synchro22(self, cr, uid, ids, context=None):
        self.pool.get('attendance.timing').run_synchro_timing11(cr, uid, ids, context=context)               
        return True
    
    def run_invalid_punch(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        shift_obj = self.pool.get('hr.shift.line')
        emp_dict = {}
        emp_dict0 = {}
        emp_dict1 = {}
        emp_dict2 = {}
        Punch = None
        count = 0
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            if each.employee_id and each.department_id and each.type:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True),('type','=',each.type)])
            elif each.employee_id and each.type:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('type','=',each.type)])
            elif each.department_id and each.type:
                list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True),('type','=',each.type)])
            elif each.type:
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('type','=',each.type)])
            elif each.employee_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True)])
            elif each.department_id:
                list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True)])
            else:
                list_ids = emp_obj.search(cr, uid, [('active','=',True)])
            
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            year = tm_tuple.tm_year  
            tm_day = tm_tuple.tm_mday
                
            emp_ids = emp_obj.browse(cr, uid, list_ids)
            for emp in emp_ids:
                date1 = datetime.strptime(str(year)+'-'+str(month)+'-'+'01','%Y-%m-%d')
                for i in range(tm_day):
                    date2 = date1.strftime('%Y-%m-%d')
                    tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                    if tm_tuple.tm_mon != month:
                        break
                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',date2)], limit=1, order='name DESC')
                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',date2)], limit=1, order='name ASC')
                    if prev_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    elif next_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    else:
                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    if shift_data:
                        for line in shift_data.shift_id.shift_line:
                            timing = self.calculate_time(cr, uid, ids, date2, line.from_time, line.to_time)
                            qry0 = "select min(name) , max(name) from raw_attendance where name + interval '5 hours 30 minute' > \
                            to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp - interval '1 hours 30 minute' \
                            and name + interval '5 hours 30 minute' < '"+str(timing['final_time'])+"' and employee_id = '"+str(emp.id)+"'"
                            
                            raw_in_punch = raw_out_punch = False
                            cr.execute(qry0)
                            result = cr.fetchall()
                            if result and len(result[0])>0 and result[0][0] != None:
                                raw_in_punch = datetime.strptime(result[0][0],"%Y-%m-%d %H:%M:%S")
                                
                            if result and len(result[0])>1 and result[0][1] != None:
                                raw_out_punch = datetime.strptime(result[0][1],"%Y-%m-%d %H:%M:%S")
                                
                            if raw_in_punch and raw_out_punch and raw_in_punch == raw_out_punch:
                                Punch = '1 PUNCH'
                                if emp_dict0.has_key(str(emp.id)):
                                    if tm_tuple.tm_mday == 1:
                                        emp_dict0[str(emp.id)]['1'] = date2
                                    elif tm_tuple.tm_mday == 2:
                                        emp_dict0[str(emp.id)]['2'] = date2
                                    elif tm_tuple.tm_mday == 3:
                                        emp_dict0[str(emp.id)]['3'] = date2
                                    elif tm_tuple.tm_mday == 4:
                                        emp_dict0[str(emp.id)]['4'] = date2
                                    elif tm_tuple.tm_mday == 5:
                                        emp_dict0[str(emp.id)]['5'] = date2
                                    elif tm_tuple.tm_mday == 6:
                                        emp_dict0[str(emp.id)]['6'] = date2
                                    elif tm_tuple.tm_mday == 7:
                                        emp_dict0[str(emp.id)]['7'] = date2
                                    elif tm_tuple.tm_mday == 8:
                                        emp_dict0[str(emp.id)]['8'] = date2
                                    elif tm_tuple.tm_mday == 9:
                                        emp_dict0[str(emp.id)]['9'] = date2
                                    elif tm_tuple.tm_mday == 10:
                                        emp_dict0[str(emp.id)]['10'] = date2
                                    elif tm_tuple.tm_mday == 11:
                                        emp_dict0[str(emp.id)]['11'] = date2
                                    elif tm_tuple.tm_mday == 12:
                                        emp_dict0[str(emp.id)]['12'] = date2
                                    elif tm_tuple.tm_mday == 13:
                                        emp_dict0[str(emp.id)]['13'] = date2
                                    elif tm_tuple.tm_mday == 14:
                                        emp_dict0[str(emp.id)]['14'] = date2
                                    elif tm_tuple.tm_mday == 15:
                                        emp_dict0[str(emp.id)]['15'] = date2
                                    elif tm_tuple.tm_mday == 16:
                                        emp_dict0[str(emp.id)]['16'] = date2
                                    elif tm_tuple.tm_mday == 17:
                                        emp_dict0[str(emp.id)]['17'] = date2
                                    elif tm_tuple.tm_mday == 18:
                                        emp_dict0[str(emp.id)]['18'] = date2
                                    elif tm_tuple.tm_mday == 19:
                                        emp_dict0[str(emp.id)]['19'] = date2
                                    elif tm_tuple.tm_mday == 20:
                                        emp_dict0[str(emp.id)]['20'] = date2
                                    elif tm_tuple.tm_mday == 21:
                                        emp_dict0[str(emp.id)]['21'] = date2
                                    elif tm_tuple.tm_mday == 22:
                                        emp_dict0[str(emp.id)]['22'] = date2
                                    elif tm_tuple.tm_mday == 23:
                                        emp_dict0[str(emp.id)]['23'] = date2
                                    elif tm_tuple.tm_mday == 24:
                                        emp_dict0[str(emp.id)]['24'] = date2
                                    elif tm_tuple.tm_mday == 25:
                                        emp_dict0[str(emp.id)]['25'] = date2
                                    elif tm_tuple.tm_mday == 26:
                                        emp_dict0[str(emp.id)]['26'] = date2
                                    elif tm_tuple.tm_mday == 27:
                                        emp_dict0[str(emp.id)]['27'] = date2
                                    elif tm_tuple.tm_mday == 28:
                                        emp_dict0[str(emp.id)]['28'] = date2
                                    elif tm_tuple.tm_mday == 29:
                                        emp_dict0[str(emp.id)]['29'] = date2
                                    elif tm_tuple.tm_mday == 30:
                                        emp_dict0[str(emp.id)]['30'] = date2
                                    elif tm_tuple.tm_mday == 31:
                                        emp_dict0[str(emp.id)]['31'] = date2
                                    else:
                                        pass
                                    
                                else:
                                    emp_dict0[str(emp.id)] = {'Pcard':emp.sinid,'name':emp.name,'reporting':emp.parent_id and emp.parent_id.name or False,
                                        '1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None,'10':None,
                                        '11':None,'12':None,'13':None,'14':None,'15':None,'16':None,'17':None,'18':None,'19':None,'20':None,
                                        '21':None,'22':None,'23':None,'24':None,'25':None,'26':None,'27':None,'28':None,'29':None,'30':None,'31':None,}
                                        
                                    if tm_tuple.tm_mday == 1:
                                        emp_dict0[str(emp.id)]['1'] = date2
                                    elif tm_tuple.tm_mday == 2:
                                        emp_dict0[str(emp.id)]['2'] = date2
                                    elif tm_tuple.tm_mday == 3:
                                        emp_dict0[str(emp.id)]['3'] = date2
                                    elif tm_tuple.tm_mday == 4:
                                        emp_dict0[str(emp.id)]['4'] = date2
                                    elif tm_tuple.tm_mday == 5:
                                        emp_dict0[str(emp.id)]['5'] = date2
                                    elif tm_tuple.tm_mday == 6:
                                        emp_dict0[str(emp.id)]['6'] = date2
                                    elif tm_tuple.tm_mday == 7:
                                        emp_dict0[str(emp.id)]['7'] = date2
                                    elif tm_tuple.tm_mday == 8:
                                        emp_dict0[str(emp.id)]['8'] = date2
                                    elif tm_tuple.tm_mday == 9:
                                        emp_dict0[str(emp.id)]['9'] = date2
                                    elif tm_tuple.tm_mday == 10:
                                        emp_dict0[str(emp.id)]['10'] = date2
                                    elif tm_tuple.tm_mday == 11:
                                        emp_dict0[str(emp.id)]['11'] = date2
                                    elif tm_tuple.tm_mday == 12:
                                        emp_dict0[str(emp.id)]['12'] = date2
                                    elif tm_tuple.tm_mday == 13:
                                        emp_dict0[str(emp.id)]['13'] = date2
                                    elif tm_tuple.tm_mday == 14:
                                        emp_dict0[str(emp.id)]['14'] = date2
                                    elif tm_tuple.tm_mday == 15:
                                        emp_dict0[str(emp.id)]['15'] = date2
                                    elif tm_tuple.tm_mday == 16:
                                        emp_dict0[str(emp.id)]['16'] = date2
                                    elif tm_tuple.tm_mday == 17:
                                        emp_dict0[str(emp.id)]['17'] = date2
                                    elif tm_tuple.tm_mday == 18:
                                        emp_dict0[str(emp.id)]['18'] = date2
                                    elif tm_tuple.tm_mday == 19:
                                        emp_dict0[str(emp.id)]['19'] = date2
                                    elif tm_tuple.tm_mday == 20:
                                        emp_dict0[str(emp.id)]['20'] = date2
                                    elif tm_tuple.tm_mday == 21:
                                        emp_dict0[str(emp.id)]['21'] = date2
                                    elif tm_tuple.tm_mday == 22:
                                        emp_dict0[str(emp.id)]['22'] = date2
                                    elif tm_tuple.tm_mday == 23:
                                        emp_dict0[str(emp.id)]['23'] = date2
                                    elif tm_tuple.tm_mday == 24:
                                        emp_dict0[str(emp.id)]['24'] = date2
                                    elif tm_tuple.tm_mday == 25:
                                        emp_dict0[str(emp.id)]['25'] = date2
                                    elif tm_tuple.tm_mday == 26:
                                        emp_dict0[str(emp.id)]['26'] = date2
                                    elif tm_tuple.tm_mday == 27:
                                        emp_dict0[str(emp.id)]['27'] = date2
                                    elif tm_tuple.tm_mday == 28:
                                        emp_dict0[str(emp.id)]['28'] = date2
                                    elif tm_tuple.tm_mday == 29:
                                        emp_dict0[str(emp.id)]['29'] = date2
                                    elif tm_tuple.tm_mday == 30:
                                        emp_dict0[str(emp.id)]['30'] = date2
                                    elif tm_tuple.tm_mday == 31:
                                        emp_dict0[str(emp.id)]['31'] = date2
                                    else:
                                        pass
                            
                            qry = "select emp.sinid from hr_attendance as hr left join hr_employee as emp "\
                            "on (hr.employee_id=emp.id) left join resource_resource as res on (emp.resource_id=res.id) "\
                            "where hr.name + interval '5 hours 30 minute' > "\
                            "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                            "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                            "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                            "hr.day = '"+str(date2)+"' and emp.id = '"+str(emp.id)+"' group by emp.sinid having count(hr.id) = 3"
                            
                            cr.execute(qry)
                            temp = cr.fetchall()
                            for miss in temp:
                                if miss and len(miss) > 0 and miss[0] != None:
                                    Punch = '3 PUNCH'
                                    if emp_dict.has_key(str(miss[0])):
                                        if tm_tuple.tm_mday == 1:
                                            emp_dict[str(miss[0])]['1'] = date2
                                        elif tm_tuple.tm_mday == 2:
                                            emp_dict[str(miss[0])]['2'] = date2
                                        elif tm_tuple.tm_mday == 3:
                                            emp_dict[str(miss[0])]['3'] = date2
                                        elif tm_tuple.tm_mday == 4:
                                            emp_dict[str(miss[0])]['4'] = date2
                                        elif tm_tuple.tm_mday == 5:
                                            emp_dict[str(miss[0])]['5'] = date2
                                        elif tm_tuple.tm_mday == 6:
                                            emp_dict[str(miss[0])]['6'] = date2
                                        elif tm_tuple.tm_mday == 7:
                                            emp_dict[str(miss[0])]['7'] = date2
                                        elif tm_tuple.tm_mday == 8:
                                            emp_dict[str(miss[0])]['8'] = date2
                                        elif tm_tuple.tm_mday == 9:
                                            emp_dict[str(miss[0])]['9'] = date2
                                        elif tm_tuple.tm_mday == 10:
                                            emp_dict[str(miss[0])]['10'] = date2
                                        elif tm_tuple.tm_mday == 11:
                                            emp_dict[str(miss[0])]['11'] = date2
                                        elif tm_tuple.tm_mday == 12:
                                            emp_dict[str(miss[0])]['12'] = date2
                                        elif tm_tuple.tm_mday == 13:
                                            emp_dict[str(miss[0])]['13'] = date2
                                        elif tm_tuple.tm_mday == 14:
                                            emp_dict[str(miss[0])]['14'] = date2
                                        elif tm_tuple.tm_mday == 15:
                                            emp_dict[str(miss[0])]['15'] = date2
                                        elif tm_tuple.tm_mday == 16:
                                            emp_dict[str(miss[0])]['16'] = date2
                                        elif tm_tuple.tm_mday == 17:
                                            emp_dict[str(miss[0])]['17'] = date2
                                        elif tm_tuple.tm_mday == 18:
                                            emp_dict[str(miss[0])]['18'] = date2
                                        elif tm_tuple.tm_mday == 19:
                                            emp_dict[str(miss[0])]['19'] = date2
                                        elif tm_tuple.tm_mday == 20:
                                            emp_dict[str(miss[0])]['20'] = date2
                                        elif tm_tuple.tm_mday == 21:
                                            emp_dict[str(miss[0])]['21'] = date2
                                        elif tm_tuple.tm_mday == 22:
                                            emp_dict[str(miss[0])]['22'] = date2
                                        elif tm_tuple.tm_mday == 23:
                                            emp_dict[str(miss[0])]['23'] = date2
                                        elif tm_tuple.tm_mday == 24:
                                            emp_dict[str(miss[0])]['24'] = date2
                                        elif tm_tuple.tm_mday == 25:
                                            emp_dict[str(miss[0])]['25'] = date2
                                        elif tm_tuple.tm_mday == 26:
                                            emp_dict[str(miss[0])]['26'] = date2
                                        elif tm_tuple.tm_mday == 27:
                                            emp_dict[str(miss[0])]['27'] = date2
                                        elif tm_tuple.tm_mday == 28:
                                            emp_dict[str(miss[0])]['28'] = date2
                                        elif tm_tuple.tm_mday == 29:
                                            emp_dict[str(miss[0])]['29'] = date2
                                        elif tm_tuple.tm_mday == 30:
                                            emp_dict[str(miss[0])]['30'] = date2
                                        elif tm_tuple.tm_mday == 31:
                                            emp_dict[str(miss[0])]['31'] = date2
                                        else:
                                            pass
                                    else:
                                        emp_dict[str(miss[0])] = {'Pcard':miss[0],'name':emp.name,'reporting':emp.parent_id and emp.parent_id.name or False,
                                        '1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None,'10':None,
                                        '11':None,'12':None,'13':None,'14':None,'15':None,'16':None,'17':None,'18':None,'19':None,'20':None,
                                        '21':None,'22':None,'23':None,'24':None,'25':None,'26':None,'27':None,'28':None,'29':None,'30':None,'31':None,}
                                        
                                        if tm_tuple.tm_mday == 1:
                                            emp_dict[str(miss[0])]['1'] = date2
                                        elif tm_tuple.tm_mday == 2:
                                            emp_dict[str(miss[0])]['2'] = date2
                                        elif tm_tuple.tm_mday == 3:
                                            emp_dict[str(miss[0])]['3'] = date2
                                        elif tm_tuple.tm_mday == 4:
                                            emp_dict[str(miss[0])]['4'] = date2
                                        elif tm_tuple.tm_mday == 5:
                                            emp_dict[str(miss[0])]['5'] = date2
                                        elif tm_tuple.tm_mday == 6:
                                            emp_dict[str(miss[0])]['6'] = date2
                                        elif tm_tuple.tm_mday == 7:
                                            emp_dict[str(miss[0])]['7'] = date2
                                        elif tm_tuple.tm_mday == 8:
                                            emp_dict[str(miss[0])]['8'] = date2
                                        elif tm_tuple.tm_mday == 9:
                                            emp_dict[str(miss[0])]['9'] = date2
                                        elif tm_tuple.tm_mday == 10:
                                            emp_dict[str(miss[0])]['10'] = date2
                                        elif tm_tuple.tm_mday == 11:
                                            emp_dict[str(miss[0])]['11'] = date2
                                        elif tm_tuple.tm_mday == 12:
                                            emp_dict[str(miss[0])]['12'] = date2
                                        elif tm_tuple.tm_mday == 13:
                                            emp_dict[str(miss[0])]['13'] = date2
                                        elif tm_tuple.tm_mday == 14:
                                            emp_dict[str(miss[0])]['14'] = date2
                                        elif tm_tuple.tm_mday == 15:
                                            emp_dict[str(miss[0])]['15'] = date2
                                        elif tm_tuple.tm_mday == 16:
                                            emp_dict[str(miss[0])]['16'] = date2
                                        elif tm_tuple.tm_mday == 17:
                                            emp_dict[str(miss[0])]['17'] = date2
                                        elif tm_tuple.tm_mday == 18:
                                            emp_dict[str(miss[0])]['18'] = date2
                                        elif tm_tuple.tm_mday == 19:
                                            emp_dict[str(miss[0])]['19'] = date2
                                        elif tm_tuple.tm_mday == 20:
                                            emp_dict[str(miss[0])]['20'] = date2
                                        elif tm_tuple.tm_mday == 21:
                                            emp_dict[str(miss[0])]['21'] = date2
                                        elif tm_tuple.tm_mday == 22:
                                            emp_dict[str(miss[0])]['22'] = date2
                                        elif tm_tuple.tm_mday == 23:
                                            emp_dict[str(miss[0])]['23'] = date2
                                        elif tm_tuple.tm_mday == 24:
                                            emp_dict[str(miss[0])]['24'] = date2
                                        elif tm_tuple.tm_mday == 25:
                                            emp_dict[str(miss[0])]['25'] = date2
                                        elif tm_tuple.tm_mday == 26:
                                            emp_dict[str(miss[0])]['26'] = date2
                                        elif tm_tuple.tm_mday == 27:
                                            emp_dict[str(miss[0])]['27'] = date2
                                        elif tm_tuple.tm_mday == 28:
                                            emp_dict[str(miss[0])]['28'] = date2
                                        elif tm_tuple.tm_mday == 29:
                                            emp_dict[str(miss[0])]['29'] = date2
                                        elif tm_tuple.tm_mday == 30:
                                            emp_dict[str(miss[0])]['30'] = date2
                                        elif tm_tuple.tm_mday == 31:
                                            emp_dict[str(miss[0])]['31'] = date2
                                        else:
                                            pass
                                        
                            
                            qry1 = "select emp.sinid from hr_attendance as hr left join hr_employee as emp "\
                            "on (hr.employee_id=emp.id) left join resource_resource as res on (emp.resource_id=res.id) "\
                            "where hr.name + interval '5 hours 30 minute' > "\
                            "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                            "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                            "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                            "hr.day = '"+str(date2)+"' and emp.id = '"+str(emp.id)+"' group by emp.sinid having count(hr.id) = 5"
                            
                            cr.execute(qry1)
                            temp1 = cr.fetchall()
                            for miss1 in temp1:
                                if miss1 and len(miss1) > 0 and miss1[0] != None:
                                    Punch = '5 PUNCH'
                                    if emp_dict1.has_key(str(miss1[0])):
                                        if tm_tuple.tm_mday == 1:
                                            emp_dict1[str(miss1[0])]['1'] = date2
                                        elif tm_tuple.tm_mday == 2:
                                            emp_dict1[str(miss1[0])]['2'] = date2
                                        elif tm_tuple.tm_mday == 3:
                                            emp_dict1[str(miss1[0])]['3'] = date2
                                        elif tm_tuple.tm_mday == 4:
                                            emp_dict1[str(miss1[0])]['4'] = date2
                                        elif tm_tuple.tm_mday == 5:
                                            emp_dict1[str(miss1[0])]['5'] = date2
                                        elif tm_tuple.tm_mday == 6:
                                            emp_dict1[str(miss1[0])]['6'] = date2
                                        elif tm_tuple.tm_mday == 7:
                                            emp_dict1[str(miss1[0])]['7'] = date2
                                        elif tm_tuple.tm_mday == 8:
                                            emp_dict1[str(miss1[0])]['8'] = date2
                                        elif tm_tuple.tm_mday == 9:
                                            emp_dict1[str(miss1[0])]['9'] = date2
                                        elif tm_tuple.tm_mday == 10:
                                            emp_dict1[str(miss1[0])]['10'] = date2
                                        elif tm_tuple.tm_mday == 11:
                                            emp_dict1[str(miss1[0])]['11'] = date2
                                        elif tm_tuple.tm_mday == 12:
                                            emp_dict1[str(miss1[0])]['12'] = date2
                                        elif tm_tuple.tm_mday == 13:
                                            emp_dict1[str(miss1[0])]['13'] = date2
                                        elif tm_tuple.tm_mday == 14:
                                            emp_dict1[str(miss1[0])]['14'] = date2
                                        elif tm_tuple.tm_mday == 15:
                                            emp_dict1[str(miss1[0])]['15'] = date2
                                        elif tm_tuple.tm_mday == 16:
                                            emp_dict1[str(miss1[0])]['16'] = date2
                                        elif tm_tuple.tm_mday == 17:
                                            emp_dict1[str(miss1[0])]['17'] = date2
                                        elif tm_tuple.tm_mday == 18:
                                            emp_dict1[str(miss1[0])]['18'] = date2
                                        elif tm_tuple.tm_mday == 19:
                                            emp_dict1[str(miss1[0])]['19'] = date2
                                        elif tm_tuple.tm_mday == 20:
                                            emp_dict1[str(miss1[0])]['20'] = date2
                                        elif tm_tuple.tm_mday == 21:
                                            emp_dict1[str(miss1[0])]['21'] = date2
                                        elif tm_tuple.tm_mday == 22:
                                            emp_dict1[str(miss1[0])]['22'] = date2
                                        elif tm_tuple.tm_mday == 23:
                                            emp_dict1[str(miss1[0])]['23'] = date2
                                        elif tm_tuple.tm_mday == 24:
                                            emp_dict1[str(miss1[0])]['24'] = date2
                                        elif tm_tuple.tm_mday == 25:
                                            emp_dict1[str(miss1[0])]['25'] = date2
                                        elif tm_tuple.tm_mday == 26:
                                            emp_dict1[str(miss1[0])]['26'] = date2
                                        elif tm_tuple.tm_mday == 27:
                                            emp_dict1[str(miss1[0])]['27'] = date2
                                        elif tm_tuple.tm_mday == 28:
                                            emp_dict1[str(miss1[0])]['28'] = date2
                                        elif tm_tuple.tm_mday == 29:
                                            emp_dict1[str(miss1[0])]['29'] = date2
                                        elif tm_tuple.tm_mday == 30:
                                            emp_dict1[str(miss1[0])]['30'] = date2
                                        elif tm_tuple.tm_mday == 31:
                                            emp_dict1[str(miss1[0])]['31'] = date2
                                        else:
                                            pass
                                    else:
                                        emp_dict1[str(miss1[0])] = {'Pcard':miss1[0],'name':emp.name,'reporting':emp.parent_id and emp.parent_id.name or False,
                                        '1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None,'10':None,
                                        '11':None,'12':None,'13':None,'14':None,'15':None,'16':None,'17':None,'18':None,'19':None,'20':None,
                                        '21':None,'22':None,'23':None,'24':None,'25':None,'26':None,'27':None,'28':None,'29':None,'30':None,'31':None,}
                                        
                                        if tm_tuple.tm_mday == 1:
                                            emp_dict1[str(miss1[0])]['1'] = date2
                                        elif tm_tuple.tm_mday == 2:
                                            emp_dict1[str(miss1[0])]['2'] = date2
                                        elif tm_tuple.tm_mday == 3:
                                            emp_dict1[str(miss1[0])]['3'] = date2
                                        elif tm_tuple.tm_mday == 4:
                                            emp_dict1[str(miss1[0])]['4'] = date2
                                        elif tm_tuple.tm_mday == 5:
                                            emp_dict1[str(miss1[0])]['5'] = date2
                                        elif tm_tuple.tm_mday == 6:
                                            emp_dict1[str(miss1[0])]['6'] = date2
                                        elif tm_tuple.tm_mday == 7:
                                            emp_dict1[str(miss1[0])]['7'] = date2
                                        elif tm_tuple.tm_mday == 8:
                                            emp_dict1[str(miss1[0])]['8'] = date2
                                        elif tm_tuple.tm_mday == 9:
                                            emp_dict1[str(miss1[0])]['9'] = date2
                                        elif tm_tuple.tm_mday == 10:
                                            emp_dict1[str(miss1[0])]['10'] = date2
                                        elif tm_tuple.tm_mday == 11:
                                            emp_dict1[str(miss1[0])]['11'] = date2
                                        elif tm_tuple.tm_mday == 12:
                                            emp_dict1[str(miss1[0])]['12'] = date2
                                        elif tm_tuple.tm_mday == 13:
                                            emp_dict1[str(miss1[0])]['13'] = date2
                                        elif tm_tuple.tm_mday == 14:
                                            emp_dict1[str(miss1[0])]['14'] = date2
                                        elif tm_tuple.tm_mday == 15:
                                            emp_dict1[str(miss1[0])]['15'] = date2
                                        elif tm_tuple.tm_mday == 16:
                                            emp_dict1[str(miss1[0])]['16'] = date2
                                        elif tm_tuple.tm_mday == 17:
                                            emp_dict1[str(miss1[0])]['17'] = date2
                                        elif tm_tuple.tm_mday == 18:
                                            emp_dict1[str(miss1[0])]['18'] = date2
                                        elif tm_tuple.tm_mday == 19:
                                            emp_dict1[str(miss1[0])]['19'] = date2
                                        elif tm_tuple.tm_mday == 20:
                                            emp_dict1[str(miss1[0])]['20'] = date2
                                        elif tm_tuple.tm_mday == 21:
                                            emp_dict1[str(miss1[0])]['21'] = date2
                                        elif tm_tuple.tm_mday == 22:
                                            emp_dict1[str(miss1[0])]['22'] = date2
                                        elif tm_tuple.tm_mday == 23:
                                            emp_dict1[str(miss1[0])]['23'] = date2
                                        elif tm_tuple.tm_mday == 24:
                                            emp_dict1[str(miss1[0])]['24'] = date2
                                        elif tm_tuple.tm_mday == 25:
                                            emp_dict1[str(miss1[0])]['25'] = date2
                                        elif tm_tuple.tm_mday == 26:
                                            emp_dict1[str(miss1[0])]['26'] = date2
                                        elif tm_tuple.tm_mday == 27:
                                            emp_dict1[str(miss1[0])]['27'] = date2
                                        elif tm_tuple.tm_mday == 28:
                                            emp_dict1[str(miss1[0])]['28'] = date2
                                        elif tm_tuple.tm_mday == 29:
                                            emp_dict1[str(miss1[0])]['29'] = date2
                                        elif tm_tuple.tm_mday == 30:
                                            emp_dict1[str(miss1[0])]['30'] = date2
                                        elif tm_tuple.tm_mday == 31:
                                            emp_dict1[str(miss1[0])]['31'] = date2
                                        else:
                                            pass
                                        
                                        
                            
                            qry2 = "select emp.sinid from hr_attendance as hr left join hr_employee as emp "\
                            "on (hr.employee_id=emp.id) left join resource_resource as res on (emp.resource_id=res.id) "\
                            "where hr.name + interval '5 hours 30 minute' > "\
                            "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                            "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                            "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                            "hr.day = '"+str(date2)+"' and emp.id = '"+str(emp.id)+"' group by emp.sinid having count(hr.id) = 7"
                            
                            cr.execute(qry2)
                            temp2 = cr.fetchall()
                            for miss2 in temp2:
                                if miss2 and len(miss2) > 0 and miss2[0] != None:
                                    Punch = '7 PUNCH'
                                    if emp_dict2.has_key(str(miss2[0])):
                                        if tm_tuple.tm_mday == 1:
                                            emp_dict2[str(miss2[0])]['1'] = date2
                                        elif tm_tuple.tm_mday == 2:
                                            emp_dict2[str(miss2[0])]['2'] = date2
                                        elif tm_tuple.tm_mday == 3:
                                            emp_dict2[str(miss2[0])]['3'] = date2
                                        elif tm_tuple.tm_mday == 4:
                                            emp_dict2[str(miss2[0])]['4'] = date2
                                        elif tm_tuple.tm_mday == 5:
                                            emp_dict2[str(miss2[0])]['5'] = date2
                                        elif tm_tuple.tm_mday == 6:
                                            emp_dict2[str(miss2[0])]['6'] = date2
                                        elif tm_tuple.tm_mday == 7:
                                            emp_dict2[str(miss2[0])]['7'] = date2
                                        elif tm_tuple.tm_mday == 8:
                                            emp_dict2[str(miss2[0])]['8'] = date2
                                        elif tm_tuple.tm_mday == 9:
                                            emp_dict2[str(miss2[0])]['9'] = date2
                                        elif tm_tuple.tm_mday == 10:
                                            emp_dict2[str(miss2[0])]['10'] = date2
                                        elif tm_tuple.tm_mday == 11:
                                            emp_dict2[str(miss2[0])]['11'] = date2
                                        elif tm_tuple.tm_mday == 12:
                                            emp_dict2[str(miss2[0])]['12'] = date2
                                        elif tm_tuple.tm_mday == 13:
                                            emp_dict2[str(miss2[0])]['13'] = date2
                                        elif tm_tuple.tm_mday == 14:
                                            emp_dict2[str(miss2[0])]['14'] = date2
                                        elif tm_tuple.tm_mday == 15:
                                            emp_dict2[str(miss2[0])]['15'] = date2
                                        elif tm_tuple.tm_mday == 16:
                                            emp_dict2[str(miss2[0])]['16'] = date2
                                        elif tm_tuple.tm_mday == 17:
                                            emp_dict2[str(miss2[0])]['17'] = date2
                                        elif tm_tuple.tm_mday == 18:
                                            emp_dict2[str(miss2[0])]['18'] = date2
                                        elif tm_tuple.tm_mday == 19:
                                            emp_dict2[str(miss2[0])]['19'] = date2
                                        elif tm_tuple.tm_mday == 20:
                                            emp_dict2[str(miss2[0])]['20'] = date2
                                        elif tm_tuple.tm_mday == 21:
                                            emp_dict2[str(miss2[0])]['21'] = date2
                                        elif tm_tuple.tm_mday == 22:
                                            emp_dict2[str(miss2[0])]['22'] = date2
                                        elif tm_tuple.tm_mday == 23:
                                            emp_dict2[str(miss2[0])]['23'] = date2
                                        elif tm_tuple.tm_mday == 24:
                                            emp_dict2[str(miss2[0])]['24'] = date2
                                        elif tm_tuple.tm_mday == 25:
                                            emp_dict2[str(miss2[0])]['25'] = date2
                                        elif tm_tuple.tm_mday == 26:
                                            emp_dict2[str(miss2[0])]['26'] = date2
                                        elif tm_tuple.tm_mday == 27:
                                            emp_dict2[str(miss2[0])]['27'] = date2
                                        elif tm_tuple.tm_mday == 28:
                                            emp_dict2[str(miss2[0])]['28'] = date2
                                        elif tm_tuple.tm_mday == 29:
                                            emp_dict2[str(miss2[0])]['29'] = date2
                                        elif tm_tuple.tm_mday == 30:
                                            emp_dict2[str(miss2[0])]['30'] = date2
                                        elif tm_tuple.tm_mday == 31:
                                            emp_dict2[str(miss2[0])]['31'] = date2
                                        else:
                                            pass
                                    else:
                                        emp_dict2[str(miss2[0])] = {'Pcard':miss2[0],'name':emp.name,'reporting':emp.parent_id and emp.parent_id.name or False,
                                        '1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None,'10':None,
                                        '11':None,'12':None,'13':None,'14':None,'15':None,'16':None,'17':None,'18':None,'19':None,'20':None,
                                        '21':None,'22':None,'23':None,'24':None,'25':None,'26':None,'27':None,'28':None,'29':None,'30':None,'31':None,}
                                        
                                        if tm_tuple.tm_mday == 1:
                                            emp_dict2[str(miss2[0])]['1'] = date2
                                        elif tm_tuple.tm_mday == 2:
                                            emp_dict2[str(miss2[0])]['2'] = date2
                                        elif tm_tuple.tm_mday == 3:
                                            emp_dict2[str(miss2[0])]['3'] = date2
                                        elif tm_tuple.tm_mday == 4:
                                            emp_dict2[str(miss2[0])]['4'] = date2
                                        elif tm_tuple.tm_mday == 5:
                                            emp_dict2[str(miss2[0])]['5'] = date2
                                        elif tm_tuple.tm_mday == 6:
                                            emp_dict2[str(miss2[0])]['6'] = date2
                                        elif tm_tuple.tm_mday == 7:
                                            emp_dict2[str(miss2[0])]['7'] = date2
                                        elif tm_tuple.tm_mday == 8:
                                            emp_dict2[str(miss2[0])]['8'] = date2
                                        elif tm_tuple.tm_mday == 9:
                                            emp_dict2[str(miss2[0])]['9'] = date2
                                        elif tm_tuple.tm_mday == 10:
                                            emp_dict2[str(miss2[0])]['10'] = date2
                                        elif tm_tuple.tm_mday == 11:
                                            emp_dict2[str(miss2[0])]['11'] = date2
                                        elif tm_tuple.tm_mday == 12:
                                            emp_dict2[str(miss2[0])]['12'] = date2
                                        elif tm_tuple.tm_mday == 13:
                                            emp_dict2[str(miss2[0])]['13'] = date2
                                        elif tm_tuple.tm_mday == 14:
                                            emp_dict2[str(miss2[0])]['14'] = date2
                                        elif tm_tuple.tm_mday == 15:
                                            emp_dict2[str(miss2[0])]['15'] = date2
                                        elif tm_tuple.tm_mday == 16:
                                            emp_dict2[str(miss2[0])]['16'] = date2
                                        elif tm_tuple.tm_mday == 17:
                                            emp_dict2[str(miss2[0])]['17'] = date2
                                        elif tm_tuple.tm_mday == 18:
                                            emp_dict2[str(miss2[0])]['18'] = date2
                                        elif tm_tuple.tm_mday == 19:
                                            emp_dict2[str(miss2[0])]['19'] = date2
                                        elif tm_tuple.tm_mday == 20:
                                            emp_dict2[str(miss2[0])]['20'] = date2
                                        elif tm_tuple.tm_mday == 21:
                                            emp_dict2[str(miss2[0])]['21'] = date2
                                        elif tm_tuple.tm_mday == 22:
                                            emp_dict2[str(miss2[0])]['22'] = date2
                                        elif tm_tuple.tm_mday == 23:
                                            emp_dict2[str(miss2[0])]['23'] = date2
                                        elif tm_tuple.tm_mday == 24:
                                            emp_dict2[str(miss2[0])]['24'] = date2
                                        elif tm_tuple.tm_mday == 25:
                                            emp_dict2[str(miss2[0])]['25'] = date2
                                        elif tm_tuple.tm_mday == 26:
                                            emp_dict2[str(miss2[0])]['26'] = date2
                                        elif tm_tuple.tm_mday == 27:
                                            emp_dict2[str(miss2[0])]['27'] = date2
                                        elif tm_tuple.tm_mday == 28:
                                            emp_dict2[str(miss2[0])]['28'] = date2
                                        elif tm_tuple.tm_mday == 29:
                                            emp_dict2[str(miss2[0])]['29'] = date2
                                        elif tm_tuple.tm_mday == 30:
                                            emp_dict2[str(miss2[0])]['30'] = date2
                                        elif tm_tuple.tm_mday == 31:
                                            emp_dict2[str(miss2[0])]['31'] = date2
                                        else:
                                            pass
                                        
                    date1 += timedelta(days=1)
                    print "<----------------------------COUNTER------------------>",date1
                count += 1
                print "<----------------------------COUNTER------------------>",emp.sinid,count,Punch
              
        myfile0 = open('/tmp/invalid_1_punch.csv','wb')
        punchwriter0 = csv.writer(myfile0, delimiter=',', quotechar='"')
        for key,data in emp_dict0.iteritems():
            row = [data['Pcard'],data['name'],data['reporting'],data['1'],data['2'],data['3'],data['4'],data['5'],data['6'],data['7'],data['8'],data['9'],data['10'],data['11'],data['12'],data['13'],data['14'],data['15'],data['16'],data['17'],data['18'],data['19'],data['20'],data['21'],data['22'],data['23'],data['24'],data['25'],data['26'],data['27'],data['28'],data['29'],data['30'],data['31'],]
    
            punchwriter0.writerow(row)
        myfile0.close()
                
        myfile = open('/tmp/invalid_3_punch.csv','wb')
        punchwriter = csv.writer(myfile, delimiter=',', quotechar='"')
        for key,data in emp_dict.iteritems():
            row = [data['Pcard'],data['name'],data['reporting'],data['1'],data['2'],data['3'],data['4'],data['5'],data['6'],data['7'],data['8'],data['9'],data['10'],data['11'],data['12'],data['13'],data['14'],data['15'],data['16'],data['17'],data['18'],data['19'],data['20'],data['21'],data['22'],data['23'],data['24'],data['25'],data['26'],data['27'],data['28'],data['29'],data['30'],data['31'],]
    
            punchwriter.writerow(row)
        myfile.close()
        
        myfile1 = open('/tmp/invalid_5_punch.csv','wb')
        punchwriter1 = csv.writer(myfile1, delimiter=',', quotechar='"')
        for key,data in emp_dict1.iteritems():
            row = [data['Pcard'],data['name'],data['reporting'],data['1'],data['2'],data['3'],data['4'],data['5'],data['6'],data['7'],data['8'],data['9'],data['10'],data['11'],data['12'],data['13'],data['14'],data['15'],data['16'],data['17'],data['18'],data['19'],data['20'],data['21'],data['22'],data['23'],data['24'],data['25'],data['26'],data['27'],data['28'],data['29'],data['30'],data['31'],]
    
            punchwriter1.writerow(row)
        myfile1.close()
        
        
        myfile2 = open('/tmp/invalid_7_punch.csv','wb')
        punchwriter2 = csv.writer(myfile2, delimiter=',', quotechar='"')
        for key,data in emp_dict2.iteritems():
            row = [data['Pcard'],data['name'],data['reporting'],data['1'],data['2'],data['3'],data['4'],data['5'],data['6'],data['7'],data['8'],data['9'],data['10'],data['11'],data['12'],data['13'],data['14'],data['15'],data['16'],data['17'],data['18'],data['19'],data['20'],data['21'],data['22'],data['23'],data['24'],data['25'],data['26'],data['27'],data['28'],data['29'],data['30'],data['31'],]
    
            punchwriter2.writerow(row)
        myfile2.close()
        
        return True
        
    def delete_invalid_punch(self, cr, uid, ids, context=None):
        res = {}
        emp_obj = self.pool.get('hr.employee')
        shift_obj = self.pool.get('hr.shift.line')
        count = 0
        for each in self.pool.get('wiz.attendance').browse(cr, uid, ids):
            if each.employee_id and each.department_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True)])
            elif each.employee_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True)])
            elif each.department_id:
                list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True)])
            else:
                list_ids = emp_obj.search(cr, uid, [('active','=',True)])
            
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            year = tm_tuple.tm_year        
            
            emp_ids = emp_obj.browse(cr, uid, list_ids)
            for emp in emp_ids:
                date1 = datetime.strptime(str(year)+'-'+str(month)+'-'+'01','%Y-%m-%d')
                for i in range(31):
                    date2 = date1.strftime('%Y-%m-%d')
                    tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                    if tm_tuple.tm_mon != month:
                        break
                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '<=',date2)], limit=1, order='name DESC')
                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', emp.id),('name', '>',date2)], limit=1, order='name ASC')
                    if prev_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    elif next_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    else:
                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    if shift_data:
                        for line in shift_data.shift_id.shift_line:
                            timing = self.calculate_time(cr, uid, ids, date2, line.from_time, line.to_time)
                            qry = "select emp.sinid from hr_attendance as hr left join hr_employee as emp "\
                            "on (hr.employee_id=emp.id) left join resource_resource as res on (emp.resource_id=res.id) "\
                            "where hr.name + interval '5 hours 30 minute' > "\
                            "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                            "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                            "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                            "hr.day = '"+str(date2)+"' and emp.id = '"+str(emp.id)+"' group by emp.sinid having count(hr.id) = 3"
                            
                            cr.execute(qry)
                            temp = cr.fetchall()
                            for miss in temp:
                                if miss and len(miss) > 0 and miss[0] != None:
                                    print("<------------------DELETE 3 PUNCH--------------------------->",emp.sinid,date2)
                                    query = "delete from hr_attendance where name in (select max(name) from hr_attendance as hr "\
                                    "where hr.name + interval '5 hours 30 minute' > "\
                                    "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                                    "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                                    "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                                    "hr.day = '"+str(date2)+"' and hr.employee_id = '"+str(emp.id)+"' )"
                                    cr.execute(query)
                            
                            qry1 = "select emp.sinid from hr_attendance as hr left join hr_employee as emp "\
                            "on (hr.employee_id=emp.id) left join resource_resource as res on (emp.resource_id=res.id) "\
                            "where hr.name + interval '5 hours 30 minute' > "\
                            "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                            "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                            "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                            "hr.day = '"+str(date2)+"' and emp.id = '"+str(emp.id)+"' group by emp.sinid having count(hr.id) = 5"
                            
                            cr.execute(qry1)
                            temp1 = cr.fetchall()
                            for miss1 in temp1:
                                if miss1 and len(miss1) > 0 and miss1[0] != None:
                                    print("<------------------DELETE 5 PUNCH--------------------------->",emp.sinid,date2)
                                    query1 = "delete from hr_attendance where name in (select max(name) from hr_attendance as hr "\
                                    "where hr.name + interval '5 hours 30 minute' > "\
                                    "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                                    "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                                    "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                                    "hr.day = '"+str(date2)+"' and hr.employee_id = '"+str(emp.id)+"' )"
                                    cr.execute(query1)
                            
                            qry2 = "select emp.sinid from hr_attendance as hr left join hr_employee as emp "\
                            "on (hr.employee_id=emp.id) left join resource_resource as res on (emp.resource_id=res.id) "\
                            "where hr.name + interval '5 hours 30 minute' > "\
                            "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                            "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                            "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                            "hr.day = '"+str(date2)+"' and emp.id = '"+str(emp.id)+"' group by emp.sinid having count(hr.id) = 7"
                            
                            cr.execute(qry2)
                            temp2 = cr.fetchall()
                            for miss2 in temp2:
                                if miss2 and len(miss2) > 0 and miss2[0] != None:
                                    print("<------------------DELETE 7 PUNCH--------------------------->",emp.sinid,date2)
                                    query2 = "delete from hr_attendance where name in (select max(name) from hr_attendance as hr "\
                                    "where hr.name + interval '5 hours 30 minute' > "\
                                    "to_timestamp('"+str(timing['start_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp "\
                                    "- interval '1 hours 30 minute'  and hr.name + interval '5 hours 30 minute' < to_timestamp( "\
                                    "'"+str(timing['final_time'])+"','YYYY-MM-DD HH24:MI:SS')::timestamp and "\
                                    "hr.day = '"+str(date2)+"' and hr.employee_id = '"+str(emp.id)+"' )"
                                    cr.execute(query2)
                                    
                    date1 += timedelta(days=1)
                count += 1
                print "<----------------------------COUNTER------------------>",emp.sinid,count
     

                                  
        return res
    def clear_fault_attendance(self, cr, uid, ids, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
            tm_tuple.tm_mon
            cr.execute("select employee_id,day from hr_attendance where month='"+str(tm_tuple.tm_mon)+"' group by employee_id,day having count(id) %2 <> 0 and count(id) > 2")
            temp = cr.fetchall()
            print "======================temp===============",len(temp)
            for val in temp:
                print "=================count==============",val
                if len(val)>1 and val[0] != None and val[1] != None:
                    query = "delete from hr_attendance where employee_id = '"+str(val[0])+"' and day = '"+str(val[1])+"' and name + interval '5 hours 30 minute' > \
                    (select min(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '"+str(val[0])+"' and day = '"+str(val[1])+"' ) and \
                    name + interval '5 hours 30 minute' < ( select max(name + interval '5 hours 30 minute') from \
                    hr_attendance where employee_id = '"+str(val[0])+"' and day = '"+str(val[1])+"' )"
                    cr.execute(query)
#                    date1 += timedelta(days=1)
        return res
    
    def correct_manual_attendance(self, cr, uid, ids, context=None):
        res = {}
        att_obj = self.pool.get('attendance.timing')
        emp_obj = self.pool.get('hr.employee')
        for each in self.browse(cr, uid, ids):
            
            tm_tuple1 = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
            date1 = datetime.strptime(str(tm_tuple1.tm_year)+'-'+str(tm_tuple1.tm_mon)+'-'+'1','%Y-%m-%d')
            for i in range(31):
                emp_ids = emp_obj.search(cr, uid, [('active','=',True)])
                date2 = date1.strftime('%Y-%m-%d')
                tm_tuple2 = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                if tm_tuple1.tm_mon != tm_tuple2.tm_mon:
                    break
                for line in emp_obj.browse(cr, uid, emp_ids):
                    att_ids = att_obj.search(cr, uid, [('method','=','Manual'),('name','=',date2),('employee_id','=',line.id)])
                    if att_ids:
                        cr.execute("delete from attendance_timing where name='"+str(date2)+"' and method='Auto' and employee_id = '"+str(line.id)+"'")
                date1 += timedelta(days=1)
        return res

class faulty_attendance(osv.osv):
    _name = 'faulty.attendance'
    
    _columns = {
                'name':fields.date('Create Date',readonly=True),
                'month':fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),
                ('8','August'),('9','September'),('10','October'),('11','November'),('12','December'),],'Month',required=True),
                'year_id':fields.many2one('holiday.year','Year',required=True),
                'faulty_lines':fields.one2many('faulty.attendance.line','fault_id','Fault Line',readonly=True),
                }
    
    _defaults = {
                 'name':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                 }
    

    
    def calculate_fault_attendance(self, cr, uid, ids, context=None):
        res = {}
        fault_obj = self.pool.get('faulty.attendance.line')
        emp_obj = self.pool.get('hr.employee')
        att_obj = self.pool.get('hr.attendance')
        for each in self.browse(cr, uid, ids):
            month = each.month
            year = each.year_id and each.year_id.name or False
            if year:
                date1 = datetime.strptime(str(year)+'-'+str(month)+'-'+'1','%Y-%m-%d')
                for i in range(31):
                    
                    date2 = date1.strftime('%Y-%m-%d')
                    tm_tuple = datetime.strptime(date2,'%Y-%m-%d').timetuple()
                    if tm_tuple.tm_mon != int(month):
                        break
                    print "===========faulty date==========",date2
                    cr.execute("select employee_id from hr_attendance  where day='"+str(date2)+"' group by employee_id having count(id) % 2 <> 0")
                    temp = cr.fetchall()
                    emp_list = []
                    emp_dict = {}
                    for val in temp:
                        emp_list.append(val[0])
                        att_ids = att_obj.search(cr, uid, [('day','=',date2),('employee_id','=',val[0])])
                        date_text = ''
                        for att in att_obj.browse(cr, uid, att_ids):
                            actual = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
                            actual = actual + timedelta(hours=5,minutes=30)
                            actual = actual.strftime("%Y-%m-%d %H:%M:%S")
                            if emp_dict.has_key(str(att.employee_id.id)):
                                emp_dict[str(att.employee_id.id)]['date_text'] = emp_dict[str(att.employee_id.id)]['date_text'] + ' , ' +  actual
                            else:
                                emp_dict[str(att.employee_id.id)] = {'date_text': actual}
                    
                    
                    emp_ids = emp_obj.browse(cr, uid, emp_list)
                    for emp in emp_ids:
                        cr.execute("delete from faulty_attendance_line where name = '"+str(date2)+"' and employee_id ='"+str(emp.id)+"'")
                        
                        created_id = fault_obj.create(cr, uid, {'name':date2,'employee_id':emp.id,
                        'department_id':emp.department_id and emp.department_id.id or False,'fault_id':ids[0],'date_text':emp_dict[str(emp.id)]['date_text'],})
                        print "=========================NEW FAULTY RECORD IS CREATED===========================",created_id
                    date1 += timedelta(days=1)
        return res

    
class faulty_attendance_line(osv.osv):
    _name = 'faulty.attendance.line'
    
    _columns = {
                'name':fields.date('Create Date',required=True,readonly=True),
                'employee_id':fields.many2one('hr.employee','Employee',required=True,readonly=True),
                'department_id':fields.related('employee_id','department_id',relation='hr.department',string='Department',type='many2one',readonly=True),
                'fault_id':fields.many2one('faulty.attendance','Fault Attendance',ondelete="cascade"),
                'date_text':fields.char('Attendance',required=True,readonly=True),
                }

    
class employee_department(osv.osv):
    _name = "employee.department"
    _columns = {
                'department_id':fields.many2one('hr.department','Department'),
                'emp_id':fields.many2one('hr.employee','Employee Name'),
                'company_id':fields.many2one('res.company','Company'),
                'employee_id':fields.many2many('hr.employee', 'hr_employee_rel', 'emp_id', 'categ_id', 'Employee')
                }
    
    def on_change_department_id(self, cr, uid, ids,department_id,emp_id,company_id,context=None):
        res={}
        emp_obj = self.pool.get('hr.employee')
        if department_id:
            emp_id = emp_obj.search(cr, uid, [('department_id', '=', department_id),('active','=',True)])
        elif emp_id:
             emp_id = emp_obj.search(cr, uid, [('id', '=', emp_id),('active','=',True)])
        elif company_id:
             emp_id = emp_obj.search(cr, uid, [('company_id', '=', company_id),('active','=',True)])  
       
        if emp_id:
            employee = emp_obj.browse(cr, uid, emp_id)   
            if employee:
                for val in employee:
                    emp_obj.write(cr, uid,[val.id], {'ot_tick':True})
                    res['value'] = {'employee_id' : employee}
                     
        return res

    def update_ot(self, cr, uid, ids, context=None):
        res = {}
        dept = self.browse(cr,uid,ids,context=None)
        emp_obj = self.pool.get('hr.employee')
        for val in dept.employee_id:
             if dept.department_id:
                 emp = emp_obj.search(cr, uid, [('department_id', '=', dept.department_id.id),('active','=',True)])
             elif dept.emp_id:
                 emp = emp_obj.search(cr, uid, [('id', '=', dept.emp_id.id),('active','=',True)])
             elif dept.company_id:
                 emp = emp_obj.search(cr, uid, [('company_id', '=', dept.company_id.id),('active','=',True)])

             if emp :
                  employee = emp_obj.browse(cr, uid, emp)
                  for val in employee: 
                      a = emp_obj.write(cr, uid,[val.id], {'ot_tick':val.ot_tick})
                     
        return res
        
    def reset_ot(self, cr, uid, ids, context=None):
         res = {}
         dept = self.browse(cr,uid,ids,context=None)
         emp_obj = self.pool.get('hr.employee')
         if dept.department_id:
             emp = emp_obj.search(cr, uid, [('department_id', '=', dept.department_id.id),('active','=',True),('ot_tick','=',True)])
         elif dept.emp_id:
             emp = emp_obj.search(cr, uid, [('id', '=', dept.emp_id.id),('active','=',True),('ot_tick','=',True)])
         elif dept.company_id:
             emp = emp_obj.search(cr, uid, [('company_id', '=', dept.company_id.id),('active','=',True),('ot_tick','=',True)])
            
         if emp :
              employee = emp_obj.browse(cr, uid, emp) 
              for val in employee :
                  a = emp_obj.write(cr, uid,[val.id],{'ot_tick':False})
                      
         return res
    

class employee_department_epf(osv.osv):
    _name = "employee.department.epf"
    _columns = {
                'department_id':fields.many2one('hr.department','Department'),
                'emp_id':fields.many2one('hr.employee','Employee Name'),
                'company_id':fields.many2one('res.company','Company'),
                'employee_id':fields.many2many('hr.employee', 'hr_employee_rel_table', 'emp_id', 'categ_id', 'Employee')
                }
    
    def on_change_department_id(self, cr, uid, ids,department_id,emp_id,company_id,context=None):
        res={}
        emp_obj = self.pool.get('hr.employee')
        if department_id:
            emp_id = emp_obj.search(cr, uid, [('department_id', '=', department_id),('active','=',True)])
        elif emp_id:
             emp_id = emp_obj.search(cr, uid, [('id', '=', emp_id),('active','=',True)])
        elif company_id:
             emp_id = emp_obj.search(cr, uid, [('company_id', '=', company_id),('active','=',True)])  
                
        if emp_id:
            employee = emp_obj.browse(cr, uid, emp_id)   
            if employee:
                for val in employee:
                    emp_obj.write(cr, uid,[val.id], {'epf_tick':True})
                    res['value'] = {'employee_id' : employee}
                     
        return res

    def update_epf(self, cr, uid, ids, context=None):
        res = {}
        dept = self.browse(cr,uid,ids,context=None)
        emp_obj = self.pool.get('hr.employee')
        for val in dept.employee_id:
             if dept.department_id:
                 emp = emp_obj.search(cr, uid, [('department_id', '=', dept.department_id.id),('active','=',True)])
             elif dept.emp_id:
                 emp = emp_obj.search(cr, uid, [('id', '=', dept.emp_id.id),('active','=',True)])
             elif dept.company_id:
                 emp = emp_obj.search(cr, uid, [('company_id', '=', dept.company_id.id),('active','=',True)])
             if emp :
                  employee = emp_obj.browse(cr, uid, emp)
                  for val in employee: 
                      a = emp_obj.write(cr, uid,[val.id], {'epf_tick':val.epf_tick})
                     
        return res
        
    def reset_epf(self, cr, uid, ids, context=None):
         res = {}
         dept = self.browse(cr,uid,ids,context=None)
         emp_obj = self.pool.get('hr.employee')
         if dept.department_id:
             emp = emp_obj.search(cr, uid, [('department_id', '=', dept.department_id.id),('active','=',True),('epf_tick','=',True)])
         elif dept.emp_id:
             emp = emp_obj.search(cr, uid, [('id', '=', dept.emp_id.id),('active','=',True),('epf_tick','=',True)])
         elif dept.company_id:
             emp = emp_obj.search(cr, uid, [('company_id', '=', dept.company_id.id),('active','=',True),('epf_tick','=',True)])
         if emp :
              employee = emp_obj.browse(cr, uid, emp) 
              for val in employee :
                  a = emp_obj.write(cr, uid,[val.id],{'epf_tick':False})
                      
         return res
    
class employee_department_esi(osv.osv):
    _name = "employee.department.esi"
    _columns = {
                'department_id':fields.many2one('hr.department','Department'),
                'emp_id':fields.many2one('hr.employee','Employee Name'),
                'company_id':fields.many2one('res.company','Company'),
                'employee_id':fields.many2many('hr.employee', 'hr_employee_rel_esi_table', 'emp_id', 'categ_id', 'Employee')
                }
    
    def on_change_department_id(self, cr, uid, ids,department_id,emp_id,company_id,context=None):
        res={}
        emp_obj = self.pool.get('hr.employee')
        if department_id:
            emp_id = emp_obj.search(cr, uid, [('department_id', '=', department_id),('active','=',True)])
        elif emp_id:
             emp_id = emp_obj.search(cr, uid, [('id', '=', emp_id),('active','=',True)])
        elif company_id:
             emp_id = emp_obj.search(cr, uid, [('company_id', '=', company_id),('active','=',True)])  
                 
        if emp_id:
            employee = emp_obj.browse(cr, uid, emp_id)   
            if employee:
                for val in employee:
                    emp_obj.write(cr, uid,[val.id], {'esi_tick':True})
                    res['value'] = {'employee_id' : employee}
                     
        return res

    def update_esi(self, cr, uid, ids, context=None):
        res = {}
        dept = self.browse(cr,uid,ids,context=None)
        emp_obj = self.pool.get('hr.employee')
        for val in dept.employee_id:
             if dept.department_id:
                 emp = emp_obj.search(cr, uid, [('department_id', '=', dept.department_id.id),('active','=',True)])
             elif dept.emp_id:
                 emp = emp_obj.search(cr, uid, [('id', '=', dept.emp_id.id),('active','=',True)])
             elif dept.company_id:
                 emp = emp_obj.search(cr, uid, [('company_id', '=', dept.company_id.id),('active','=',True)])
             if emp :
                  employee = emp_obj.browse(cr, uid, emp)
                  for val in employee: 
                      a = emp_obj.write(cr, uid,[val.id], {'esi_tick':val.esi_tick})
                     
        return res
        
    def reset_esi(self, cr, uid, ids, context=None):
         res = {}
         dept = self.browse(cr,uid,ids,context=None)
         emp_obj = self.pool.get('hr.employee')
         if dept.department_id:
             emp = emp_obj.search(cr, uid, [('department_id', '=', dept.department_id.id),('active','=',True),('esi_tick','=',True)])
         elif dept.emp_id:
             emp = emp_obj.search(cr, uid, [('id', '=', dept.emp_id.id),('active','=',True),('esi_tick','=',True)])
         elif dept.company_id:
             emp = emp_obj.search(cr, uid, [('company_id', '=', dept.company_id.id),('active','=',True),('esi_tick','=',True)])
         if emp :
              employee = emp_obj.browse(cr, uid, emp) 
              for val in employee :
                  a = emp_obj.write(cr, uid,[val.id],{'esi_tick':False})
                      
         return res
    
#                                                   EMPLOYEE PAYMENT  MANAGEMENT BONUS 

class payment_management_bonus(osv.osv):
    _name='payment.management.bonus'
    
    _columns={
              'bonus_from':fields.date('Bonus From',required=True),
              'bonus_till':fields.date('Bonus Till',required=True),
              'employee_id':fields.many2one('hr.employee','Employee'),
              'company_id':fields.many2one('res.company','Company',),
              'user_id':fields.many2one('res.users','User',readonly=True),
              'bonus_line':fields.one2many('payment.management.bonus.line','bonus_id','Bonus line'),
              'export_data':fields.binary('File',readonly=True),
              'filename':fields.char('File Name',size=250,readonly=True),
              'name':fields.char('Name',size=250),
              'employment_type':fields.selection([('Employee','Employee'),('Labor','Labor')],'Employment Type'),
              }    
    
    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               'name': 'Payment Bonus',
              }

    def compute_bonus(self, cr, uid, ids, context=None):
        sal_obj = self.pool.get('salary.payment.line')
        emp_obj = self.pool.get('hr.employee')
        year_obj = self.pool.get('emp.year')
        categ_obj = self.pool.get('employee.salary.category')
        count = 0
        categ_list = []
        
        cr.execute("select id from employee_salary_category ")
        temp = cr.fetchall()
        for data in temp:
            categ_list.append(data[0])
            
        for each in self.browse(cr, uid, ids):
  
            if  each.employee_id and each.company_id and each.employment_type :
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('id','=',each.employee_id.id),('employment_type','=',each.employment_type),('company_id','=',each.company_id.id)])
            elif each.employee_id and each.company_id  :
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('id','=',each.employee_id.id),('company_id','=',each.company_id.id)])    
            elif each.employee_id and each.employment_type  :
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('id','=',each.employee_id.id),('employment_type','=',each.employment_type)])    
            elif each.company_id and each.employment_type  :
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('employment_type','=',each.employment_type)])      
            elif each.employee_id:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('id','=',each.employee_id.id)])
            elif each.company_id:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id)])
            elif each.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('employment_type','=',each.employment_type)])    
            else:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True)])
            
            for line in emp_obj.browse(cr, uid, emp_ids):
                jan = feb = mar = apr = may = jun = jul = aug = sep = oct = nov = dec =0
                jan_day = feb_day = mar_day = apr_day = may_day = june_day = july_day = aug_day = sep_day = oct_day = nov_day = dec_day =0
                total_salary=apr_salary=may_salary=june_salary=july_salary=aug_salary=sep_salary=oct_salary=nov_salary=dec_salary=jan_salary=feb_salary=mar_salary=0
                basic = 0
                for val1 in categ_obj.browse(cr,uid,categ_list):
                    if val1.category == 'Skilled' and line.category == 'Skilled':
                        category = 'Skilled'
                        bonus_limit = val1.bonus_limit
                        salary = val1.salary
                    if  val1.category == 'UnSkilled' and line.category == 'UnSkilled':
                        category = 'UnSkilled'
                        bonus_limit = val1.bonus_limit
                        salary = val1.salary
                    if val1.category == 'Semi_Skilled' and line.category == 'Semi_Skilled':
                        category = 'Semi_Skilled'
                        bonus_limit = val1.bonus_limit
                        salary = val1.salary
                
                if line.category == category and bonus_limit >= line.total_salary:
                    starting_date = False
                    total_month_days = 0
                    total_days1 = 0
                    bonus_from = each.bonus_from
                    bonus_till = each.bonus_till
                    total_day = 0
                    rnd_total_pay = total_pay = 0
                    month_count=0
                    month = 0
                    bonus_from = datetime.strptime(bonus_from,'%Y-%m-%d')
                    bonus_till = datetime.strptime(bonus_till,'%Y-%m-%d')
                    starting_date = bonus_from
                    while (bonus_from <= bonus_till):
                        bonus_till_to = bonus_till
                        month += 1
                        tm_tuple = datetime.strptime(bonus_from.strftime('%Y-%m-%d'),'%Y-%m-%d').timetuple()
                        emp_month = tm_tuple.tm_mon
                        emp_year = tm_tuple.tm_year
                        tm_tuple_to = datetime.strptime(bonus_till_to.strftime('%Y-%m-%d'),'%Y-%m-%d').timetuple()
                        emp_month_to = tm_tuple_to.tm_mon
                        emp_year_to = tm_tuple_to.tm_year
                        year_id1 = year_obj.search(cr, uid, [('name','=',emp_year_to)])
                        salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month_to),('year_id.name','=',emp_year_to)])
                        
                        if sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month_to),('year_id.name','=',emp_year_to)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month_to),('year_id.name','=',emp_year_to)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month_to)-1)),('year_id.name','=',emp_year_to)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month_to)-1)),('year_id.name','=',emp_year_to)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month_to)-2)),('year_id.name','=',emp_year_to)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month_to)-2)),('year_id.name','=',emp_year_to)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+8)),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+8)),('year_id.name','=',emp_year)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+7)),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+7)),('year_id.name','=',emp_year)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+6)),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+6)),('year_id.name','=',emp_year)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+5)),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+5)),('year_id.name','=',emp_year)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+4)),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+4)),('year_id.name','=',emp_year)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+3)),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+3)),('year_id.name','=',emp_year)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+2)),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+2)),('year_id.name','=',emp_year)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+1)),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+1)),('year_id.name','=',emp_year)])
                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month),('year_id.name','=',emp_year)]):
                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month),('year_id.name','=',emp_year)])
                        else:
                            salary_id=[] 
                            
                        for val in sal_obj.browse(cr, uid, sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month),('year_id.name','=',emp_year)])):
                            if val:
                                month_count+=1
                                if line.category == 'Skilled':
                                    if category == 'Skilled':
                                        basic = salary

                                if line.category == 'UnSkilled':
                                    if category == 'UnSkilled':
                                        basic = salary

                                if line.category == 'Semi_Skilled':
                                    if category == 'Semi_Skilled':
                                        basic = salary
                                         
                                cr.execute("select rc.id from res_company as rc left join resource_resource as rr on rc.id = rr.company_id left join hr_employee as hr on rr.id = hr.resource_id where hr.id = '"+str(line.id)+"' and rc.name ilike '%%%%%Lohia%%%%%'")
                                company = cr.fetchall()
                                if company:
                                    total_pay += ((((basic * val.days) / val.month_days) * 8.33)/100)   

                                cr.execute("select rc.id from res_company as rc left join resource_resource as rr on rc.id = rr.company_id left join hr_employee as hr on rr.id = hr.resource_id where hr.id = '"+str(line.id)+"' and rc.name ilike '%%%%%%%%Designco%%%%%%%%'")
                                company = cr.fetchall()
                                if company:
                                    total_pay += ((((basic * val.days) / val.month_days) * 8.33)/100)   
                                    
                                if emp_month==1:
                                        jan=val.days
                                        jan_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * jan)/jan_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            jan_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            jan_salary = math.ceil(t)
                                elif emp_month==2:
                                        feb=val.days
                                        feb_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * feb)/feb_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            feb_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            feb_salary = math.ceil(t)
                                elif emp_month==3:
                                        mar=val.days
                                        mar_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * mar)/mar_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            mar_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            mar_salary = math.ceil(t)
                                elif emp_month==4:
                                        apr=val.days
                                        apr_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * apr)/apr_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            apr_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            apr_salary = math.ceil(t)
                                elif emp_month==5:
                                        may=val.days
                                        may_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary =((basic * may)/may_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            may_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            may_salary = math.ceil(t)
                                elif emp_month==6:
                                        jun=val.days
                                        june_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * jun)/june_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            june_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            june_salary = math.ceil(t)
                                elif emp_month==7:
                                        jul=val.days
                                        july_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * jul)/july_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            july_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            july_salary = math.ceil(t)
                                elif emp_month==8:
                                        aug=val.days
                                        aug_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * aug)/aug_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            aug_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            aug_salary = math.ceil(t)
                                elif emp_month==9:
                                        sep=val.days
                                        sep_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * sep)/sep_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            sep_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            sep_salary = math.ceil(t)
                                elif emp_month==10:
                                        oct=val.days
                                        oct_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * oct)/oct_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            oct_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            oct_salary = math.ceil(t)
                                elif emp_month==11:
                                        nov=val.days
                                        nov_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * nov)/nov_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            nov_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            nov_salary = math.ceil(t)
                                elif emp_month==12:
                                        dec=val.days
                                        dec_day = val.month_days
                                        month_id = val.month
                                        year_id = val.year_id.id
                                        salary = ((basic * dec)/dec_day)
                                        salary1 = str(salary)
                                        salary2 = salary1.split('.')
                                        salary3 = salary2[0]
                                        salary4 = int(salary2[1][0:2])
                                        if salary4 in range(0,50):
                                            sal = salary3
                                            t = float(sal)
                                            dec_salary = t
                                        else:
                                            sal = salary3 + '.' + str(salary4)
                                            t = float(sal)
                                            dec_salary = math.ceil(t)
                                            
                                            
                        total_days1 = (jan + feb + mar + apr + may + jun + jul + aug + sep + oct + nov + dec)
                        total_month_days = (jan_day + feb_day + mar_day + apr_day + may_day + june_day + july_day + aug_day + sep_day + oct_day + nov_day + dec_day)
                        total_salary=apr_salary+may_salary+june_salary+july_salary+aug_salary+sep_salary+oct_salary+nov_salary+dec_salary+jan_salary+feb_salary+mar_salary
                        bonus_from = bonus_from + relativedelta(months=+1)
                    
                    if month < 0:
                        continue     
                    a = total_pay
                    if a > 0:
                        b = str(a)
                        c = b.split('.')
                        d = c[0]
                        e = int(c[1][0:2])
                        if e in range(0,50):
                            s = d
                            t = float(s)
                            rnd_total_pay = t
                        else:
                            s = d + '.' + str(e)
                            t = float(s)
                            rnd_total_pay = math.ceil(t)
                                
                    line_dict = {
                                  'bonus_id':each.id,
                                  'employee_id':line.id,
                                  'joining_date':line.doj,
                                  'company_id':line.company_id.id,
                                  'bonus_from':starting_date,
                                  'bonus_till':each.bonus_till,
                                  'bonus_month':str(month_count) + ' month',
                                  'bonus':rnd_total_pay,
                                  'basic':basic,
                                  'apr':apr,
                                  'may':may,
                                  'june':jun,
                                  'july':jul,
                                  'aug':aug,
                                  'sep':sep,
                                  'oct':oct,
                                  'nov':nov,
                                  'dec':dec,
                                  'jan':jan,
                                  'feb':feb,
                                  'mar':mar,
                                  'apr_day':apr_day,
                                  'may_day':may_day,
                                  'june_day':june_day,
                                  'july_day':july_day,
                                  'aug_day':aug_day,
                                  'sep_day':sep_day,
                                  'oct_day':oct_day,
                                  'nov_day':nov_day,
                                  'dec_day':dec_day,
                                  'jan_day':jan_day,
                                  'feb_day':feb_day,
                                  'mar_day':mar_day,
                                  'apr_salary':apr_salary,
                                  'may_salary':may_salary,
                                  'june_salary':june_salary,
                                  'july_salary':july_salary,
                                  'aug_salary':aug_salary,
                                  'sep_salary':sep_salary,
                                  'oct_salary':oct_salary,
                                  'nov_salary':nov_salary,
                                  'dec_salary':dec_salary,
                                  'jan_salary':jan_salary,
                                  'feb_salary':feb_salary,
                                  'mar_salary':mar_salary,
                                  'total_day':total_days1,
                                  'total_month_day':total_month_days,
                                  'total_salary':total_salary,
                                  'user_id':uid,
                                  'month':month_id,
                                  'year_id':year_id,
                                 }
                    print"====month_id====",month_id,"====year_id===",year_id,"===line.id====",line.id
                    cr.execute("delete from payment_management_bonus_line where employee_id ='"+str(line.id)+"' and year_id = '"+str(year_id)+"' and month = '"+str(month_id)+"'")
                    if rnd_total_pay == 0.0:
                        continue
                    count += 1
                    new_id = self.pool.get('payment.management.bonus.line').create(cr, uid, line_dict)
                    print "<------------------- NEW RECORD CREATED  --------------->",count,str(month) + ' month',rnd_total_pay
        return True

    def print_report(self, cr, uid, ids, data, context=None):
        obj = self.browse(cr,uid,ids)
        f_name = ''
        d_name = ''
        wb = Workbook()
        ws = wb.add_sheet('Payment Bonus')
        fnt1 = Font()
        fnt1.name = 'Arial'
        fnt1.height= 300
        fnt1.bold=True
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_CENTER
        borders1 = Borders()
        borders1.left = 0x00
        borders1.right = 0x00
        borders1.top = 0x00
        borders1.bottom = 0x00
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_CENTER
        pattern1 = Pattern()
        pattern1.pattern1 = Pattern.SOLID_PATTERN
        pattern1.pattern1_fore_colour =  0x1F
        style_header1= XFStyle()
        style_header1.font= fnt1
        style_header1.pattern= pattern1
        style_header1.borders = borders1
        style_header1.alignment=align1
        
        fnt2 = Font()
        fnt2.name = 'Arial'
        fnt2.height= 300
        fnt2.bold=True
        align_content2 = Alignment()
        align_content2.horz= Alignment.HORZ_CENTER
        borders2 = Borders()
        borders2.left = 0x00
        borders2.right = 0x00
        borders2.top = 0x00
        borders2.bottom = 0x00
        align2 = Alignment()
        align2.horz = Alignment.HORZ_CENTER
        align2.vert = Alignment.VERT_CENTER
        pattern2 = Pattern()
        pattern2.pattern2 = Pattern.SOLID_PATTERN
        pattern2.pattern2_fore_colour =  0x1F
        style_header2= XFStyle()
        style_header2.font= fnt2
        style_header2.pattern= pattern2
        style_header2.borders = borders2
        style_header2.alignment=align2

        fnt3 = Font()
        fnt3.name = 'Arial'
        fnt3.height= 300
        fnt3.bold=True
        align_content3 = Alignment()
        align_content3.horz= Alignment.HORZ_CENTER
        borders3 = Borders()
        borders3.left = 0x00
        borders3.right = 0x00
        borders3.top = 0x00
        borders3.bottom = 0x00
        align3 = Alignment()
        align3.horz = Alignment.HORZ_CENTER
        align3.vert = Alignment.VERT_CENTER
        pattern3 = Pattern()
        pattern3.pattern3 = Pattern.SOLID_PATTERN
        pattern3.pattern3_fore_colour =  0x1F
        style_header3= XFStyle()
        style_header3.font= fnt3
        style_header3.pattern= pattern3
        style_header3.borders = borders3
        style_header3.alignment=align3
        
        fnt = Font()
        fnt.name = 'Arial'
        fnt.height= 275
        content_fnt = Font()
        content_fnt.name ='Arial'
        content_fnt.height =150
        align_content = Alignment()
        align_content.horz= Alignment.HORZ_CENTER
        borders = Borders()
        borders.left = 0x02
        borders.right = 0x02
        borders.top = 0x02
        borders.bottom = 0x02
        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        align.vert = Alignment.VERT_CENTER
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour =  0x1F
        style_header= XFStyle()
        style_header.font= fnt
        style_header.pattern= pattern
        style_header.borders = borders
        style_header.alignment=align

        fnt5 = Font()
        fnt5.name = 'Arial'
        fnt5.height= 200
        content_fnt5 = Font()
        content_fnt5.name ='Arial'
        content_fnt5.height =150
        align_content5 = Alignment()
        align_content5.horz= Alignment.HORZ_CENTER
        borders5 = Borders()
        borders5.left = 0x02
        borders5.right = 0x02
        borders5.top = 0x02
        borders5.bottom = 0x02
        align5 = Alignment()
        align5.horz = Alignment.HORZ_CENTER
        align5.vert = Alignment.VERT_CENTER
        pattern5 = Pattern()
#        pattern5.pattern = Pattern.SOLID_PATTERN
#        pattern5.pattern_fore_colour =  0x1F
        style_header5= XFStyle()
        style_header5.font= fnt5
        style_header5.pattern= pattern5
        style_header5.borders = borders5
        style_header5.alignment=align5

        if obj.company_id:
            get_name = obj.company_id.name
        else:
            get_name = obj.employee_id.resource_id.company_id.name
        
        ws.row(0).height=500
        ws.write_merge(0,0,0,20,get_name,style_header1)
        
        date1 = datetime.strptime(obj.bonus_from,"%Y-%m-%d").timetuple().tm_year
        date2 = datetime.strptime(obj.bonus_till,"%Y-%m-%d").timetuple().tm_year
        if date1 == date2 :
           d_name = 'BONUS' +' - '+ str(date1)
        else:
            d_name = 'BONUS' +'  '+ str(date1) + ' ' + '-' + ' ' +  str(date2)
              
        ws.row(1).height=500
        ws.write_merge(1,1,0,20,d_name,style_header2)


        ws.col(0).width = 5000 
        ws.col(1).width = 6000   
        ws.col(2).width = 3000 
        ws.col(3).width = 3000 
        ws.col(4).width = 3000 
        ws.col(5).width = 3000   
        ws.col(6).width = 3000 
        ws.col(7).width = 3000 
        ws.col(8).width = 3000 
        ws.col(9).width = 3000   
        ws.col(10).width = 3000 
        ws.col(11).width = 3000 
        ws.col(12).width = 3000 
        ws.col(13).width = 3000   
        ws.col(14).width = 3000 
        ws.col(15).width = 3000 
        ws.col(16).width = 3000 
        ws.col(17).width = 3000   
        ws.col(18).width = 3000 
        ws.col(19).width = 3000 
        ws.col(20).width = 3000 
        ws.col(21).width = 3000   
        ws.col(22).width = 3000 
        ws.col(23).width = 3000 
        ws.col(24).width = 3000 
        ws.col(25).width = 3000   
        ws.col(26).width = 3000 
        ws.col(27).width = 3000 
        ws.col(28).width = 4000
        
        ws.row(2).height=400
        ws.write(2,0,'EMP. CODE',style_header)
        ws.write(2,1,'NAME',style_header)
        ws.write_merge(2,2,2,3,'APRIL',style_header)
        ws.write_merge(2,2,4,5,'MAY',style_header)
        ws.write_merge(2,2,6,7,'JUNE',style_header)
        ws.write_merge(2,2,8,9,'JULY',style_header)
        ws.write_merge(2,2,10,11,'AUGUST',style_header)
        ws.write_merge(2,2,12,13,'SEPTEMBER',style_header)
        ws.write_merge(2,2,14,15,'OCTOBER',style_header)
        ws.write_merge(2,2,16,17,'NOVEMBER',style_header)
        ws.write_merge(2,2,18,19,'DECEMBER',style_header)
        ws.write_merge(2,2,20,21,'JANUARY',style_header)
        ws.write_merge(2,2,22,23,'FEBRUARY',style_header)
        ws.write_merge(2,2,24,25,'MARCH',style_header)
        ws.write_merge(2,2,26,27,'TOTAL',style_header)
        ws.write(2,28,'BONUS',style_header)

        ws.row(3).height=400
        ws.write(3,0,'',style_header)
        ws.write(3,1,'',style_header)
        ws.write(3,2,'DAYS',style_header)
        ws.write(3,3,'SALARY',style_header)
        ws.write(3,4,'DAYS',style_header)
        ws.write(3,5,'SALARY',style_header)
        ws.write(3,6,'DAYS',style_header)
        ws.write(3,7,'SALARY',style_header)
        ws.write(3,8,'DAYS',style_header)
        ws.write(3,9,'SALARY',style_header)
        ws.write(3,10,'DAYS',style_header)
        ws.write(3,11,'SALARY',style_header)
        ws.write(3,12,'DAYS',style_header)
        ws.write(3,13,'SALARY',style_header)
        ws.write(3,14,'DAYS',style_header)
        ws.write(3,15,'SALARY',style_header)
        ws.write(3,16,'DAYS',style_header)
        ws.write(3,17,'SALARY',style_header)
        ws.write(3,18,'DAYS',style_header)
        ws.write(3,19,'SALARY',style_header)
        ws.write(3,20,'DAYS',style_header)
        ws.write(3,21,'SALARY',style_header)
        ws.write(3,22,'DAYS',style_header)
        ws.write(3,23,'SALARY',style_header)
        ws.write(3,24,'DAYS',style_header)
        ws.write(3,25,'SALARY',style_header)
        ws.write(3,26,'DAYS',style_header)
        ws.write(3,27,'SALARY',style_header)
        ws.write(3,28,'',style_header)
        
        for row in obj:
            if len(row.bonus_line) > 0:
                columnno = 4
                for inlinerow in row.bonus_line:
                    ws.write(columnno,0,inlinerow.employee_id.sinid,style_header5)
                    ws.write(columnno,1,inlinerow.employee_id.name,style_header5)
                    ws.write(columnno,2,inlinerow.apr,style_header5)
                    ws.write(columnno,3,inlinerow.apr_salary,style_header5)
                    ws.write(columnno,4,inlinerow.may,style_header5)
                    ws.write(columnno,5,inlinerow.may_salary,style_header5)
                    ws.write(columnno,6,inlinerow.june,style_header5)
                    ws.write(columnno,7,inlinerow.june_salary,style_header5)
                    ws.write(columnno,8,inlinerow.july,style_header5)
                    ws.write(columnno,9,inlinerow.july_salary,style_header5)
                    ws.write(columnno,10,inlinerow.aug,style_header5)
                    ws.write(columnno,11,inlinerow.aug_salary,style_header5)
                    ws.write(columnno,12,inlinerow.sep,style_header5)
                    ws.write(columnno,13,inlinerow.sep_salary,style_header5)
                    ws.write(columnno,14,inlinerow.oct,style_header5)
                    ws.write(columnno,15,inlinerow.oct_salary,style_header5)
                    ws.write(columnno,16,inlinerow.nov,style_header5)
                    ws.write(columnno,17,inlinerow.nov_salary,style_header5)
                    ws.write(columnno,18,inlinerow.dec,style_header5)
                    ws.write(columnno,19,inlinerow.dec_salary,style_header5)
                    ws.write(columnno,20,inlinerow.jan,style_header5)
                    ws.write(columnno,21,inlinerow.jan_salary,style_header5)
                    ws.write(columnno,22,inlinerow.feb,style_header5)
                    ws.write(columnno,23,inlinerow.feb_salary,style_header5)
                    ws.write(columnno,24,inlinerow.mar,style_header5)
                    ws.write(columnno,25,inlinerow.mar_salary,style_header5)
                    ws.write(columnno,26,inlinerow.total_day,style_header5)
                    ws.write(columnno,27,inlinerow.total_salary,style_header5)
                    ws.write(columnno,28,inlinerow.bonus,style_header5)

                    columnno += 1
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        
        return self.write(cr, uid, ids, {'export_data':out,'filename':'Payment Bonus.xls'}, context=context)
    
    
class payment_management_bonus_line(osv.osv):
    _name='payment.management.bonus.line'
    
    _columns={
              'bonus_id':fields.many2one('payment.management.bonus','Bonus'),
              'employee_id':fields.many2one('hr.employee','Employee',required=True, readonly=True),
              'joining_date':fields.date('Joining Date',required=True, readonly=True),
              'company_id':fields.many2one('res.company','Company',),
              'bonus_from':fields.date('Bonus From',required=True,readonly=True),
              'bonus_till':fields.date('Bonus Till',required=True,readonly=True),
              'bonus_month':fields.char('Total Month',size=64,readonly=True),
              'bonus':fields.float('Amount',digits_compute= dp.get_precision('Account'),readonly=True),
              'basic':fields.float('Basic'),
              'apr':fields.float('APR'),
              'may':fields.float('MAY'),
              'june':fields.float('JUNE'),
              'july':fields.float('JULY'),
              'aug':fields.float('AUG'),
              'sep':fields.float('SEP'),
              'oct':fields.float('OCT'),
              'nov':fields.float('NOV'),
              'dec':fields.float('DEC'),
              'jan':fields.float('JAN'),
              'feb':fields.float('FEB'),
              'mar':fields.float('MAR'),
              'apr_day':fields.float('APR DAY'),
              'may_day':fields.float('MAY DAY'),
              'june_day':fields.float('JUNE DAY'),
              'july_day':fields.float('JULY DAY'),
              'aug_day':fields.float('AUG DAY'),
              'sep_day':fields.float('SEP DAY'),
              'oct_day':fields.float('OCT DAY'),
              'nov_day':fields.float('NOV DAY'),
              'dec_day':fields.float('DEC DAY'),
              'jan_day':fields.float('JAN DAY'),
              'feb_day':fields.float('FEB DAY'),
              'mar_day':fields.float('MAR DAY'),
              'apr_salary':fields.float('APR SALARY'),
              'may_salary':fields.float('MAY SALARY'),
              'june_salary':fields.float('JUNE SALARY'),
              'july_salary':fields.float('JULY SALARY'),
              'aug_salary':fields.float('AUG SALARY'),
              'sep_salary':fields.float('SEP SALARY'),
              'oct_salary':fields.float('OCT SALARY'),
              'nov_salary':fields.float('NOV SALARY'),
              'dec_salary':fields.float('DEC SALARY'),
              'jan_salary':fields.float('JAN SALARY'),
              'feb_salary':fields.float('FEB SALARY'),
              'mar_salary':fields.float('MAR SALARY'),
              'total_day':fields.float('T.DAYS'),
              'total_month_day':fields.float('MONTH DAYS'),
              'total_salary':fields.float('TOTAL SALARY'),
              'user_id':fields.many2one('res.users','Created By',readonly=True),
              'month':fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),
                ('8','August'),('9','September'),('10','October'),('11','November'),('12','December'),],'Month',readonly=True),
              'year_id':fields.many2one('holiday.year','Year',readonly=True),
              'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),
              }
    
    
    _defaults={
              'user_id': lambda obj, cr, uid, context: uid,
              }




