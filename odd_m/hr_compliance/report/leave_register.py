import time
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp  import api ,models
from dateutil import rrule
import calendar

class leave_register(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(leave_register, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.count1=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_sequence1":self.get_sequence1,
                                  "get_time":self.get_time,
                                  "get_data":self.get_data,
                                  })
    
    def get_time(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
        return date1
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_sequence1(self):
        self.count1=self.count1+1
        return self.count1
          
    def get_data(self,from_month_id,till_month_id,company_id,employee_id,department_id) :
        l = []
        list_ids = [] 
        list_month = []
        
        from_month_browse = self.pool.get('holiday.list').browse(self.cr, 1, from_month_id.id)
        from_month = int(from_month_browse.month)
        from_year = int(from_month_browse.year_id.name)
        
        till_month_browse = self.pool.get('holiday.list').browse(self.cr, 1, till_month_id.id)
        till_month = int(till_month_browse.month)
        till_year = int(till_month_browse.year_id.name)
        
        if (from_month == till_month) and (from_year == till_year) :
            q =  self.cr.execute("select hl.id from holiday_list as hl left join holiday_year as hy on (hl.year_id=hy.id) "
                                 "where hl.month='"+str(from_month)+"' and hy.name='"+str(from_year)+"'  " )
            t = self.cr.fetchall()
            list_month.append(t[0][0])
        elif from_year==till_year :
            while(from_month<=till_month) :
                q =  self.cr.execute("select hl.id from holiday_list as hl left join holiday_year as hy on (hl.year_id=hy.id) "
                                     "where hl.month='"+str(from_month)+"' and hy.name='"+str(from_year)+"'  " )
                t = self.cr.fetchall()
                list_month.append(t[0][0])
                from_month += 1
        else :
            while(from_year<=till_year) :        
                if from_year < till_year :
                    while(from_year!=till_year) :
                        q =  self.cr.execute("select hl.id from holiday_list as hl left join holiday_year as hy on (hl.year_id=hy.id) "
                                             "where hl.month='"+str(from_month)+"' and hy.name='"+str(from_year)+"'  " )
                        t = self.cr.fetchall()
                        list_month.append(t[0][0])
                        if from_month == 12 :
                            from_month = 1
                            from_year += 1
                        else :
                            from_month += 1
                if from_year==till_year :
                    while(from_month<=till_month) :
                        q =  self.cr.execute("select hl.id from holiday_list as hl left join holiday_year as hy on (hl.year_id=hy.id) "
                                             "where hl.month='"+str(from_month)+"' and hy.name='"+str(from_year)+"'  " )
                        t = self.cr.fetchall()
                        list_month.append(t[0][0])
                        from_month += 1
                    from_year += 1
                
        if len(list_month) == 0 :
            raise osv.except_osv(('Warning !'),("Please enter from month & till month correctly !!!"))
                        
        emp_obj = self.pool.get('hr.employee')
        if employee_id and department_id and company_id :
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee_id.id),('department_id', '=', department_id.id),('active','=',True),('company_id','=',company_id.id),('type','=','Employee')])
        elif employee_id and company_id :
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee_id.id),('active','=',True),('company_id','=',company_id.id),('type','=','Employee')])
        elif department_id and company_id :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department_id.id),('active','=',True),('company_id','=',company_id.id),('type','=','Employee')])
        elif company_id :
            list_ids = emp_obj.search(self.cr, 1, [('active','=',True),('company_id','=',company_id.id),('type','=','Employee')])
        elif employee_id :
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee_id.id),('active','=',True),('type','=','Employee')])
        elif department_id :
            raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
        else:
            list_ids = emp_obj.search(self.cr, 1, [('active','=',True),('type','=','Employee')])
        
        for emp in list_ids :
            l1 = []
            l2 = []
            l3 = []
            seq = 0
            total_present = 0
            total_el = 0
            total_cl = 0
            total_sl = 0
            total_day = 0
            department = ''
            doj = ''
            dod = ''
            f_name = ''
            emp_obj = self.pool.get('hr.employee')
            emp_browse = emp_obj.browse(self.cr, 1, emp)
            department = emp_browse.department_id.name 
            doj = emp_browse.doj
            company = emp_browse.company_id.name
            sinid = emp_browse.sinid
            emp_name = emp_browse.name
            last_earn_date = emp_browse.earn_date
            
            query1 = self.cr.execute("select name from family where employee_id='"+str(emp)+"' and relation='Father'  ")
            temp1  = self.cr.fetchall()
            if temp1 :
                f_name = temp1[0][0]        
                    
            query2 = self.cr.execute("select name from hr_active_history where employee_id='"+str(emp)+"' order by date desc limit 1 ")
            temp2 = self.cr.fetchall()
            if temp2 :
                if temp2[0][0] == 'In Active' :
                    dod = temp2[0][0]
            
            l1.append(department)
            l1.append(doj)
            l1.append(company)
            l1.append(sinid)
            l1.append(emp_name)
            l1.append(f_name)
            l1.append(dod)
            
            for month_id in list_month :
                tup1 = ()
                opening_bal = '-'
                monthly_earn_leave = '-'
                basic = 0
                gross = 0
                p_count = 0
                curr_earn = 0
                el_date_lst = []
                cl_date_lst = []
                sl_date_lst = []
                el_dates = ''
                cl_dates = ''
                sl_dates = ''
                cl_sl_dates = ''
                month_browse = self.pool.get('holiday.list').browse(self.cr, 1, month_id)
                period = month_browse.name[0:3] + '-' + month_browse.year_id.name[2:4]
                month = int(month_browse.month)
                year = int(month_browse.year_id.name)
                seq = year
                start_date = str(year) + '-' + str(month) + '-' + '01'
                month_tup = calendar.monthrange(year,month)
                end_date = str(year) + '-' + str(month) + '-' + str(month_tup[1])
                
                
                start_date = datetime.strptime(start_date,"%Y-%m-%d")
                end_date = datetime.strptime(end_date,"%Y-%m-%d")
                                
                if month_browse.month == '1' :
                    opening_date = str(year) + '-01-01'
                    que1 = self.cr.execute("select earn_leave from hr_employee where id='"+str(emp)+"' ")
                    tmp1 = self.cr.fetchall()
                    if tmp1 :
                        opening_bal = tmp1[0][0]
#                        print " opening bal sabse pahela=================================",opening_bal    
                    
                    que2 = self.cr.execute("select sum(curr_earn-prev_earn) from earn_leave_history where employee_id='"+str(emp)+"' and name >= '"+str(opening_date)+"'  ")
                    tmp2 = self.cr.fetchall()
                    print "tmp2==============",tmp2
                    if tmp2 and tmp2[0][0] != None :
                        opening_bal = opening_bal - tmp2[0][0]
#                        print " opening bal 2=================================",opening_bal 
                    
                    que3 = self.cr.execute("select sum(hol.number_of_days_temp) from hr_holidays as hol left join hr_holidays_status as hol_status on (hol.holiday_status_id=hol_status.id) where hol.employee_id='"+str(emp)+"' and hol.from_date >= '"+str(opening_date)+"' and hol_status.name='Earned Leaves' and hol.state='validate' and hol.type='remove' ")  
                    tmp3 = self.cr.fetchall()
                    print "tmp3============",tmp3
                    if tmp3 and tmp3[0][0] != None :
                        opening_bal = opening_bal + tmp3[0][0]
#                        print " opening bal 3=================================",opening_bal
                    if opening_bal > 30 :
                          opening_bal=30
               
                earn_month = month_browse.month
                if len(earn_month) == 1 :
                    earn_month = '0' + earn_month
                earn_year = month_browse.year_id.name
                que4 = self.cr.execute("select sum(curr_earn-prev_earn) from earn_leave_history where employee_id='"+str(emp)+"' and extract(month from name) = '"+str(earn_month)+"' and extract(year from name) = '"+str(earn_year)+"' ")
                tmp4 = self.cr.fetchall()
                if tmp4 and tmp4[0][0] != None :
                    monthly_earn_leave = tmp4[0][0]
                
#                 query3 = self.cr.execute("select curr_earn from earn_leave_history where employee_id='"+str(emp)+"' and name <= '"+str(end_date)+"' order by name desc limit 1 ")
#                 temp3 = self.cr.fetchall()

                query3 = self.cr.execute("select earn_leave from hr_employee where id='"+str(emp)+"' ")
                temp3 = self.cr.fetchall()
                if temp3 :
                    curr_earn = temp3[0][0]
                
                query4 = self.cr.execute("select sum(curr_earn-prev_earn) from earn_leave_history where employee_id='"+str(emp)+"' and name > '"+str(end_date)+"'  ")
                temp4 = self.cr.fetchall()
                if temp4 and temp4[0][0] != None :
                    curr_earn = curr_earn - temp4[0][0]
                
                query5 = self.cr.execute("select sum(hol.number_of_days_temp) from hr_holidays as hol left join hr_holidays_status as hol_status on (hol.holiday_status_id=hol_status.id) where hol.employee_id='"+str(emp)+"' and hol.from_date > '"+str(end_date)+"' and hol_status.name='Earned Leaves' and hol.state='validate' and hol.type='remove' ")  
                temp5 = self.cr.fetchall()
                if temp5 and temp5[0][0] != None :
                    curr_earn = curr_earn + temp5[0][0]
                
                q1 = self.cr.execute("select days_amount,basic from salary_payment_line where employee_id='"+str(emp)+"' and month='"+str(month)+"' and year_id='"+str(month_browse.year_id.id)+"' ")
                t1 = self.cr.fetchall()
                if t1 :
                    gross = t1[0][0] 
                    basic = t1[0][1] 
                                        
                for val_date in rrule.rrule(rrule.DAILY,dtstart=start_date,until=end_date):
                    val_date_str = val_date.strftime('%Y-%m-%d')
                    val_from_date_str = val_date_str + ' 00:00:00'
                    val_till_date_str = val_date_str + ' 23:59:59'
                    q2 = self.cr.execute("select working from attendance_timing where employee_id='"+str(emp)+"' and name='"+str(val_date)+"'  ")
                    t2 = self.cr.fetchall()
                    if t2 :
                        if t2[0][0] == 'P' :
                            p_count += 1
                            total_present += 1
                    if len(t2) == 0  :
                        q3 = self.cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp)+"' and state='validate' and type='remove' ")
                        t3 = self.cr.fetchall()
                        if t3 :    
                            for val1 in t3 :
                                for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                    if leave_date == val_date :
                                        if val1[2] == 'Earned Leaves' : 
                                            el_date = leave_date.strftime('%d')
                                            el_date_lst.append(el_date)
                                        elif val1[2][0:4] == 'Sick' : 
                                            sl_date = leave_date.strftime('%d')
                                            sl_date_lst.append(sl_date)
                                        elif val1[2][0:4] == 'Casu' : 
                                            cl_date = leave_date.strftime('%d')
                                            cl_date_lst.append(cl_date)
                
#                 curr_earn = curr_earn - len(el_date_lst)
                total_el += len(el_date_lst)
                total_cl += len(cl_date_lst)
                total_sl += len(sl_date_lst)
                total_day = total_present + total_el
                                   
                if el_date_lst :
                    if len(el_date_lst) == 1 :
                        el_dates = el_date_lst[0]
                    else :
                        for el_val in el_date_lst :
                            if el_dates == '' :
                                el_dates = el_val
                            else :
                                el_dates = el_dates + ',' + el_val
                                
                if cl_date_lst :
                    if len(cl_date_lst) == 1 :
                        cl_dates = cl_date_lst[0]
                    else :
                        for cl_val in cl_date_lst :
                            if cl_dates == '' :
                                cl_dates = cl_val
                            else :
                                cl_dates = cl_dates + ',' + cl_val
                                
                if sl_date_lst :
                    if len(sl_date_lst) == 1 :
                        sl_dates = sl_date_lst[0]
                    else :
                        for sl_val in sl_date_lst :
                            if sl_dates == '' :
                                sl_dates = sl_val
                            else :
                                sl_dates = sl_dates + ',' + sl_val
                            
                if cl_dates == '' and sl_dates == '' :
                    cl_sl_dates = ''
                elif cl_dates == '' :
                    cl_sl_dates = sl_dates
                elif sl_dates == '' :
                    cl_sl_dates = cl_dates
                else :
                    cl_sl_dates = cl_dates + ',' + sl_dates
                            
                tup1 = (seq,period, gross, p_count, len(el_date_lst), p_count+len(el_date_lst), opening_bal, monthly_earn_leave, el_dates, curr_earn, basic, len(cl_date_lst), len(sl_date_lst), cl_sl_dates  )    
                l2.append(tup1)    
                    
            l2.append(('', '', 'Total', total_present, total_el, total_day,'', '', '', '', '', total_cl, total_sl, ''))
            l1.append(l2)    
            l.append(l1)
                    
        return l            
                    
    
class report_leave_register(osv.AbstractModel):
    _name = 'report.hr_compliance.report_leave_register'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_leave_register'
    _wrapped_report_class = leave_register

                


#                                              CONTRACTOR LEAVE REGISTER


class contractor_leave_register(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_leave_register, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.count1=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_sequence1":self.get_sequence1,
                                  "get_time":self.get_time,
                                  "get_data":self.get_data,
                                  })
    
    def get_time(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
        return date1
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_sequence1(self):
        self.count1=self.count1+1
        return self.count1
          
    def get_data(self,from_month_id,till_month_id,partner_id,employee_id) :
        l = []
        list_ids = [] 
        list_month = []
        
        from_month_browse = self.pool.get('holiday.list').browse(self.cr, 1, from_month_id.id)
        from_month = int(from_month_browse.month)
        from_year = int(from_month_browse.year_id.name)
        
        till_month_browse = self.pool.get('holiday.list').browse(self.cr, 1, till_month_id.id)
        till_month = int(till_month_browse.month)
        till_year = int(till_month_browse.year_id.name)
        
        if (from_month == till_month) and (from_year == till_year) :
            q =  self.cr.execute("select hl.id from holiday_list as hl left join holiday_year as hy on (hl.year_id=hy.id) "
                                 "where hl.month='"+str(from_month)+"' and hy.name='"+str(from_year)+"'  " )
            t = self.cr.fetchall()
            list_month.append(t[0][0])
        elif from_year==till_year :
            while(from_month<=till_month) :
                q =  self.cr.execute("select hl.id from holiday_list as hl left join holiday_year as hy on (hl.year_id=hy.id) "
                                     "where hl.month='"+str(from_month)+"' and hy.name='"+str(from_year)+"'  " )
                t = self.cr.fetchall()
                list_month.append(t[0][0])
                from_month += 1
        else :
            while(from_year<=till_year) :        
                if from_year < till_year :
                    while(from_year!=till_year) :
                        q =  self.cr.execute("select hl.id from holiday_list as hl left join holiday_year as hy on (hl.year_id=hy.id) "
                                             "where hl.month='"+str(from_month)+"' and hy.name='"+str(from_year)+"'  " )
                        t = self.cr.fetchall()
                        list_month.append(t[0][0])
                        if from_month == 12 :
                            from_month = 1
                            from_year += 1
                        else :
                            from_month += 1
                if from_year==till_year :
                    while(from_month<=till_month) :
                        q =  self.cr.execute("select hl.id from holiday_list as hl left join holiday_year as hy on (hl.year_id=hy.id) "
                                             "where hl.month='"+str(from_month)+"' and hy.name='"+str(from_year)+"'  " )
                        t = self.cr.fetchall()
                        list_month.append(t[0][0])
                        from_month += 1
                    from_year += 1
                
        if len(list_month) == 0 :
            raise osv.except_osv(('Warning !'),("Please enter from month & till month correctly !!!"))
                        
        emp_obj = self.pool.get('hr.employee')
        if employee_id and partner_id:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee_id.id),('partner_id', '=', partner_id.id),('active','=',True),('type','=','Contractor')])
        elif employee_id:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee_id.id),('active','=',True),('type','=','Contractor')])
        elif partner_id:
            list_ids = emp_obj.search(self.cr, 1, [('partner_id', '=', partner_id.id),('active','=',True),('type','=','Contractor')])
        
        for emp in list_ids :
            l1 = []
            l2 = []
            l3 = []
            seq = 0
            total_present = 0
            total_el = 0
            total_cl = 0
            total_sl = 0
            total_day = 0
            department = ''
            doj = ''
            dod = ''
            f_name = ''
            emp_obj = self.pool.get('hr.employee')
            emp_browse = emp_obj.browse(self.cr, 1, emp)
            doj = emp_browse.doj
            sinid = emp_browse.sinid
            emp_name = emp_browse.name
            last_earn_date = emp_browse.earn_date
            company = emp_browse.company_id.name
            department = emp_browse.department_id.name 
            
            query1 = self.cr.execute("select name from family where employee_id='"+str(emp)+"' and relation='Father'  ")
            temp1  = self.cr.fetchall()
            if temp1 :
                f_name = temp1[0][0]        
                    
            query2 = self.cr.execute("select name from hr_active_history where employee_id='"+str(emp)+"' order by date desc limit 1 ")
            temp2 = self.cr.fetchall()
            if temp2 :
                if temp2[0][0] == 'In Active' :
                    dod = temp2[0][0]
            
            l1.append(department)
            l1.append(doj)
            l1.append(company)
            l1.append(sinid)
            l1.append(emp_name)
            l1.append(f_name)
            l1.append(dod)

            for month_id in list_month :
                tup1 = ()
                opening_bal = '-'
                monthly_earn_leave = '-'
                basic = 0
                gross = 0
                p_count = 0
                curr_earn = 0
                el_date_lst = []
                cl_date_lst = []
                sl_date_lst = []
                el_dates = ''
                cl_dates = ''
                sl_dates = ''
                cl_sl_dates = ''
                month_browse = self.pool.get('holiday.list').browse(self.cr, 1, month_id)
                period = month_browse.name[0:3] + '-' + month_browse.year_id.name[2:4]
                month = int(month_browse.month)
                year = int(month_browse.year_id.name)
                seq = year
                start_date = str(year) + '-' + str(month) + '-' + '01'
                month_tup = calendar.monthrange(year,month)
                end_date = str(year) + '-' + str(month) + '-' + str(month_tup[1])
                
                
                start_date = datetime.strptime(start_date,"%Y-%m-%d")
                end_date = datetime.strptime(end_date,"%Y-%m-%d")
                                
                if month_browse.month == '1' :
                    opening_date = str(year) + '-01-01'
                    que1 = self.cr.execute("select earn_leave from hr_employee where id='"+str(emp)+"' ")
                    tmp1 = self.cr.fetchall()
                    if tmp1 :
                        opening_bal = tmp1[0][0]
#                        print " opening bal sabse pahela=================================",opening_bal    
                    
                    que2 = self.cr.execute("select sum(curr_earn-prev_earn) from earn_leave_history where employee_id='"+str(emp)+"' and name >= '"+str(opening_date)+"'  ")
                    tmp2 = self.cr.fetchall()
                    if tmp2 and tmp2[0][0] != None :
                        opening_bal = opening_bal - tmp2[0][0]
#                        print " opening bal 2=================================",opening_bal 
                    
                    que3 = self.cr.execute("select sum(hol.number_of_days_temp) from hr_holidays as hol left join hr_holidays_status as hol_status on (hol.holiday_status_id=hol_status.id) where hol.employee_id='"+str(emp)+"' and hol.from_date >= '"+str(opening_date)+"' and hol_status.name='Earned Leaves' and hol.state='validate' and hol.type='remove' ")  
                    tmp3 = self.cr.fetchall()
                    if tmp3 and tmp3[0][0] != None :
                        opening_bal = opening_bal + tmp3[0][0]
                    if opening_bal > 30 :
                          opening_bal=30    
                        
#                        print " opening bal 3=================================",opening_bal  
                
                earn_month = month_browse.month
                if len(earn_month) == 1 :
                    earn_month = '0' + earn_month
                earn_year = month_browse.year_id.name
                que4 = self.cr.execute("select sum(curr_earn-prev_earn) from earn_leave_history where employee_id='"+str(emp)+"' and extract(month from name) = '"+str(earn_month)+"' and extract(year from name) = '"+str(earn_year)+"' ")
                tmp4 = self.cr.fetchall()
                if tmp4 and tmp4[0][0] != None :
                    monthly_earn_leave = tmp4[0][0]
                
#                 query3 = self.cr.execute("select curr_earn from earn_leave_history where employee_id='"+str(emp)+"' and name <= '"+str(end_date)+"' order by name desc limit 1 ")
#                 temp3 = self.cr.fetchall()

                query3 = self.cr.execute("select earn_leave from hr_employee where id='"+str(emp)+"' ")
                temp3 = self.cr.fetchall()
                if temp3 :
                    curr_earn = temp3[0][0]
                
                query4 = self.cr.execute("select sum(curr_earn-prev_earn) from earn_leave_history where employee_id='"+str(emp)+"' and name > '"+str(end_date)+"'  ")
                temp4 = self.cr.fetchall()
                if temp4 and temp4[0][0] != None :
                    curr_earn = curr_earn - temp4[0][0]
                
                query5 = self.cr.execute("select sum(hol.number_of_days_temp) from hr_holidays as hol left join hr_holidays_status as hol_status on (hol.holiday_status_id=hol_status.id) where hol.employee_id='"+str(emp)+"' and hol.from_date > '"+str(end_date)+"' and hol_status.name='Earned Leaves' and hol.state='validate' and hol.type='remove' ")  
                temp5 = self.cr.fetchall()
                if temp5 and temp5[0][0] != None :
                    curr_earn = curr_earn + temp5[0][0]
                
                q1 = self.cr.execute("select days_amount,basic from salary_payment_line where employee_id='"+str(emp)+"' and month='"+str(month)+"' and year_id='"+str(month_browse.year_id.id)+"' ")
                t1 = self.cr.fetchall()
                if t1 :
                    gross = t1[0][0] 
                    basic = t1[0][1] 
                                        
                for val_date in rrule.rrule(rrule.DAILY,dtstart=start_date,until=end_date):
                    val_date_str = val_date.strftime('%Y-%m-%d')
                    val_from_date_str = val_date_str + ' 00:00:00'
                    val_till_date_str = val_date_str + ' 23:59:59'
                    q2 = self.cr.execute("select working from attendance_timing where employee_id='"+str(emp)+"' and name='"+str(val_date)+"'  ")
                    t2 = self.cr.fetchall()
                    if t2 :
                        if t2[0][0] == 'P' :
                            p_count += 1
                            total_present += 1
                    if len(t2) == 0  :
                        q3 = self.cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp)+"' and state='validate' and type='remove' ")
                        t3 = self.cr.fetchall()
                        if t3 :    
                            for val1 in t3 :
                                for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                    if leave_date == val_date :
                                        if val1[2] == 'Earned Leaves' : 
                                            el_date = leave_date.strftime('%d')
                                            el_date_lst.append(el_date)
                                        elif val1[2][0:4] == 'Sick' : 
                                            sl_date = leave_date.strftime('%d')
                                            sl_date_lst.append(sl_date)
                                        elif val1[2][0:4] == 'Casu' : 
                                            cl_date = leave_date.strftime('%d')
                                            cl_date_lst.append(cl_date)
                
#                 curr_earn = curr_earn - len(el_date_lst)
                total_el += len(el_date_lst)
                total_cl += len(cl_date_lst)
                total_sl += len(sl_date_lst)
                total_day = total_present + total_el
                                   
                if el_date_lst :
                    if len(el_date_lst) == 1 :
                        el_dates = el_date_lst[0]
                    else :
                        for el_val in el_date_lst :
                            if el_dates == '' :
                                el_dates = el_val
                            else :
                                el_dates = el_dates + ',' + el_val
                                
                if cl_date_lst :
                    if len(cl_date_lst) == 1 :
                        cl_dates = cl_date_lst[0]
                    else :
                        for cl_val in cl_date_lst :
                            if cl_dates == '' :
                                cl_dates = cl_val
                            else :
                                cl_dates = cl_dates + ',' + cl_val
                                
                if sl_date_lst :
                    if len(sl_date_lst) == 1 :
                        sl_dates = sl_date_lst[0]
                    else :
                        for sl_val in sl_date_lst :
                            if sl_dates == '' :
                                sl_dates = sl_val
                            else :
                                sl_dates = sl_dates + ',' + sl_val
                            
                if cl_dates == '' and sl_dates == '' :
                    cl_sl_dates = ''
                elif cl_dates == '' :
                    cl_sl_dates = sl_dates
                elif sl_dates == '' :
                    cl_sl_dates = cl_dates
                else :
                    cl_sl_dates = cl_dates + ',' + sl_dates
                            
                tup1 = (seq,period, gross, p_count, len(el_date_lst), p_count+len(el_date_lst), opening_bal, monthly_earn_leave, el_dates, curr_earn, basic, len(cl_date_lst), len(sl_date_lst), cl_sl_dates  )    
                l2.append(tup1)    
                    
            l2.append(('', '', 'Total', total_present, total_el, total_day,'', '', '', '', '', total_cl, total_sl, ''))
            l1.append(l2)    
            l.append(l1)
        print"=====llllllll=====",l            
        return l            
                    
    
class report_contractor_leave_register(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_leave_register'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_leave_register'
    _wrapped_report_class = contractor_leave_register

