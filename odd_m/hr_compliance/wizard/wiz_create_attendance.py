from openerp.osv import osv, fields
import time
import random
from datetime import datetime, timedelta
from openerp.tools.translate import _
import math
import dateutil.relativedelta as relativedelta
import dateutil.rrule as rrule

class wiz_create_att(osv.TransientModel):
    _name = 'wiz.create.att'
    
    _columns={
              'name':fields.date("From Date"),
              'till_date':fields.date("Till Date"),
              'security':fields.boolean("Security"),
              'employee_id':fields.many2one("hr.employee",string="Employee"),
              }
    
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
        
        val2 = self.float_time_convert(end)
        if val2 and len(str(val2[1])) == 1:
            time2 = str(val2[0]) +':'+'0'+str(val2[1])
        
        if val2 and len(str(val2[1])) == 2:
            time2 = str(val2[0]) +':'+str(val2[1])
        
        date_tuple = datetime.strptime(date,'%Y-%m-%d').timetuple()      
        year = date_tuple.tm_year
        mon = date_tuple.tm_mon
        day = date_tuple.tm_mday
        start_time = str(year)+'-'+str(mon)+'-'+str(day)+' '+str(time1)+':00'
        
        if end < start:
            date1 = datetime.strptime(date,'%Y-%m-%d')
            date1 =  date1 + timedelta(days=1)
            date1 = datetime.strftime(date1,'%Y-%m-%d')
            date_tuple = datetime.strptime(date1,'%Y-%m-%d').timetuple()      
            year = date_tuple.tm_year
            mon = date_tuple.tm_mon
            day = date_tuple.tm_mday
            end_time = str(year)+'-'+str(mon)+'-'+str(day)+' '+str(time2)+':00'
            
        else:
            end_time = str(year)+'-'+str(mon)+'-'+str(day)+' '+str(time2)+':00'
            
        
        
        timing = {
                  'start_time':start_time,
                  'end_time':end_time,
                  }
        return timing

    
    def compute_attendance(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        att_obj = self.pool.get('hr.attendance')
        shift_obj = self.pool.get('hr.shift.line')
        for each in self.pool.get('wiz.create.att').browse(cr, uid, ids):
            if each.employee_id :
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True)])
            emp_ids = emp_obj.browse(cr, uid, list_ids)
            if each.security :
                if each.name and not each.till_date :
                    tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
                    month = tm_tuple.tm_mon
                    year = tm_tuple.tm_year        
                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                    for val in emp_ids:
                        rec_data = self.pool.get('hr.attendance').search(cr, uid, (['search_date','=',each.name],['employee_id','=',val.id]))
                        if len(rec_data) == 0:
                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',each.name)], limit=1, order='name DESC')
                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',each.name)], limit=1, order='name ASC')
                            if prev_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                            elif next_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to attendance date." % (val.name)))
                            if shift_data:
                                for line in shift_data.shift_id.shift_line:
                                    timing = self.calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                            in_time = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S')
                            out_time = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                            search_date1 = in_time.strftime("%Y-%m-%d")
                            search_date2 = out_time.strftime("%Y-%m-%d")
                            in_temp = random.randrange(3,9)
                            out_temp = random.randrange(1,5)
                            in_time = in_time - timedelta(hours=0,minutes=in_temp)
                            in_time = in_time - timedelta(hours=5,minutes=30)
                            out_time = out_time + timedelta(hours=0,minutes=out_temp)
                            out_time = out_time - timedelta(hours=5,minutes=30)
                            att_in_id = att_obj.create(cr, uid, {'name' : in_time, 'employee_id' : val.id ,'day':each.name,'month':str(month),'year_id':year_id and year_id[0] or False,
                                                         'search_date':search_date1,'company_id':val.company_id and val.company_id.id or False,'department_id':val.department_id and val.department_id.id or False,'method':'Manual' })
                            
                            print "=========================NEW EMPLOYEE IN ATTENDANCE IS CREATED=========================",att_in_id
                            
                            att_out_id = att_obj.create(cr, uid, {'name' : out_time, 'employee_id' : val.id ,'day':each.name,'month':str(month),'year_id':year_id and year_id[0] or False,
                                                     'search_date':search_date1,'company_id':val.company_id and val.company_id.id or False,'department_id':val.department_id and val.department_id.id or False,'method':'Manual' })
                            
                            print "=========================NEW EMPLOYEE OUT ATTENDANCE IS CREATED=========================",att_out_id
                        else:
                            raise osv.except_osv(_('Warning !'),_("Employee %s is Present on %s") %(val.name,each.name))
                elif each.name and each.till_date :
                    start_date = datetime.strptime(each.name,'%Y-%m-%d')
                    end_date = datetime.strptime(each.till_date,'%Y-%m-%d')
                    while (start_date <= end_date):   
                        s_date = start_date.strftime('%Y-%m-%d')
                        tm_tuple = datetime.strptime(s_date,'%Y-%m-%d').timetuple()
                        month = tm_tuple.tm_mon
                        year = tm_tuple.tm_year        
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                        for val in emp_ids:
                            rec_data = self.pool.get('hr.attendance').search(cr, uid, (['search_date','=',start_date],['employee_id','=',val.id]))
                            if len(rec_data) == 0:
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',start_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',start_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to attendance date." % (val.name)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, s_date, line.from_time, line.to_time)
                                in_time = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S')
                                out_time = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                                search_date1 = in_time.strftime("%Y-%m-%d")
                                search_date2 = out_time.strftime("%Y-%m-%d")
                                in_temp = random.randrange(3,9)
                                out_temp = random.randrange(1,5)
                                in_time = in_time - timedelta(hours=0,minutes=in_temp)
                                in_time = in_time - timedelta(hours=5,minutes=30)
                                out_time = out_time + timedelta(hours=0,minutes=out_temp)
                                out_time = out_time - timedelta(hours=5,minutes=30)
                                att_in_id = att_obj.create(cr, uid, {'name' : in_time, 'employee_id' : val.id , 'month':str(month),'day':s_date,'year_id':year_id and year_id[0] or False,
                                                         'search_date':search_date1,'company_id':val.company_id and val.company_id.id or False,'department_id':val.department_id and val.department_id.id or False,'method':'Manual' })
                                
                                print "=========================NEW EMPLOYEE IN ATTENDANCE IS CREATED=====1====================",att_in_id
                                
                                att_out_id = att_obj.create(cr, uid, {'name' : out_time, 'employee_id' : val.id ,'day':s_date,'month':str(month),'year_id':year_id and year_id[0] or False,
                                                         'search_date':search_date1,'company_id':val.company_id and val.company_id.id or False,'department_id':val.department_id and val.department_id.id or False,'method':'Manual' })
                                
                                print "=========================NEW EMPLOYEE OUT ATTENDANCE IS CREATED=====2====================",att_out_id
                            else:
                                raise osv.except_osv(_('Warning !'),_("Employee %s is Present on %s") %(val.name,start_date))
                        start_date += timedelta(days=1)

            else :
                if each.name and not each.till_date :
                    tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
                    month = tm_tuple.tm_mon
                    year = tm_tuple.tm_year        
                    year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                    for val in emp_ids:
                        rec_data = self.pool.get('hr.attendance').search(cr, uid, (['search_date','=',each.name],['employee_id','=',val.id]))
                        if len(rec_data) == 0:
                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',each.name)], limit=1, order='name DESC')
                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',each.name)], limit=1, order='name ASC')
                            if prev_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                            elif next_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to attendance date." % (val.name)))
                            if shift_data:
                                for line in shift_data.shift_id.shift_line:
                                    timing = self.calculate_time(cr, uid, ids, each.name, line.from_time, line.to_time)
                            in_time = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S')
                            out_time = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                            search_date1 = in_time.strftime("%Y-%m-%d")
                            search_date2 = out_time.strftime("%Y-%m-%d")
                            in_temp = random.randrange(0,5)
                            out_temp = random.randrange(0,5)
                            in_time = in_time + timedelta(hours=0,minutes=in_temp)
                            in_time = in_time - timedelta(hours=5,minutes=30)
                            out_time = out_time + timedelta(hours=0,minutes=out_temp)
                            out_time = out_time - timedelta(hours=5,minutes=30)
                            att_in_id = att_obj.create(cr, uid, {'name' : in_time, 'employee_id' : val.id ,'day':each.name,'month':str(month),'year_id':year_id and year_id[0] or False,
                                                         'search_date':search_date1,'company_id':val.company_id and val.company_id.id or False,'department_id':val.department_id and val.department_id.id or False,'method':'Manual' })
                            
                            print "=========================NEW EMPLOYEE IN ATTENDANCE IS CREATED=========================",att_in_id
                            
                            att_out_id = att_obj.create(cr, uid, {'name' : out_time, 'employee_id' : val.id ,'day':each.name,'month':str(month),'year_id':year_id and year_id[0] or False,
                                                     'search_date':search_date1,'company_id':val.company_id and val.company_id.id or False,'department_id':val.department_id and val.department_id.id or False,'method':'Manual' })
                            
                            print "=========================NEW EMPLOYEE OUT ATTENDANCE IS CREATED=========================",att_out_id
                        else:
                            raise osv.except_osv(_('Warning !'),_("Employee %s is Present on %s") %(val.name,each.name))
                elif each.name and each.till_date :
                    start_date = datetime.strptime(each.name,'%Y-%m-%d')
                    end_date = datetime.strptime(each.till_date,'%Y-%m-%d') 
                    while (start_date <= end_date):   
                        s_date = start_date.strftime('%Y-%m-%d')
                        tm_tuple = datetime.strptime(s_date,'%Y-%m-%d').timetuple()
                        month = tm_tuple.tm_mon
                        year = tm_tuple.tm_year        
                        year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
                        for val in emp_ids:
                            rec_data = self.pool.get('hr.attendance').search(cr, uid, (['search_date','=',start_date],['employee_id','=',val.id]))
                            if len(rec_data) == 0:
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',start_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',start_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to attendance date." % (val.name)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, s_date, line.from_time, line.to_time)
                                in_time = datetime.strptime(timing['start_time'],'%Y-%m-%d %H:%M:%S')
                                out_time = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                                search_date1 = in_time.strftime("%Y-%m-%d")
                                search_date2 = out_time.strftime("%Y-%m-%d")
                                in_temp = random.randrange(0,5)
                                out_temp = random.randrange(0,5)
                                in_time = in_time + timedelta(hours=0,minutes=in_temp)
                                in_time = in_time - timedelta(hours=5,minutes=30)
                                out_time = out_time + timedelta(hours=0,minutes=out_temp)
                                out_time = out_time - timedelta(hours=5,minutes=30)
                                att_in_id = att_obj.create(cr, uid, {'name' : in_time, 'employee_id' : val.id , 'month':str(month),'day':s_date,'year_id':year_id and year_id[0] or False,
                                                         'search_date':search_date1,'company_id':val.company_id and val.company_id.id or False,'department_id':val.department_id and val.department_id.id or False,'method':'Manual' })
                                
                                print "=========================NEW EMPLOYEE IN ATTENDANCE IS CREATED=========================",att_in_id
                                
                                att_out_id = att_obj.create(cr, uid, {'name' : out_time, 'employee_id' : val.id ,'day':s_date,'month':str(month),'year_id':year_id and year_id[0] or False,
                                                         'search_date':search_date1,'company_id':val.company_id and val.company_id.id or False,'department_id':val.department_id and val.department_id.id or False,'method':'Manual' })
                                
                                print "=========================NEW EMPLOYEE OUT ATTENDANCE IS CREATED=========================",att_out_id
                            else:
                                raise osv.except_osv(_('Warning !'),_("Employee %s is Present on %s") %(val.name,start_date))
                        start_date += timedelta(days=1)
                        
                        
    def compute_attendance11(self, cr, uid, ids, context=None):
        for each in self.pool.get('wiz.create.att').browse(cr, uid, ids):
            if each.name and each.till_date and each.employee_id:
                list_ids = self.pool.get('hr.employee').search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True)])
                
            emp_ids = self.pool.get('hr.employee').browse(cr, uid, list_ids)
            b = emp_ids.week.upper()[0:2]
            for val in emp_ids:
                start_date = datetime.strptime(each.name,'%Y-%m-%d')
                end_date = datetime.strptime(each.till_date,'%Y-%m-%d')
                s_date = start_date.strftime('%Y-%m-%d')
                tm_tuple = datetime.strptime(s_date,'%Y-%m-%d').timetuple()
                month = tm_tuple.tm_mon
                year = tm_tuple.tm_year
                start = tm_tuple.tm_mday
                e_date = end_date.strftime('%Y-%m-%d')
                tm_tuple1 = datetime.strptime(e_date,'%Y-%m-%d').timetuple()
                end = tm_tuple1.tm_mday
                
                before=datetime(year,month,start)
                after=datetime(year,month,end)
                if val.week.upper()[0:2]=='SU':
                    rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.SU,dtstart=before)
                    week_off_lst = rr.between(before,after,inc=True) 
                elif val.week.upper()[0:2]=='MO':
                    rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.MO,dtstart=before)
                    week_off_lst = rr.between(before,after,inc=True)
                elif val.week.upper()[0:2]=='TU':
                    rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.TU,dtstart=before)
                    week_off_lst = rr.between(before,after,inc=True)
                elif val.week.upper()[0:2]=='WE':
                    rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.WE,dtstart=before)
                    week_off_lst = rr.between(before,after,inc=True)
                elif val.week.upper()[0:2]=='TH':
                    rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.TH,dtstart=before)
                    week_off_lst = rr.between(before,after,inc=True)
                elif val.week.upper()[0:2]=='FR':
                    rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.FR,dtstart=before)
                    week_off_lst = rr.between(before,after,inc=True)
                elif val.week.upper()[0:2]=='SA':
                    rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.SA,dtstart=before)
                    week_off_lst = rr.between(before,after,inc=True)
                    
                while (start_date <= end_date):   
                    if week_off_lst:
                        for vall in week_off_lst:
                            week_day = vall.strftime('%Y-%m-%d')
                            atten_id = self.pool.get('hr.attendance').search(cr, uid, (['search_date','=',week_day],['employee_id','=',val.id]))
                            if atten_id:
                                for atten  in self.pool.get('hr.attendance').browse(cr, uid, atten_id):
                                    cr.execute("delete from hr_attendance where id='"+str(atten.id)+"'  and employee_id = '"+str(val.id)+"'")
                                    
                    start_date += timedelta(days=1)
                        
                        
