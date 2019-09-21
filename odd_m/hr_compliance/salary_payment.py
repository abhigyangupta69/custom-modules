from openerp.osv import fields, osv
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
import re 
import base64, urllib
import os
from openerp.tools.translate import _
from datetime import datetime,timedelta
from openerp.addons.decimal_precision import decimal_precision as dp
import math
import csv
import cStringIO
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, Alignment,  easyxf
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import dateutil.relativedelta as relativedelta
import dateutil.rrule as rrule

class salary_payment(osv.osv):
    _name = 'salary.payment'
    
    def _calculate_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr, uid, ids):
            res[val.id] = val.month and val.month.name or False
        return res
    
    def _create_emp_lines(self, val):
        return  {
                   'employee_id':val.id,
                   'department_id':val.department_id and val.department_id.id or False,
                   'basic':val.salary,
               }
    
    def _get_all_employee(self, cr, uid, context=None):
        
        lines = []
        emp_obj = self.pool.get('hr.employee')
        emp_ids = emp_obj.search(cr, uid, [('active','=',True)])
        for val in emp_obj.browse(cr, uid, emp_ids):
            lines.append(self._create_emp_lines(val))
        return lines
    
    
    def calculate_loan_balance(self, cr, uid, ids, context=None):
        sal_line_obj=self.pool.get('salary.payment.line')
        loan_line_obj=self.pool.get('loan.deduction.line')
        for each in self.browse(cr, uid, ids):
            month = int(each.month.month)
            year = int(each.month.year_id.name)
            if month == 12:
                year += 1
                month = 0
            month += 1
            check_date = str(year)+'-'+str(month)+'-20'
            if datetime.strptime(check_date,'%Y-%m-%d') < datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),'%Y-%m-%d'):
                for line in each.salary_payment_line:
                    if line.salary_type == 'Salary':
                        cr.execute("select line.id from loan_deduction_line as line left join loan_deduction as " \
                                   "loan on (line.loan_deduct_id = loan.id) left join holiday_list as holi on (line.loan_id = holi.id) " \
                                   "where holi.month='"+str(each.month.month)+"' and holi.year_id='"+str(each.month.year_id.id)+"' and loan.emp_id='"+str(line.employee_id.id)+"' and line.state='not_paid'")

                        temp = cr.fetchall()
                        for data in temp:
                            if data and data[0] != None:
                                print "<------------------- EMI CALCULATION FOR EMPLOYEE ------------->",line.employee_id.name
                                loan_line_obj.balance_paid(cr, uid, [data[0]], context)
                                sal_line_obj.write(cr, uid, [line.id], {'state':'Paid'})
                                
                    
            else:
                raise osv.except_osv(_('Warning !'),_("You cannot deduct loan EMI, to do so please wait till date 20."))
        return True
    
    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False

    _columns = {
                'name':fields.function(_calculate_name,method=True,store=True,string='Name',type='char',size=64),
                'month':fields.many2one('holiday.list','Month',required=True),
                'year_id':fields.many2one('holiday.year','Year',required=True),
                'salary_payment_line':fields.one2many('salary.payment.line','salary_id','Holiday Lines'),
                'salary_type':fields.selection([('Salary','Salary')],'Salary Type',required=True),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'company_id':fields.many2one('res.company','Company'),
                'salary_payment_line_manual':fields.one2many('salary.payment.line.manual','salary_id','Manual Lines'),
                'manual_sheet':fields.boolean('Other'),
                'user_id':fields.many2one('res.users',string='User'),
                'employment_type':fields.selection([('Employee','Employee'),('Labor','Labor'),('Trainee','Trainee')],'Employment Type'),
                'type':fields.selection([('Employee','Employee'),('Contractor','Contractor')],'Type'),
                }
    
    _defaults = {
                 'salary_type':'Salary',
                 'company_id' : _get_company_id,
                 'user_id' : lambda obj, cr, uid, context: uid,
                 }

    _sql_constraints = [('unique_month_year','unique(month,year_id,salary_type)','Salary payment for this month & year is already define.')]
    
    def onchange_month(self, cr, uid, ids, month, context=None):
        res = {}
        if not month:
            res['value'] = {'year_id':False}
            return res
        month_obj = self.pool.get('holiday.list')
        month_data = month_obj.browse(cr, uid, month)
        if not month_data.year_id:
            res['warning'] = {'title': _('Warning'), 'message': _('Unable to process request, year is not selected in month.')}
        res['value'] = {'year_id':month_data.year_id and month_data.year_id.id or False}
        return res
    
    def calculate_payment(self, cr, uid, ids, context=None):
        res = {}
        emp_obj = self.pool.get('hr.employee')
        shift_obj = self.pool.get('hr.shift.line')
        att_obj = self.pool.get('attendance.timing')
        salline_obj = self.pool.get('salary.payment.line')
        counter = 1
        month = off_day = sunday = off_day1 = sunday1 = holiday = 0
        for line in self.browse(cr, uid, ids):
            emp_ids = []
            neg_sunday_lst = []
            if line.manual_sheet:
                for manual in line.salary_payment_line_manual:
                    emp_ids.append(manual.employee_id.id)
            elif line.company_id and line.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False),('company_id','=',line.company_id.id),('employment_type','=',line.employment_type)])
            elif line.company_id:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False),('company_id','=',line.company_id.id)])
            elif line.employee_id:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False),('id','=',line.employee_id.id)])
#            elif line.employment_type:
#                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False),('employment_type','=',line.employment_type)])
            else:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False)])
            if int(line.month.month) in [1,3,5,7,8,10,12]:
                month = 31
            if int(line.month.month) in [4,6,9,11]:
                month = 30
            if int(line.month.month) in [2]:
                if int(line.month.year_id.name) % 4 == 0:
                    month = 29
                else:
                    month = 28
            start_date = str(line.month.year_id.name)+'-'+str(line.month.month)+'-01'
            end_date = str(line.month.year_id.name)+'-'+str(line.month.month)+'-'+str(month)
                       
#            cr.execute("select max(name) from attendance_timing where DATE_PART('MONTH',name)='"+str(line.month.month)+"' and DATE_PART('YEAR',name)='"+str(line.month.year_id.name)+"'") 
#            temp_day = cr.fetchall()
#            for dval in temp_day:
#                if dval and dval[0] != None:
#                    end_date = dval[0]
#            print"end_date =-=-=-=-=-=-=------------------------------------------------",end_date
            new_wk_day = wk_day = 0
            
            if datetime.strptime(end_date,"%Y-%m-%d").date() >= datetime.strptime(start_date,"%Y-%m-%d").date():
                new_wk_day = datetime.strptime(end_date,"%Y-%m-%d").date() - datetime.strptime(start_date,"%Y-%m-%d").date() 
                new_wk_day = new_wk_day.days
                if new_wk_day >= 28:
                    new_wk_day = new_wk_day + 1 
            
            for val in emp_obj.browse(cr, uid, emp_ids):
                start_dat = datetime.strptime(start_date,'%Y-%m-%d')
                end_dat = datetime.strptime(end_date,'%Y-%m-%d')
                s_date = start_dat.strftime('%Y-%m-%d')
                tm_tuple = datetime.strptime(s_date,'%Y-%m-%d').timetuple()
                month1 = tm_tuple.tm_mon
                year1 = tm_tuple.tm_year
                start1 = tm_tuple.tm_mday
                e_date = end_dat.strftime('%Y-%m-%d')
                tm_tuple1 = datetime.strptime(e_date,'%Y-%m-%d').timetuple()
                end1 = tm_tuple1.tm_mday
                
                before=datetime(year1,month1,start1)
                after=datetime(year1,month1,end1)
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
#                print"week_off_lst ==================",week_off_lst
                sunday = 0
                off_day = 0
                neg_sunday = 0
                neg_sunday_tup = ()
                next_date = datetime.strptime(start_date,"%Y-%m-%d")
                if val.week == 'Sunday':
#                    print"in ifff ==============="
                    for i in range(month):
                        next_date1 = next_date.strftime('%Y-%m-%d')
                        for sun in line.month.holiday_lines:
                            if datetime.strptime(next_date1,"%Y-%m-%d").date() == datetime.strptime(sun.leave_date,"%Y-%m-%d").date():
                               if sun.week == 'Sunday':
                                    sunday += 1
                                    joining = val.doj
                                    prev_day_list  = []
                                    leave_count = 0
                                    joining_count = 0
                                    if sun.leave_date > joining: 
                                        prev_day1 = next_date + timedelta(days=-1)
                                        prev_day1 = prev_day1.strftime('%Y-%m-%d')
                                        prev_day2 = next_date + timedelta(days=-2)
                                        prev_day2 = prev_day2.strftime('%Y-%m-%d')
                                        prev_day3 = next_date + timedelta(days=-3)
                                        prev_day3 = prev_day3.strftime('%Y-%m-%d')
                                        prev_day4 = next_date + timedelta(days=-4)
                                        prev_day4 = prev_day4.strftime('%Y-%m-%d')
                                        prev_day5 = next_date + timedelta(days=-5)
                                        prev_day5 = prev_day5.strftime('%Y-%m-%d')
                                        prev_day6 = next_date + timedelta(days=-6)
                                        prev_day6 = prev_day6.strftime('%Y-%m-%d')
                                        prev_day_tup = (prev_day1,prev_day2,prev_day3,prev_day4,prev_day5,prev_day6)
                                        prev_day_list.append(prev_day_tup)
                                        for prev_day in prev_day_list[0]:
                                            prev_day_strp = datetime.strptime(prev_day,"%Y-%m-%d")
                                            prev_day_month = prev_day_strp.strftime('%m')
                                            prev_day_month = int(prev_day_month)
                                            prev_day_month = str(prev_day_month)
                                            prev_day_year = prev_day_strp.strftime('%Y')
                                            prev_day_year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',prev_day_year)])
                                            prev_day_month_id = self.pool.get('holiday.list').search(cr, uid, [('month','=',prev_day_month),('year_id','=',prev_day_year_id[0])])
                                            if prev_day == joining :
                                                joining_count = 1
                                            cr.execute("select id from holiday_list_lines where leave_date = '"+str(prev_day)+"' ") 
                                            prev_temp_day = cr.fetchall()
                       
                                            if prev_temp_day and prev_day > joining:
                                                leave_count += 1
                                            if not prev_temp_day:
                                                cr.execute("select id from attendance_timing where name = '"+str(prev_day)+"' and working = 'P' and employee_id ='"+str(val.id)+"' ") 
                                                prev_temp_day11 = cr.fetchall()
                                                if prev_temp_day11 :
                                                   leave_count += 1 
                                        
                                            if not prev_temp_day and not prev_temp_day11:
                                                query = cr.execute("select hol.from_date,hol.date_to from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(val.id)+"' and state='validate' and month = "+str(prev_day_month_id[0])+" and type='remove' ")
                                                temp = cr.fetchall()
                                                if temp :    
                                                    for val1 in temp :
                                                        for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                                            leave_date = datetime.strftime(leave_date,"%Y-%m-%d")
                                                            if leave_date == prev_day :
                                                                leave_count += 1
                                        
                                        if leave_count < 4 and joining_count == 0:
                                            neg_sunday += 1
                               
                               else:
                                   off_day += 1
                                 
                                    
                        next_date += timedelta(days=1)
                        wk_day += 1 
#                    print"aman ==========================",neg_sunday,leave_count,joining_count
                    neg_sunday_tup = (val.id,neg_sunday)
                    neg_sunday_lst.append(neg_sunday_tup)

                elif val.week != 'Sunday':
#                    print"in elifff =========================="
                    for i in range(month):
                        next_date1 = next_date.strftime('%Y-%m-%d')
                        for vall in week_off_lst:
                            week_day = vall.strftime('%Y-%m-%d')
                            if datetime.strptime(next_date1,"%Y-%m-%d").date() == datetime.strptime(week_day,"%Y-%m-%d").date():
                                sunday += 1
                                joining = val.doj
                                prev_day_list  = []
                                leave_count = 0
                                joining_count = 0
                                if week_day > joining: 
                                    prev_day1 = next_date + timedelta(days=-1)
                                    prev_day1 = prev_day1.strftime('%Y-%m-%d')
                                    prev_day2 = next_date + timedelta(days=-2)
                                    prev_day2 = prev_day2.strftime('%Y-%m-%d')
                                    prev_day3 = next_date + timedelta(days=-3)
                                    prev_day3 = prev_day3.strftime('%Y-%m-%d')
                                    prev_day4 = next_date + timedelta(days=-4)
                                    prev_day4 = prev_day4.strftime('%Y-%m-%d')
                                    prev_day5 = next_date + timedelta(days=-5)
                                    prev_day5 = prev_day5.strftime('%Y-%m-%d')
                                    prev_day6 = next_date + timedelta(days=-6)
                                    prev_day6 = prev_day6.strftime('%Y-%m-%d')
                                    prev_day_tup = (prev_day1,prev_day2,prev_day3,prev_day4,prev_day5,prev_day6)
                                    prev_day_list.append(prev_day_tup)
                                    for prev_day in prev_day_list[0]:
                                        prev_day_strp = datetime.strptime(prev_day,"%Y-%m-%d")
                                        prev_day_month = prev_day_strp.strftime('%m')
                                        prev_day_month = int(prev_day_month)
                                        prev_day_month = str(prev_day_month)
                                        prev_day_year = prev_day_strp.strftime('%Y')
                                        prev_day_year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',prev_day_year)])
                                        prev_day_month_id = self.pool.get('holiday.list').search(cr, uid, [('month','=',prev_day_month),('year_id','=',prev_day_year_id[0])])
                                        if prev_day == joining :
                                            joining_count = 1
                                        cr.execute("select id from holiday_list_lines where leave_date = '"+str(prev_day)+"' ") 
                                        prev_temp_day = cr.fetchall()
                   
                                        if prev_temp_day and prev_day > joining:
                                            leave_count += 1
                                        if not prev_temp_day:
                                            cr.execute("select id from attendance_timing where name = '"+str(prev_day)+"' and working = 'P' and employee_id ='"+str(val.id)+"' ") 
                                            prev_temp_day11 = cr.fetchall()
                                            if prev_temp_day11 :
                                               leave_count += 1 
                                    
                                        if not prev_temp_day and not prev_temp_day11:
                                            query = cr.execute("select hol.from_date,hol.date_to from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(val.id)+"' and state='validate' and month = "+str(prev_day_month_id[0])+" and type='remove' ")
                                            temp = cr.fetchall()
                                            if temp :    
                                                for val1 in temp :
                                                    for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                                        leave_date = datetime.strftime(leave_date,"%Y-%m-%d")
                                                        if leave_date == prev_day :
                                                            leave_count += 1
                                    
                                    if leave_count < 4 and joining_count == 0:
                                        neg_sunday += 1
                                
                        for sun in line.month.holiday_lines:
                            if datetime.strptime(next_date1,"%Y-%m-%d").date() == datetime.strptime(sun.leave_date,"%Y-%m-%d").date():
                               if sun.week != 'Sunday' and val.week != sun.week:
                                    off_day += 1

                        next_date += timedelta(days=1)
                        wk_day += 1 
#                    print"amanb ==========================",wk_day,off_day,neg_sunday,leave_count,joining_count
                    neg_sunday_tup = (val.id,neg_sunday)
                    neg_sunday_lst.append(neg_sunday_tup)


                
            daily_part =  month - off_day - sunday
#            print"daily_part =========================",daily_part,month,off_day,sunday
#            next_date = datetime.strptime(start_date,"%Y-%m-%d")
#            if line.salary_type == 'Kharcha':
#                off_day = sunday = wk_day = 0
#                new_wk_day = 21
#                end_date = str(line.month.year_id.name)+'-'+str(line.month.month)+'-15'
#            
#                for i in range(new_wk_day):
#                    next_date1 = next_date.strftime('%Y-%m-%d')
#                    for sun in line.month.holiday_lines:
#                        if datetime.strptime(next_date1,"%Y-%m-%d").date() == datetime.strptime(sun.leave_date,"%Y-%m-%d").date():
#                            if sun.week == 'Sunday':
#                                sunday += 1 
#                            else:
#                                off_day += 1
#                    next_date += timedelta(days=1)
#                    wk_day += 1 

            working_day = wk_day - off_day - sunday
#            print"working_day =====================",working_day,wk_day,off_day,sunday
            working_day1 = working_day
            off_day1 = off_day
            sunday1 = sunday
            holiday_date = []
            for leave in line.month.holiday_lines:
                holiday_date.append(leave.leave_date)
#            print"holiday_date ========================",holiday_date
            for val in emp_obj.browse(cr, uid, emp_ids):
#                    print"val ==========================",val
                    working_day = working_day1
                    off_day = off_day1
                    sunday = sunday1
                    emp_sunday = sunday
                    joining = val.doj
                    if joining and datetime.strptime(joining,"%Y-%m-%d").date() > datetime.strptime(start_date,"%Y-%m-%d").date():
                        working_day = 0
                        cur_wk_day = datetime.strptime(end_date,"%Y-%m-%d").date() - datetime.strptime(joining,"%Y-%m-%d").date()
                        if cur_wk_day:
                            working_day = cur_wk_day.days + 1
                            off_day = sunday  = 0
                            for sun in line.month.holiday_lines:
#                                print"sun =====================================",joining,sun.leave_date,end_date
                                
                                if datetime.strptime(joining,"%Y-%m-%d").date() < datetime.strptime(sun.leave_date,"%Y-%m-%d").date() and datetime.strptime(end_date,"%Y-%m-%d").date() >= datetime.strptime(sun.leave_date,"%Y-%m-%d").date():
#                                    print"in iffff -----------------------------------------"
                                    if sun.week == 'Sunday':
                                        sunday += 1
                                    else:
                                        off_day += 1
                            
#                            print"amannnnnnnnnnn =========================",working_day,off_day,sunday
                            working_day = working_day - off_day - sunday
                            
                        else:
                            continue
                           
                    if emp_sunday <> sunday:
                        emp_sunday = sunday

                    hrs = 0
                    att_list = []
                    
#                    hrs = daily = OT_amt = hra = conveyance = medical = allowance = 0.0
                    hrs = daily = OT_amt = other_salary = 0.0
                    total_amount = daily_amt = over_time_amt = sun_over_time_amt =  OT_amt = days = sun_over_time = over_time = work_day = 0.0
                    salary = days = total_days = over_time = sun_over_time = over_time_amt = daily_amt = sun_over_time_amt= work_day = 0.0
#                    hra_amt = conveyance_amt = medical_amt = allowance_amt = total_amounts = 0.0
                    other_salary_amount = total_amounts = 0.0
                    
                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id)], limit=1, order='name DESC')
                    print"aaaaaaaaaaaaaaaa",val.sinid
                    if prev_shift_ids:
                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                        for line1 in shift_data.shift_id.shift_line:
                            hrs = line1.shift_id.shift_line[0].working_time
                            if not hrs:
                                raise osv.except_osv(_('Warning !'),_("Working hours in not define in shift time of employee. "))
                    else:
                        if val.shift_id and val.shift_id.shift_line:
                            hrs = val.shift_id.shift_line[0].working_time
                        if not hrs:
                            raise osv.except_osv(_('Warning !'),_("Working hours in not define in shift time of employee. "))
                                         
                    if val.current_salary:
                        daily = val.current_salary / month
                        OT_amt = ((val.current_salary+val.other_salary) / (26 * 8))

                    if val.other_salary:
                        other_salary = val.other_salary / month
                        
#                    if val.hra:
#                        hra = val.hra / month
#                        
#                    if val.conveyance:
#                        conveyance = val.conveyance / month
#                        
#                    if val.medical:
#                        medical = val.medical / month
#                        
#                    if val.special_allowance:
#                        allowance = val.special_allowance / month
                                            
                    if line.salary_type == 'Salary':
#                            cr.execute("select id from attendance_timing where employee_id ='"+str(val.id)+"' and DATE_PART('MONTH',name)='"+str(line.month.month)+"' and year_id='"+str(line.month.year_id.id)+"' and name <= '"+str(end_date)+"' and (status is null or status in ('A_OK','B_Reduced'))")
#                    else:
                           cr.execute("select id from attendance_timing where employee_id ='"+str(val.id)+"' and DATE_PART('MONTH',name)='"+str(line.month.month)+"' and year_id='"+str(line.month.year_id.id)+"' and name <= '"+str(end_date)+"' and (status is null or status in ('A_OK','B_Reduced'))")
                    
                    temp = cr.fetchall()
                    for data in temp:
                        att_list.append(data[0])
                    
                    for rec in att_obj.browse(cr, uid, att_list):
                        if rec.working == 'P':
                            days += 1
                            total_days += 1
                        elif rec.working == 'POH':
                            days += 0
                            total_days += 0
                        elif rec.working == 'POW':
                            days += 0
                            total_days += 0
                        else:
                            days += 0
                            total_days += 1
                    
                       
                    if line.manual_sheet:
                        for manual in line.salary_payment_line_manual:
                            if manual.employee_id.id==val.id:
                                days = manual.days 
                                total_days = manual.days 
                            
                    start = datetime.strptime(start_date,"%Y-%m-%d")
                    year_val = start.strftime("%Y")
                    casual_val = 'Casual Leaves' + ' ' +str(year_val)
                    sick_val = 'Sick Leaves' + ' ' +str(year_val)
                    
                    casual = 0
                    cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where hh.employee_id='"+str(val.id)+"' and hh.month='"+str(line.month.id)+"' and hh.type = 'remove' and hhs.name = '"+str(casual_val)+"'  and state = 'validate' ") 
                    casual_leave = cr.fetchall()
                    if casual_leave[0][0] != None:
                        for temp in casual_leave:
                            casual = temp[0]

                    sick = 0
                    cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where hh.employee_id='"+str(val.id)+"' and hh.month='"+str(line.month.id)+"' and hh.type = 'remove' and hhs.name = '"+str(sick_val)+"' and state = 'validate' ") 
                    sick_leave = cr.fetchall()
                    if sick_leave[0][0] != None:
                        for temp in sick_leave:
                            sick = temp[0]

                    compensatory = 0
                    cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where hh.employee_id='"+str(val.id)+"' and hh.month='"+str(line.month.id)+"' and hh.type = 'remove' and hhs.name = 'Compensatory Days'  and state = 'validate' ") 
                    compensatory_leave = cr.fetchall()
                    if compensatory_leave[0][0] != None:
                        for temp in compensatory_leave:
                            compensatory = temp[0]

                    earned = 0
                    cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where hh.employee_id='"+str(val.id)+"' and hh.month='"+str(line.month.id)+"' and hh.type = 'remove' and hhs.name = 'Earned Leaves' and state = 'validate' ") 
                    earned_leave = cr.fetchall()
                    if earned_leave[0][0] != None:
                        for temp in earned_leave:
                            earned = temp[0]
        
                    holiday = 0
                    cr.execute("select sum(number_of_days_temp) from hr_holidays where employee_id='"+str(val.id)+"' and month='"+str(line.month.id)+"' and type = 'remove'  and state = 'validate' ") 
                    leave_day = cr.fetchall()
#                    print"leave_day =-=-=-=-=-=--=---=-=----------",leave_day
                    if leave_day[0][0] != None:
                        for temp in leave_day:
                            holiday = temp[0]
#                            print"holiday -=-=-===-=-=-=-=----------------",holiday

                    factory = 0
                    cr.execute("select sum(hh.number_of_days_temp) from hr_holidays as hh left join hr_holidays_status as hhs on hh.holiday_status_id = hhs.id where hh.employee_id='"+str(val.id)+"' and hh.month='"+str(line.month.id)+"' and hh.type = 'remove' and hhs.name = 'Factory Work'  and state = 'validate' ") 
                    casual_leave = cr.fetchall()
                    if casual_leave[0][0] != None:
                        for temp in casual_leave:
                            factory = temp[0]
                            
                    if days < 0:
                        days = 0

                    for val6 in neg_sunday_lst:
                        if val6[0] == val.id :
                            neg_sunday = val6[1]
                    
                    if days > 0:
                        work_day = days
#                        print"in ifff ============================",days,off_day,emp_sunday,holiday,neg_sunday
                        days = days + off_day + emp_sunday + holiday - neg_sunday
                    if days >= month:
                        days = month
#                    print"days ========================",days
                    holiday_leave = off_day     
                    week_leave = emp_sunday - neg_sunday
                    daily_amt = round(days * daily,0)
                    other_salary_amount = round(days * other_salary,0)
#                    hra_amt = round(days * hra,0)
#                    conveyance_amt = round(days * conveyance,0)
#                    medical_amt = round(days * medical,0)
#                    allowance_amt = round(days * allowance,0)
                    
                    salary = days * daily
                    TOTAL_PENALTY = TOTAL_SAL = CUTT_OFF = ALLOW_HR = DAILY_AMT = AMT_HR =  WORK_OT = SUN_OT = HALF_OT = HALF_OT_HR = TOTAL_OT = ACTUAL_OT = SUN_ACTUAL_OT = WORK_OVER_TIME = SUN_OVER_TIME = TOTAL_OVER_TIME = WORK_OT1 = SUN_OT1 = 0.0
                    TOTAL_OT_TIME = TOTAL_OT_TIME1 = c = 0
                    s = ''
                    for rec in att_obj.browse(cr, uid, att_list):
                        if rec.name in holiday_date:
                            sun_ot = float(rec.over_time / 60)
                            SUN_OT += sun_ot
                            SUN_OVER_TIME += rec.over_time
                        else:
                            work_ot = float(rec.over_time / 60)
                            WORK_OT += work_ot
                            WORK_OVER_TIME += rec.over_time
                            
                        TOTAL_PENALTY += rec.penalty 
                       
                    SUN_OT = SUN_OT
                    WORK_OT = WORK_OT
                    TOTAL_OVER_TIME = SUN_OVER_TIME + WORK_OVER_TIME
                    if TOTAL_OVER_TIME:
                        TOTAL_OT_TIME = int(TOTAL_OVER_TIME / 60)
                        TOTAL_OT_TIME1 = int(TOTAL_OVER_TIME % 60)
                        if TOTAL_OT_TIME1 in range (0,10):
                            c = '0' + str(TOTAL_OT_TIME1)
                        elif TOTAL_OT_TIME1 in range (10,99):
                            c = TOTAL_OT_TIME1    
                        s = s + str(TOTAL_OT_TIME) + '.' + str(c)
                        
                    if line.manual_sheet:
                        for manual in line.salary_payment_line_manual:
                            if manual.employee_id.id==val.id:
                                WORK_OT = manual.working_ot
                                SUN_OT = manual.sunday_ot
                                WORK_OT1 = manual.working_ot
                                SUN_OT1 = manual.sunday_ot
                               
                    TOTAL_OVER_TIME = ((WORK_OT1 + SUN_OT1) * 60)
                    if TOTAL_OVER_TIME:
                        TOTAL_OT_TIME = int(TOTAL_OVER_TIME / 60)
                        TOTAL_OT_TIME1 = int(TOTAL_OVER_TIME % 60)
                        if TOTAL_OT_TIME1 in range (0,10):
                            c = '0' + str(TOTAL_OT_TIME1)
                        elif TOTAL_OT_TIME1 in range (10,99):
                            c = TOTAL_OT_TIME1    
                        s = s + str(TOTAL_OT_TIME) + '.' + str(c)
                            
                    DAILY_AMT = daily_amt
                    AMT_HR = OT_amt
                    
                    TOTAL_SAL = daily_amt + (WORK_OT * OT_amt *2)  + (SUN_OT * OT_amt * 2)
                   
                    if val.current_salary:
                        ACTUAL_OT = WORK_OT
                        SUN_ACTUAL_OT = SUN_OT
                   
                    over_time = ACTUAL_OT
                    sun_over_time = SUN_ACTUAL_OT
                    ACTUAL_OT_AMT = over_time * OT_amt * 2
                    over_time_amt = round(ACTUAL_OT_AMT,0)

                    SUN_ACTUAL_OT_AMT = sun_over_time * OT_amt * 2
                    sun_over_time_amt = round(SUN_ACTUAL_OT_AMT,0)
                    total_over_time = s
                    
                    total_work_time = days * 8
                    if total_over_time:
                        complete_work_time = total_work_time + float(total_over_time)
                    else:
                         complete_work_time = total_work_time   
                    total_overtime_amount = over_time_amt + sun_over_time_amt
                    
                    if days <= 0:
#                        total_amount = daily_amt = sun_over_time = over_time_amt = OT_amt = days = over_time = sun_over_time_amt= total_overtime_amount = hra_amt = conveyance_amt = medical_amt = allowance_amt = total_amounts =0.0
                        total_amount = daily_amt = sun_over_time = over_time_amt = OT_amt = days = over_time = sun_over_time_amt= total_overtime_amount = other_salary_amount = total_amounts =0.0
                        
#                    total_amount = daily_amt + over_time_amt + sun_over_time_amt + hra_amt + conveyance_amt + medical_amt + allowance_amt
                    total_amount = daily_amt + over_time_amt + sun_over_time_amt + other_salary_amount
                    total_amounts = daily_amt + over_time_amt + sun_over_time_amt
                    
                    cr.execute("delete from salary_payment_line where employee_id ='"+str(val.id)+"' and month = '"+str(line.month.month)+"' and salary_id = '"+str(line.id)+"'")
                    salline_obj.create(cr, uid, {'salary_id':line.id,'year_id':line.month.year_id.id,'employee_id':val.id,'basic':val.current_salary,
                        'days':days,'days_amount':daily_amt,'over_time':over_time,'overtime_amount':over_time_amt,'sun_over_time':sun_over_time,'sun_overtime_amount':sun_over_time_amt,
                        'total_amount':total_amount,'month':line.month.month,'state':'Draft','salary_type':line.salary_type,'month_days':month,'total_over_time':total_over_time,'total_over_time1':total_over_time,
                        'total_work_time':total_work_time,'complete_work_time':complete_work_time,'days_amount1':daily_amt,'total_overtime_amount':total_overtime_amount,
                        'holiday_leave':holiday_leave,'casual_leave':casual,'sick_leave':sick,'compensatory_leave':compensatory,'earned_leave':earned,'week_leave':week_leave,'work_day':work_day,
                        'other_salary':val.other_salary,'other_salary_amount':other_salary_amount,'total_amounts':total_amounts,'factory_work':factory})
                        
#                    salline_obj.create(cr, uid, {'salary_id':line.id,'year_id':line.month.year_id.id,'employee_id':val.id,'basic':val.current_salary,
#                        'days':days,'days_amount':daily_amt,'over_time':over_time,'overtime_amount':over_time_amt,'sun_over_time':sun_over_time,'sun_overtime_amount':sun_over_time_amt,
#                        'total_amount':total_amount,'month':line.month.month,'state':'Draft','salary_type':line.salary_type,'month_days':month,'total_over_time':total_over_time,'total_over_time1':total_over_time,
#                        'total_work_time':total_work_time,'complete_work_time':complete_work_time,'days_amount1':daily_amt,'total_overtime_amount':total_overtime_amount,
#                        'holiday_leave':holiday_leave,'casual_leave':casual,'sick_leave':sick,'compensatory_leave':compensatory,'earned_leave':earned,'week_leave':week_leave,'work_day':work_day,
#                        'hra':val.hra,'conveyance':val.conveyance,'medical':val.medical,'special_allowance':val.special_allowance,
#                        'hra_amount':hra_amt,'conveyance_amount':conveyance_amt,'medical_amount':medical_amt,'special_allowance_amount':allowance_amt,'total_amounts':total_amounts})
                    print "<----------------------------SALARY CALCULATED----------------------------------->",counter,total_amount
                    counter += 1
        return res
    
    def get_paid_salary(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('salary.payment.line')
        emp_obj = self.pool.get('hr.employee')
        counter = 1
        loan12 = ''
        s = ''
        for each in self.browse(cr, uid, ids):
            if each.company_id and each.employment_type:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False),('company_id','=',each.company_id.id),('employment_type','=',each.employment_type)])  
            elif each.company_id:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False),('company_id','=',each.company_id.id)])  
            elif each.employee_id:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False),('id','=',each.employee_id.id)])

#            elif each.employment_type:
#                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False),('employment_type','=',each.employment_type)])    
            else:
                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('shift_lines','!=',False)])
            for val in line_obj.browse(cr, uid, line_obj.search(cr, uid, [('employee_id','in',emp_ids),('salary_id','=',each.id)])):
#                rnd_grand_total = grand_total = tds = epf = kharcha = loan = current_loan = esi = epf1 = epf2 = epf_amt = tax = 0.0
                rnd_grand_total = grand_total = tds = epf = kharcha = loan = current_loan = esi = epf1 = epf2 = epf_amt = vpf = 0.0 
                if each.salary_type == 'Salary':
                    cr.execute("select tds from payment_management_tds  where  employee_id = '"+str(val.employee_id.id)+"' order by tds_date desc limit 1 ")
                    temp = cr.fetchall()
                    for data in temp:
                        if data and data[0] != None:
                            tds = data[0]
                            
                if each.salary_type in ['Salary','Kharcha']:
                    cr.execute("select sum(total_amount) from payment_management_advance  where month='"+str(each.month.month)+"' and year_id='"+str(val.year_id.id)+"' and employee_id = '"+str(val.employee_id.id)+"'")
                    temp = cr.fetchall()
                    for data in temp:
                        if data and data[0] != None:
                            kharcha = data[0]
                            
                if each.salary_type == 'Salary':
                    cr.execute("select max(line.loan_line_amt) from loan_deduction_line as line left join loan_deduction as " \
                               "loan on (line.loan_deduct_id = loan.id) left join holiday_list as holi on (line.loan_id = holi.id) " \
                               "where holi.month='"+str(each.month.month)+"' and holi.year_id='"+str(val.year_id.id)+"' and loan.emp_id='"+str(val.employee_id.id)+"' and loan.state='done'")
                    temp = cr.fetchall()
                    for data in temp:
                        if data and data[0] != None:
                            loan = data[0]
                            
                if each.salary_type == 'Salary':
                    cr.execute("select line.state from loan_deduction_line as line left join loan_deduction as " \
                               "loan on (line.loan_deduct_id = loan.id) left join holiday_list as holi on (line.loan_id = holi.id) " \
                               "where holi.month='"+str(each.month.month)+"' and holi.year_id='"+str(val.year_id.id)+"' and loan.emp_id='"+str(val.employee_id.id)+"' and loan.state='done'")
                    temp = cr.fetchall()
                    for data in temp:
                        if data and data[0] != None:
                            loan12 = data[0]
                            
                            
                if each.salary_type == 'Salary':
                    cr.execute("select sum(loan.balance) from loan_deduction_line as line left join loan_deduction as " \
                               "loan on (line.loan_deduct_id = loan.id) left join holiday_list as holi on (line.loan_id = holi.id) " \
                               "where holi.month='"+str(each.month.month)+"' and holi.year_id='"+str(val.year_id.id)+"' and loan.emp_id='"+str(val.employee_id.id)+"' and loan.state='done'")
                    temp = cr.fetchall()
                    for data in temp:
                        if data and data[0] != None:
                            current_loan = data[0]

                if each.salary_type == 'Salary':
                    cr.execute("select vpf from payment_management_vpf where employee_id = '"+str(val.employee_id.id)+"' order by vpf_date desc limit 1 ")
                    temp = cr.fetchall()
                    for data in temp:
                        if data and data[0] != None:
                            vpf = data[0]
                            
#                if each.salary_type == 'Salary':
#                    cr.execute("select tax from professional_tax  where  employee_id = '"+str(val.employee_id.id)+"' order by tax_date desc limit 1 ")
#                    temp = cr.fetchall()
#                    for data in temp:
#                        if data and data[0] != None:
#                            tax = data[0]
                            
                            
                days = val.days
                month = val.month_days
                gross_salary = val.days_amount
                current_salary = val.employee_id.current_salary
                epf_tick = val.employee_id.epf_tick
                esi_tick = val.employee_id.esi_tick   
                total=val.total_amount
                total_amt = val.total_amounts
                if gross_salary:
                    if epf_tick:
                        if current_salary > 15000:
                            epf_amt = ((15000 * days)/month)
                            epf = round(((epf_amt * 12) /100),0)
                            epf1 = round(((epf_amt * 8.33) /100),0)
                        else:
                            epf_amt = gross_salary
                            epf = round(((epf_amt * 12)/100),0)   
                            epf1 = round(((epf_amt * 8.33)/100),0)
                            
                    if esi_tick:      
                        if total :
                            a = ((total * 1.75)/100)
                            b = str(a)
                            c = b.split('.')
                            d = c[0]
                            e = c[1][0:2]
                            s = d + '.' + e
                            t = float(s)
                            esi = math.ceil(t)
#                           esi = (math.ceil((total * 1.75)/100))
                           
                get_esi=esi   
                get_epf=epf 
                get_advance=kharcha
                get_tds=tds
                get_loan=loan
                get_curr_loan=current_loan
                get_vpf = vpf
#                get_tax = tax
                if val.days <= 0 and not (get_advance or get_epf or get_tds or get_loan or get_curr_loan or get_esi):   
                    cr.execute("delete from salary_payment_line where id = '"+str(val.id)+"'")
                    continue
                if get_curr_loan < 0:
                    raise osv.except_osv(_('Warning !'), _('Current loan can not be negative'))
                if get_advance < 0:
                    raise osv.except_osv(_('Warning !'), _('Kharcha can not be negative'))
                if get_tds < 0:
                    raise osv.except_osv(_('Warning !'), _('TDS can not be negative'))
                if get_esi < 0:
                    raise osv.except_osv(_('Warning !'), _('ESI can not be negative'))
                if get_epf < 0:
                    raise osv.except_osv(_('Warning !'), _('EPF can not be negative'))
                if get_loan < 0:
                    raise osv.except_osv(_('Warning !'), _('Loan amount can not be negative'))
                if get_vpf < 0:
                    raise osv.except_osv(_('Warning !'), _('VPF can not be negative'))
                
                if loan12 == 'stop':
#                    grand_total=total - get_tds - get_epf  - get_advance  - get_esi - get_tax
                    grand_total=total - get_tds - get_epf  - get_advance  - get_esi - get_vpf
                else:    
#                    grand_total=total - get_tds - get_epf  - get_advance  - get_esi - get_loan - get_tax
                    grand_total=total - get_tds - get_epf  - get_advance  - get_esi - get_loan - get_vpf
                    
                rnd_grand_total = grand_total
                rnd = grand_total % 10
                if rnd >= 0 and rnd < 3:
                    rnd_grand_total = grand_total - rnd
                elif rnd > 2 and rnd < 6:
                    if rnd == 3:
                        rnd = 2
                    elif rnd == 4:
                        rnd = 1 
                    else:
                        rnd = 0
                    rnd_grand_total = grand_total + rnd
                elif rnd > 5 and rnd < 8:
                    if rnd == 6:
                        rnd = 1
                    elif rnd == 7:
                        rnd = 2
                    rnd_grand_total = grand_total - rnd
                elif rnd > 7:
                    if rnd == 8:
                        rnd = 2
                    elif rnd == 9:
                        rnd = 1 
                    rnd_grand_total = grand_total + rnd
                    
                if each.salary_type == 'Kharcha':
                    rnd_grand_total = int(math.ceil(rnd_grand_total / 100.0)) * 100
                if loan12 == 'stop':  
                    vals = { 
                             'kharcha':kharcha,
                             'epf':epf,
                             'tds':tds,
                             'esi':esi,
                             'grand_total':grand_total,
                             'rnd_grand_total':rnd_grand_total,
                             'epf1':epf1,
                             'epf2':epf - epf1,
                             'gross':epf_amt,
                             'vpf':vpf
#                             'pro_tax_amt':tax
                             }
                else:     
                    vals = { 
                             'current_loan':current_loan,
                             'kharcha':kharcha,
                             'epf':epf,
                             'tds':tds,
                             'esi':esi,
                             'loan':loan,
                             'grand_total':grand_total,
                             'rnd_grand_total':rnd_grand_total,
                             'epf1':epf1,
                             'epf2':epf - epf1,
                             'gross':epf_amt,
                             'vpf':vpf
#                             'pro_tax_amt':tax
                             }
                
                line_obj.write(cr, uid, [val.id],vals)
                print "<--------------------------------PROCESSING---------------------------------->",counter
                counter += 1
                
        return True

class salary_payment_line(osv.osv):
    _name = 'salary.payment.line'
    _order = 'employee_id'
    
    _columns = {
                'salary_id':fields.many2one('salary.payment','Salary',ondelete="cascade"),
                'employee_id':fields.many2one('hr.employee','Employee',required=True,readonly=True),
                'department_id':fields.related('employee_id','department_id',relation='hr.department',string='Department',type="many2one",readonly=True,store=True),
                'job_id':fields.related('employee_id','job_id',relation='hr.job',string='Designation',type="many2one",readonly=True,store=True),
                'basic':fields.float('Total Monthly Gross',digits_compute= dp.get_precision('Account'),readonly=True),
                'days':fields.float('Days',digits_compute= dp.get_precision('Account'),readonly=True),
                'month_days':fields.float('Month Days',digits_compute= dp.get_precision('Account'),readonly=True),
                'days_amount':fields.float('Actual Monthly Payment (Basic + DA)',digits_compute= dp.get_precision('Account'),readonly=True),
                'over_time':fields.float('WORK O.T',digits_compute= dp.get_precision('Account'),readonly=True),
                'overtime_amount':fields.float('WORK Amt',digits_compute= dp.get_precision('Account'),readonly=True),
                'sun_over_time':fields.float('Holiday O.T',digits_compute= dp.get_precision('Account'),readonly=True),
                'sun_overtime_amount':fields.float('Holiday Amt',digits_compute= dp.get_precision('Account'),readonly=True),
                'total_amount':fields.float('T Amt',digits_compute= dp.get_precision('Account'),readonly=True),
                'grand_total':fields.float('Grd Total',digits_compute= dp.get_precision('Account'),readonly=True),
                'rnd_grand_total':fields.float('Rnd Grd Total',digits_compute= dp.get_precision('Account'), readonly=True),
                'month':fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),
                ('8','August'),('9','September'),('10','October'),('11','November'),('12','December'),],'Month',readonly=True),
                'year_id':fields.many2one('holiday.year','Year',readonly=True),
                'current_loan':fields.float('Curr. Loan',digits_compute= dp.get_precision('Account'),required=True, readonly=True),
                'loan':fields.float('Loan EMI',digits_compute= dp.get_precision('Account'), readonly=True),
                'kharcha':fields.float('Advance Amt',digits_compute= dp.get_precision('Account'),readonly=True),
                'epf':fields.float('EPF',digits_compute= dp.get_precision('Account'), readonly=True),
                'tds':fields.float('TDS',digits_compute= dp.get_precision('Account'), readonly=True),
                'esi':fields.float('ESI',digits_compute= dp.get_precision('Account'), readonly=True),
                'state':fields.selection([('Draft','Draft'),('Ready','Ready'),('Paid','Paid')],'Status',readonly=True),
                'salary_type':fields.selection([('Kharcha','Kharcha'),('Salary','Salary')],'Salary Type',required=True),
                'total_over_time':fields.float('Total Overtime',digits_compute= dp.get_precision('Account'),readonly=True),
                'total_over_time1':fields.float('Total OT Hours',digits_compute= dp.get_precision('Account'),readonly=True),
                'total_work_time':fields.float('Total Hours Worked',digits_compute= dp.get_precision('Account'),readonly=True),
                'complete_work_time':fields.float('Total Working Hours',digits_compute= dp.get_precision('Account'),readonly=True),
                'days_amount1':fields.float('Actual Total Gross Salary paid',digits_compute= dp.get_precision('Account'),readonly=True),
                'total_overtime_amount':fields.float('OT Salary',digits_compute= dp.get_precision('Account'),readonly=True),
                'department_name':fields.related('employee_id','department_id','name',relation='hr.department',string='Department Name',type="char",readonly=True,store=True),
                'job_name':fields.related('employee_id','job_id','name',relation='hr.job',string='Designation Name',type="char",readonly=True,store=True),
                'sinid':fields.related('employee_id','sinid',relation='hr.employee',string='PCard',type="char",readonly=True,store=True),
                'employee_name':fields.related('employee_id','name',relation='hr.employee',string='Employee Name',type="char",readonly=True,store=True),
                'holiday_leave':fields.float('Holiday Leave',digits_compute= dp.get_precision('Account'),readonly=True),
                'casual_leave':fields.float('Casual Leave',digits_compute= dp.get_precision('Account'),readonly=True),
                'sick_leave':fields.float('Sick Leave',digits_compute= dp.get_precision('Account'),readonly=True),
                'compensatory_leave':fields.float('Compensatory Leave',digits_compute= dp.get_precision('Account'),readonly=True),
                'earned_leave':fields.float('Earned Leave',digits_compute= dp.get_precision('Account'),readonly=True),
                'week_leave':fields.float('Week Off Leave',digits_compute= dp.get_precision('Account'),readonly=True),
                'epf1':fields.float('EPF',digits_compute= dp.get_precision('Account'), readonly=True),
                'epf2':fields.float('EPF',digits_compute= dp.get_precision('Account'), readonly=True),
                'work_day':fields.float('Work day',digits_compute= dp.get_precision('Account'),readonly=True),
                'gross':fields.float('Actual Monthly Payment (Basic + DA)',digits_compute= dp.get_precision('Account'),readonly=True),
                'hra':fields.float("HRA",digits_compute= dp.get_precision('Account')),
                'conveyance':fields.float("Conveyance",digits_compute= dp.get_precision('Account')),
                'medical':fields.float("Medical",digits_compute= dp.get_precision('Account')),
                'special_allowance':fields.float("Special Allowance",digits_compute= dp.get_precision('Account')),
                'hra_amount':fields.float('HRA Amt.',digits_compute= dp.get_precision('Account'),readonly=True),
                'conveyance_amount':fields.float('Conveyance Amt.',digits_compute= dp.get_precision('Account'),readonly=True),
                'medical_amount':fields.float('Medical Amt.',digits_compute= dp.get_precision('Account'),readonly=True),
                'special_allowance_amount':fields.float('Special Allowance Amt.',digits_compute= dp.get_precision('Account'),readonly=True),
                'pro_tax_amt':fields.float("Professional Tax",digits_compute= dp.get_precision('Account')),
                'total_amounts':fields.float('Total Amt',digits_compute= dp.get_precision('Account'),readonly=True),
                'other_salary':fields.float("Other",digits_compute= dp.get_precision('Account')),
                'other_salary_amount':fields.float('Other- Amt.',digits_compute= dp.get_precision('Account'),readonly=True),
                'factory_work':fields.float('Factory Work',digits_compute= dp.get_precision('Account'),readonly=True),
                'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),
                'vpf':fields.float('VPF',digits_compute= dp.get_precision('Account'), readonly=True),                
                }
    
    _defaults = {
                 'state':'Draft',
                 'kharcha':0.0,
                 'epf':0.0,
                 'tds':0.0,
                 'loan':0.0,
                 'current_loan':0.0,
                 'esi':0.0,
                 'hra_amount':0.0,
                 'conveyance_amount':0.0,
                 'medical_amount':0.0,
                 'special_allowance_amount':0.0,
                 'pro_tax_amt':0.0,
                 'vpf':0.0
                 }
    
    _sql_constraints = [('unique_employee_month_year','unique(employee_id,month,year_id,salary_type)','Employee salary line for this month and year is already exist.')]
    
    
    def unlink(self, cr, uid, ids, context=None):
        order = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for line in order:
            if line['state'] in ['Draft']:
                unlink_ids.append(line['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('You cannot delete Salary Line.'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
    
class payment_management_advance(osv.osv):
    _name='payment.management.advance'
    
    def _calculate_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.advance_date,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            res[each.id] = month     
        return res
    
    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.advance_date,'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                res[each.id] = year_id[0]  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res
    
        
    _columns={
              'name':fields.date('Create Date',readonly=True),
              'advance_date':fields.date('Advance Date',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'month':fields.function(_calculate_month,method=True,type='integer',string='Month',store=True),
              'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
              'employee_id':fields.many2one('hr.employee','Employee',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'total_amount':fields.float('Advance',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'remark':fields.char('Remark',size=512, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'user_id':fields.many2one('res.users','Created By',readonly=True),
              'state':fields.selection([('draft','Draft'),('done','Done')],'State',readonly=True),
              'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),
              }
    _defaults={
               'name':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
               'user_id': lambda obj, cr, uid, context: uid,
               'state':'draft',
               }
    
    _sql_constraints = [('unique_name_employee_advance_date','unique(employee_id,advance_date)','Advance line is already created for this date and employee.')]
    
    def onchange_employee(self, cr, uid, ids, employee, context=None):
        res = {}
        if not employee:
            return res
        cr.execute("select advance_date from payment_management_advance order by id desc limit 1") 
        temp = cr.fetchall()
        for data in temp:
            if data and len(data) > 0 and data[0] != None:
                date1 = data[0]
                res['value'] = {'advance_date':date1}
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        
        unlink_ids = []
        for line in self.browse(cr, uid, ids, context):
            if line.state in ['draft']:
                unlink_ids.append(line.id)
            else:
                raise osv.except_osv(_('Invalid action !'), _('You cannot delete posted entry.'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    

class payment_management_tds(osv.osv):
    _name='payment.management.tds'
    
    def create(self, cr, uid, vals, context=None):
        year_name = ''
        if 'tds_date' in vals and vals['tds_date']:
            tm_tuple = datetime.strptime(vals['tds_date'],'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                year_name = self.pool.get('holiday.year').browse(cr, uid,year_id[0]).name
                vals['year'] = year_name
                vals['state'] = 'done'
        res = super(payment_management_tds, self).create(cr, uid, vals, context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        year_name = ''
        if 'tds_date' in vals and vals['tds_date']:
            tm_tuple = datetime.strptime(vals['tds_date'],'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                year_name = self.pool.get('holiday.year').browse(cr, uid,year_id[0]).name
                vals['year'] = year_name

        res = super(payment_management_tds, self).write(cr, uid, ids, vals, context)
        return res
    
    def _calculate_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.tds_date,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            res[each.id] = month     
        return res
    
    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.tds_date,'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                res[each.id] = year_id[0]  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res
    
    
    _columns={
              'name':fields.date('Create Date',readonly=True),
              'tds_date':fields.date('TDS Date',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'employee_id':fields.many2one('hr.employee','Employee',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'month':fields.function(_calculate_month,method=True,type='integer',string='Month',store=True),
              'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
              'tds':fields.float('TDS',digits_compute= dp.get_precision('Account'),required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'user_id':fields.many2one('res.users','Created By',readonly=True),
              'state':fields.selection([('draft','Draft'),('done','Done')],'State',readonly=True),
              'year':fields.selection([('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),
                                         ('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),
                                         ('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),
                                         ('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),
                                         ('2030','2030'),('2031','2031'),('2032','2032'),('2033','2033'),
                                         ('2034','2034'),('2035','2035'),],'YEAR'),
              'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),                           
              }
    
    _sql_constraints = [('unique_name_employee_month_year','unique(employee_id,month,year_id)','Payment line is already created for this date, employee, month and year.')]
    
    _defaults={
           'name':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
           'user_id': lambda obj, cr, uid, context: uid,
           'state':'draft',
           'year':time.strftime('%Y'),
           }
    
    def onchange_employee(self, cr, uid, ids, employee, context=None):
        res = {}
        if not employee:
            return res
        cr.execute("select tds_date from payment_management_tds order by id desc limit 1") 
        temp = cr.fetchall()
        for data in temp:
            if data and len(data) > 0 and data[0] != None:
                date1 = data[0]
                res['value'] = {'tds_date':date1}
        return res
    
    def onchange_month(self, cr, uid, ids, month, context=None):
        res = {}
        if not month:
            res['value'] = {'year_id':False}
            return res
        month_obj = self.pool.get('holiday.list')
        month_data = month_obj.browse(cr, uid, month)
        if not month_data.year_id:
            res['warning'] = {'title': _('Warning'), 'message': _('Unable to process request, year is not selected in month.')}
        res['value'] = {'year_id':month_data.year_id and month_data.year_id.id or False}
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        
        unlink_ids = []
        for line in self.browse(cr, uid, ids, context):
            if line.state in ['draft']:
                unlink_ids.append(line.id)
            else:
                raise osv.except_osv(_('Invalid action !'), _('You cannot delete posted entry.'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)

class salary_payment_line_manual(osv.osv):
    _name = 'salary.payment.line.manual'
    _description = 'Manual Salary Payment Lines'

    def _calculate_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            month = each.salary_id.month.id
            if month:
                res[each.id] = month  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res

    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            year_id = each.salary_id.month.year_id.id
            if year_id:
                res[each.id] = year_id  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res
    

    _columns = {
                'name':fields.char(string='Name',type='char',size=64),
                'salary_id':fields.many2one('salary.payment','Salary',ondelete="cascade"),
                'employee_id':fields.many2one('hr.employee','Employee',required=True, select=True),
                'month':fields.function(_calculate_month,relation="holiday.list",type='many2one',string='Month',store=True),
                'year_id':fields.function(_calculate_year,relation="holiday.year",type='many2one',string='Year',store=True),
                'days':fields.float('Days',digits=(3,1), select=True),
                'working_ot':fields.float('Working Day OT',digits=(16,2), select=True),
                'sunday_ot':fields.float('Leave Day OT',digits=(16,2), select=True),                
                'salary_type':fields.related('salary_id','salary_type',selection=[('Salary','Salary')],string='Salary Type',type="selection",store=True),
    }
    
    _sql_constraints = [('unique_employee_month_year','unique(employee_id,month,year_id,salary_type)','Employee salary line for this month and year is already exist.')]
 
 
#class payment_management_bonus(osv.osv):
#    _name='payment.management.bonus'
#    
#    _columns={
#              'bonus_from':fields.date('Bonus From',required=True),
#              'bonus_till':fields.date('Bonus Till',required=True),
#              'employee_id':fields.many2one('hr.employee','Employee'),
#              'company_id':fields.many2one('res.company','Company',),
#              'user_id':fields.many2one('res.users','User',readonly=True),
#              'bonus_line':fields.one2many('payment.management.bonus.line','bonus_id','Bonus line'),
#              'export_data':fields.binary('File',readonly=True),
#              'filename':fields.char('File Name',size=250,readonly=True),
#              'name':fields.char('Name',size=250),
#              }    
#    
#    _defaults={
#               'user_id': lambda obj, cr, uid, context: uid,
#               'name': 'Payment Bonus',
#              }
#
#    def compute_bonus(self, cr, uid, ids, context=None):
#        sal_obj = self.pool.get('salary.payment.line')
#        emp_obj = self.pool.get('hr.employee')
#        year_obj = self.pool.get('emp.year')
#        categ_obj = self.pool.get('employee.salary.category')
#        count = 0
#        categ_list = []
#        
#        cr.execute("select id from employee_salary_category ")
#        temp = cr.fetchall()
#        for data in temp:
#            categ_list.append(data[0])
#            
#        for each in self.browse(cr, uid, ids):           
#            if  each.employee_id:
#                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('id','=',each.employee_id.id)])
#            elif each.company_id:
#                emp_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id)])
#                
#            else:
#                emp_ids = emp_obj.search(cr, uid, [('active','=',True)])
#            
#            for line in emp_obj.browse(cr, uid, emp_ids):
#                jan = feb = mar = apr = may = jun = jul = aug = sep = oct = nov = dec =0
#                jan_day = feb_day = mar_day = apr_day = may_day = june_day = july_day = aug_day = sep_day = oct_day = nov_day = dec_day =0
#                total_salary=apr_salary=may_salary=june_salary=july_salary=aug_salary=sep_salary=oct_salary=nov_salary=dec_salary=jan_salary=feb_salary=mar_salary=0
#                basic = 0
#                for val in categ_obj.browse(cr,uid,categ_list):
#                    if val.category == 'Skilled' and line.category == 'Skilled':
#                        category = 'Skilled'
#                        bonus_limit = val.bonus_limit
#                        salary = val.salary
#                    if  val.category == 'UnSkilled' and line.category == 'UnSkilled':
#                        category = 'UnSkilled'
#                        bonus_limit = val.bonus_limit
#                        salary = val.salary
#                    if val.category == 'Semi_Skilled' and line.category == 'Semi_Skilled':
#                        category = 'Semi_Skilled'
#                        bonus_limit = val.bonus_limit
#                        salary = val.salary
#                          
#                if line.category == category and bonus_limit >= line.current_salary:
#                    starting_date = False
#                    total_month_days = 0
#                    total_days1 = 0
#                    bonus_from = each.bonus_from
#                    bonus_till = each.bonus_till
#                    total_day = 0
#                    rnd_total_pay = total_pay = 0
#                    month_count=0
#                    month = 0
#                    bonus_from = datetime.strptime(bonus_from,'%Y-%m-%d')
#                    bonus_till = datetime.strptime(bonus_till,'%Y-%m-%d')
#                    starting_date = bonus_from
#                    while (bonus_from <= bonus_till):
#                        bonus_till_to = bonus_till
#                        month += 1
#                        tm_tuple = datetime.strptime(bonus_from.strftime('%Y-%m-%d'),'%Y-%m-%d').timetuple()
#                        emp_month = tm_tuple.tm_mon
#                        emp_year = tm_tuple.tm_year
#                        tm_tuple_to = datetime.strptime(bonus_till_to.strftime('%Y-%m-%d'),'%Y-%m-%d').timetuple()
#                        emp_month_to = tm_tuple_to.tm_mon
#                        emp_year_to = tm_tuple_to.tm_year
#                        year_id = year_obj.search(cr, uid, [('name','=',emp_year_to)])
#                        salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month_to),('year_id.name','=',emp_year_to)])
#                        
#                        if sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month_to),('year_id.name','=',emp_year_to)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month_to),('year_id.name','=',emp_year_to)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month_to)-1)),('year_id.name','=',emp_year_to)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month_to)-1)),('year_id.name','=',emp_year_to)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month_to)-2)),('year_id.name','=',emp_year_to)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month_to)-2)),('year_id.name','=',emp_year_to)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+8)),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+8)),('year_id.name','=',emp_year)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+7)),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+7)),('year_id.name','=',emp_year)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+6)),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+6)),('year_id.name','=',emp_year)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+5)),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+5)),('year_id.name','=',emp_year)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+4)),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+4)),('year_id.name','=',emp_year)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+3)),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+3)),('year_id.name','=',emp_year)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+2)),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+2)),('year_id.name','=',emp_year)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+1)),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',(int(emp_month)+1)),('year_id.name','=',emp_year)])
#                        elif sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month),('year_id.name','=',emp_year)]):
#                            salary_id = sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month),('year_id.name','=',emp_year)])
#                        else:
#                            salary_id=[] 
#                            
#                        for val in sal_obj.browse(cr, uid, sal_obj.search(cr, uid, [('employee_id','=',line.id),('month','=',emp_month),('year_id.name','=',emp_year)])):
#                                if val.salary_type=='Salary':
#                                    month_count+=1
#                                    if line.category == 'Skilled':
#                                        if category == 'Skilled':
#                                            basic = salary
#
#                                    if line.category == 'UnSkilled':
#                                        if category == 'UnSkilled':
#                                            basic = salary
#
#                                    if line.category == 'Semi_Skilled':
#                                        if category == 'Semi_Skilled':
#                                            basic = salary
#                                             
#                                    cr.execute("select rc.id from res_company as rc left join resource_resource as rr on rc.id = rr.company_id left join hr_employee as hr on rr.id = hr.resource_id where hr.id = '"+str(line.id)+"' and rc.name ilike '%%%%%Lohia%%%%%'")
#                                    company = cr.fetchall()
#                                    if company:
#                                        total_pay += ((((basic * val.days) / val.month_days) * 8.33)/100)   
#
#                                    cr.execute("select rc.id from res_company as rc left join resource_resource as rr on rc.id = rr.company_id left join hr_employee as hr on rr.id = hr.resource_id where hr.id = '"+str(line.id)+"' and rc.name ilike '%%%%%%%%Designco%%%%%%%%'")
#                                    company = cr.fetchall()
#                                    if company:
#                                        total_pay += ((((basic * val.days) / val.month_days) * 20)/100)   
#                                        
#                                    if emp_month==1:
#                                            jan=val.days
#                                            jan_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * jan)/jan_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                jan_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                jan_salary = math.ceil(t)
#                                    elif emp_month==2:
#                                            feb=val.days
#                                            feb_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * feb)/feb_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                feb_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                feb_salary = math.ceil(t)
#                                    elif emp_month==3:
#                                            mar=val.days
#                                            mar_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * mar)/mar_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                mar_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                mar_salary = math.ceil(t)
#                                    elif emp_month==4:
#                                            apr=val.days
#                                            apr_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * apr)/apr_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                apr_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                apr_salary = math.ceil(t)
#                                    elif emp_month==5:
#                                            may=val.days
#                                            may_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary =((basic * may)/may_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                may_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                may_salary = math.ceil(t)
#                                    elif emp_month==6:
#                                            jun=val.days
#                                            june_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * jun)/june_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                june_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                june_salary = math.ceil(t)
#                                    elif emp_month==7:
#                                            jul=val.days
#                                            july_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * jul)/july_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                july_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                july_salary = math.ceil(t)
#                                    elif emp_month==8:
#                                            aug=val.days
#                                            aug_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * aug)/aug_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                aug_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                aug_salary = math.ceil(t)
#                                    elif emp_month==9:
#                                            sep=val.days
#                                            sep_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * sep)/sep_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                sep_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                sep_salary = math.ceil(t)
#                                    elif emp_month==10:
#                                            oct=val.days
#                                            oct_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * oct)/oct_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                oct_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                oct_salary = math.ceil(t)
#                                    elif emp_month==11:
#                                            nov=val.days
#                                            nov_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * nov)/nov_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                nov_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                nov_salary = math.ceil(t)
#                                    elif emp_month==12:
#                                            dec=val.days
#                                            dec_day = val.month_days
#                                            month_id = val.month
#                                            year_id = val.year_id.id
#                                            salary = ((basic * dec)/dec_day)
#                                            salary1 = str(salary)
#                                            salary2 = salary1.split('.')
#                                            salary3 = salary2[0]
#                                            salary4 = int(salary2[1][0:2])
#                                            if salary4 in range(0,50):
#                                                sal = salary3
#                                                t = float(sal)
#                                                dec_salary = t
#                                            else:
#                                                sal = salary3 + '.' + str(salary4)
#                                                t = float(sal)
#                                                dec_salary = math.ceil(t)
#                                            
#                                            
#                        total_days1 = (jan + feb + mar + apr + may + jun + jul + aug + sep + oct + nov + dec)
#                        total_month_days = (jan_day + feb_day + mar_day + apr_day + may_day + june_day + july_day + aug_day + sep_day + oct_day + nov_day + dec_day)
#                        total_salary=apr_salary+may_salary+june_salary+july_salary+aug_salary+sep_salary+oct_salary+nov_salary+dec_salary+jan_salary+feb_salary+mar_salary
#                        bonus_from = bonus_from + relativedelta(months=+1)
#                    
#                    if month < 0:
#                        continue     
#                    a = total_pay
#                    if a > 0:
#                        b = str(a)
#                        c = b.split('.')
#                        d = c[0]
#                        e = int(c[1][0:2])
#                        if e in range(0,50):
#                            s = d
#                            t = float(s)
#                            rnd_total_pay = t
#                        else:
#                            s = d + '.' + str(e)
#                            t = float(s)
#                            rnd_total_pay = math.ceil(t)
#                                
#                    line_dict = {
#                                  'bonus_id':each.id,
#                                  'employee_id':line.id,
#                                  'joining_date':line.doj,
#                                  'company_id':line.company_id.id,
#                                  'bonus_from':starting_date,
#                                  'bonus_till':each.bonus_till,
#                                  'bonus_month':str(month_count) + ' month',
#                                  'bonus':rnd_total_pay,
#                                  'basic':basic,
#                                  'apr':apr,
#                                  'may':may,
#                                  'june':jun,
#                                  'july':jul,
#                                  'aug':aug,
#                                  'sep':sep,
#                                  'oct':oct,
#                                  'nov':nov,
#                                  'dec':dec,
#                                  'jan':jan,
#                                  'feb':feb,
#                                  'mar':mar,
#                                  'apr_day':apr_day,
#                                  'may_day':may_day,
#                                  'june_day':june_day,
#                                  'july_day':july_day,
#                                  'aug_day':aug_day,
#                                  'sep_day':sep_day,
#                                  'oct_day':oct_day,
#                                  'nov_day':nov_day,
#                                  'dec_day':dec_day,
#                                  'jan_day':jan_day,
#                                  'feb_day':feb_day,
#                                  'mar_day':mar_day,
#                                  'apr_salary':apr_salary,
#                                  'may_salary':may_salary,
#                                  'june_salary':june_salary,
#                                  'july_salary':july_salary,
#                                  'aug_salary':aug_salary,
#                                  'sep_salary':sep_salary,
#                                  'oct_salary':oct_salary,
#                                  'nov_salary':nov_salary,
#                                  'dec_salary':dec_salary,
#                                  'jan_salary':jan_salary,
#                                  'feb_salary':feb_salary,
#                                  'mar_salary':mar_salary,
#                                  'total_day':total_days1,
#                                  'total_month_day':total_month_days,
#                                  'total_salary':total_salary,
#                                  'user_id':uid,
#                                  'month':month_id,
#                                  'year_id':year_id,
#                                 }
#                    
#                    cr.execute("delete from payment_management_bonus_line where employee_id ='"+str(line.id)+"' and bonus_id = '"+str(each.id)+"'")
#                    if rnd_total_pay == 0.0:
#                        continue
#                    count += 1
#                    new_id = self.pool.get('payment.management.bonus.line').create(cr, uid, line_dict)
#                    print "<------------------- NEW RECORD CREATED  --------------->",count,str(month) + ' month',rnd_total_pay
#        return True
#
#    def print_report(self, cr, uid, ids, data, context=None):
#        obj = self.browse(cr,uid,ids)
#        f_name = ''
#        d_name = ''
#        wb = Workbook()
#        ws = wb.add_sheet('Payment Bonus')
#        fnt1 = Font()
#        fnt1.name = 'Arial'
#        fnt1.height= 300
#        fnt1.bold=True
#        align_content1 = Alignment()
#        align_content1.horz= Alignment.HORZ_CENTER
#        borders1 = Borders()
#        borders1.left = 0x00
#        borders1.right = 0x00
#        borders1.top = 0x00
#        borders1.bottom = 0x00
#        align1 = Alignment()
#        align1.horz = Alignment.HORZ_CENTER
#        align1.vert = Alignment.VERT_CENTER
#        pattern1 = Pattern()
#        pattern1.pattern1 = Pattern.SOLID_PATTERN
#        pattern1.pattern1_fore_colour =  0x1F
#        style_header1= XFStyle()
#        style_header1.font= fnt1
#        style_header1.pattern= pattern1
#        style_header1.borders = borders1
#        style_header1.alignment=align1
#        
#        fnt2 = Font()
#        fnt2.name = 'Arial'
#        fnt2.height= 300
#        fnt2.bold=True
#        align_content2 = Alignment()
#        align_content2.horz= Alignment.HORZ_CENTER
#        borders2 = Borders()
#        borders2.left = 0x00
#        borders2.right = 0x00
#        borders2.top = 0x00
#        borders2.bottom = 0x00
#        align2 = Alignment()
#        align2.horz = Alignment.HORZ_CENTER
#        align2.vert = Alignment.VERT_CENTER
#        pattern2 = Pattern()
#        pattern2.pattern2 = Pattern.SOLID_PATTERN
#        pattern2.pattern2_fore_colour =  0x1F
#        style_header2= XFStyle()
#        style_header2.font= fnt2
#        style_header2.pattern= pattern2
#        style_header2.borders = borders2
#        style_header2.alignment=align2
#
#        fnt3 = Font()
#        fnt3.name = 'Arial'
#        fnt3.height= 300
#        fnt3.bold=True
#        align_content3 = Alignment()
#        align_content3.horz= Alignment.HORZ_CENTER
#        borders3 = Borders()
#        borders3.left = 0x00
#        borders3.right = 0x00
#        borders3.top = 0x00
#        borders3.bottom = 0x00
#        align3 = Alignment()
#        align3.horz = Alignment.HORZ_CENTER
#        align3.vert = Alignment.VERT_CENTER
#        pattern3 = Pattern()
#        pattern3.pattern3 = Pattern.SOLID_PATTERN
#        pattern3.pattern3_fore_colour =  0x1F
#        style_header3= XFStyle()
#        style_header3.font= fnt3
#        style_header3.pattern= pattern3
#        style_header3.borders = borders3
#        style_header3.alignment=align3
#        
#        fnt = Font()
#        fnt.name = 'Arial'
#        fnt.height= 275
#        content_fnt = Font()
#        content_fnt.name ='Arial'
#        content_fnt.height =150
#        align_content = Alignment()
#        align_content.horz= Alignment.HORZ_CENTER
#        borders = Borders()
#        borders.left = 0x02
#        borders.right = 0x02
#        borders.top = 0x02
#        borders.bottom = 0x02
#        align = Alignment()
#        align.horz = Alignment.HORZ_CENTER
#        align.vert = Alignment.VERT_CENTER
#        pattern = Pattern()
#        pattern.pattern = Pattern.SOLID_PATTERN
#        pattern.pattern_fore_colour =  0x1F
#        style_header= XFStyle()
#        style_header.font= fnt
#        style_header.pattern= pattern
#        style_header.borders = borders
#        style_header.alignment=align
#
#        fnt5 = Font()
#        fnt5.name = 'Arial'
#        fnt5.height= 200
#        content_fnt5 = Font()
#        content_fnt5.name ='Arial'
#        content_fnt5.height =150
#        align_content5 = Alignment()
#        align_content5.horz= Alignment.HORZ_CENTER
#        borders5 = Borders()
#        borders5.left = 0x02
#        borders5.right = 0x02
#        borders5.top = 0x02
#        borders5.bottom = 0x02
#        align5 = Alignment()
#        align5.horz = Alignment.HORZ_CENTER
#        align5.vert = Alignment.VERT_CENTER
#        pattern5 = Pattern()
##        pattern5.pattern = Pattern.SOLID_PATTERN
##        pattern5.pattern_fore_colour =  0x1F
#        style_header5= XFStyle()
#        style_header5.font= fnt5
#        style_header5.pattern= pattern5
#        style_header5.borders = borders5
#        style_header5.alignment=align5
#
#        if obj.company_id:
#            get_name = obj.company_id.name
#        else:
#            get_name = obj.employee_id.resource_id.company_id.name
#        
#        ws.row(0).height=500
#        ws.write_merge(0,0,0,20,get_name,style_header1)
#        
#        date1 = datetime.strptime(obj.bonus_from,"%Y-%m-%d").timetuple().tm_year
#        date2 = datetime.strptime(obj.bonus_till,"%Y-%m-%d").timetuple().tm_year
#        if date1 == date2 :
#           d_name = 'BONUS' +' - '+ str(date1)
#        else:
#            d_name = 'BONUS' +'  '+ str(date1) + ' ' + '-' + ' ' +  str(date2)
#              
#        ws.row(1).height=500
#        ws.write_merge(1,1,0,20,d_name,style_header2)
#
#
#        ws.col(0).width = 5000 
#        ws.col(1).width = 6000   
#        ws.col(2).width = 3000 
#        ws.col(3).width = 3000 
#        ws.col(4).width = 3000 
#        ws.col(5).width = 3000   
#        ws.col(6).width = 3000 
#        ws.col(7).width = 3000 
#        ws.col(8).width = 3000 
#        ws.col(9).width = 3000   
#        ws.col(10).width = 3000 
#        ws.col(11).width = 3000 
#        ws.col(12).width = 3000 
#        ws.col(13).width = 3000   
#        ws.col(14).width = 3000 
#        ws.col(15).width = 3000 
#        ws.col(16).width = 3000 
#        ws.col(17).width = 3000   
#        ws.col(18).width = 3000 
#        ws.col(19).width = 3000 
#        ws.col(20).width = 3000 
#        ws.col(21).width = 3000   
#        ws.col(22).width = 3000 
#        ws.col(23).width = 3000 
#        ws.col(24).width = 3000 
#        ws.col(25).width = 3000   
#        ws.col(26).width = 3000 
#        ws.col(27).width = 3000 
#        ws.col(28).width = 4000
#        
#        ws.row(2).height=400
#        ws.write(2,0,'EMP. CODE',style_header)
#        ws.write(2,1,'NAME',style_header)
#        ws.write_merge(2,2,2,3,'APRIL',style_header)
#        ws.write_merge(2,2,4,5,'MAY',style_header)
#        ws.write_merge(2,2,6,7,'JUNE',style_header)
#        ws.write_merge(2,2,8,9,'JULY',style_header)
#        ws.write_merge(2,2,10,11,'AUGUST',style_header)
#        ws.write_merge(2,2,12,13,'SEPTEMBER',style_header)
#        ws.write_merge(2,2,14,15,'OCTOBER',style_header)
#        ws.write_merge(2,2,16,17,'NOVEMBER',style_header)
#        ws.write_merge(2,2,18,19,'DECEMBER',style_header)
#        ws.write_merge(2,2,20,21,'JANUARY',style_header)
#        ws.write_merge(2,2,22,23,'FEBRUARY',style_header)
#        ws.write_merge(2,2,24,25,'MARCH',style_header)
#        ws.write_merge(2,2,26,27,'TOTAL',style_header)
#        ws.write(2,28,'BONUS',style_header)
#
#        ws.row(3).height=400
#        ws.write(3,0,'',style_header)
#        ws.write(3,1,'',style_header)
#        ws.write(3,2,'DAYS',style_header)
#        ws.write(3,3,'SALARY',style_header)
#        ws.write(3,4,'DAYS',style_header)
#        ws.write(3,5,'SALARY',style_header)
#        ws.write(3,6,'DAYS',style_header)
#        ws.write(3,7,'SALARY',style_header)
#        ws.write(3,8,'DAYS',style_header)
#        ws.write(3,9,'SALARY',style_header)
#        ws.write(3,10,'DAYS',style_header)
#        ws.write(3,11,'SALARY',style_header)
#        ws.write(3,12,'DAYS',style_header)
#        ws.write(3,13,'SALARY',style_header)
#        ws.write(3,14,'DAYS',style_header)
#        ws.write(3,15,'SALARY',style_header)
#        ws.write(3,16,'DAYS',style_header)
#        ws.write(3,17,'SALARY',style_header)
#        ws.write(3,18,'DAYS',style_header)
#        ws.write(3,19,'SALARY',style_header)
#        ws.write(3,20,'DAYS',style_header)
#        ws.write(3,21,'SALARY',style_header)
#        ws.write(3,22,'DAYS',style_header)
#        ws.write(3,23,'SALARY',style_header)
#        ws.write(3,24,'DAYS',style_header)
#        ws.write(3,25,'SALARY',style_header)
#        ws.write(3,26,'DAYS',style_header)
#        ws.write(3,27,'SALARY',style_header)
#        ws.write(3,28,'',style_header)
#        
#        for row in obj:
#            if len(row.bonus_line) > 0:
#                columnno = 4
#                for inlinerow in row.bonus_line:
#                    ws.write(columnno,0,inlinerow.employee_id.sinid,style_header5)
#                    ws.write(columnno,1,inlinerow.employee_id.name,style_header5)
#                    ws.write(columnno,2,inlinerow.apr,style_header5)
#                    ws.write(columnno,3,inlinerow.apr_salary,style_header5)
#                    ws.write(columnno,4,inlinerow.may,style_header5)
#                    ws.write(columnno,5,inlinerow.may_salary,style_header5)
#                    ws.write(columnno,6,inlinerow.june,style_header5)
#                    ws.write(columnno,7,inlinerow.june_salary,style_header5)
#                    ws.write(columnno,8,inlinerow.july,style_header5)
#                    ws.write(columnno,9,inlinerow.july_salary,style_header5)
#                    ws.write(columnno,10,inlinerow.aug,style_header5)
#                    ws.write(columnno,11,inlinerow.aug_salary,style_header5)
#                    ws.write(columnno,12,inlinerow.sep,style_header5)
#                    ws.write(columnno,13,inlinerow.sep_salary,style_header5)
#                    ws.write(columnno,14,inlinerow.oct,style_header5)
#                    ws.write(columnno,15,inlinerow.oct_salary,style_header5)
#                    ws.write(columnno,16,inlinerow.nov,style_header5)
#                    ws.write(columnno,17,inlinerow.nov_salary,style_header5)
#                    ws.write(columnno,18,inlinerow.dec,style_header5)
#                    ws.write(columnno,19,inlinerow.dec_salary,style_header5)
#                    ws.write(columnno,20,inlinerow.jan,style_header5)
#                    ws.write(columnno,21,inlinerow.jan_salary,style_header5)
#                    ws.write(columnno,22,inlinerow.feb,style_header5)
#                    ws.write(columnno,23,inlinerow.feb_salary,style_header5)
#                    ws.write(columnno,24,inlinerow.mar,style_header5)
#                    ws.write(columnno,25,inlinerow.mar_salary,style_header5)
#                    ws.write(columnno,26,inlinerow.total_day,style_header5)
#                    ws.write(columnno,27,inlinerow.total_salary,style_header5)
#                    ws.write(columnno,28,inlinerow.bonus,style_header5)
#
#                    columnno += 1
#        f = cStringIO.StringIO()
#        wb.save(f)
#        out=base64.encodestring(f.getvalue())
#        
#        return self.write(cr, uid, ids, {'export_data':out,'filename':'Payment Bonus.xls'}, context=context)
#    
#    
#class payment_management_bonus_line(osv.osv):
#    _name='payment.management.bonus.line'
#    
#    _columns={
#              'bonus_id':fields.many2one('payment.management.bonus','Bonus'),
#              'employee_id':fields.many2one('hr.employee','Employee',required=True, readonly=True),
#              'joining_date':fields.date('Joining Date',required=True, readonly=True),
#              'company_id':fields.many2one('res.company','Company',),
#              'bonus_from':fields.date('Bonus From',required=True,readonly=True),
#              'bonus_till':fields.date('Bonus Till',required=True,readonly=True),
#              'bonus_month':fields.char('Total Month',size=64,readonly=True),
#              'bonus':fields.float('Amount',digits_compute= dp.get_precision('Account'),readonly=True),
#              'basic':fields.float('Basic'),
#              'apr':fields.float('APR'),
#              'may':fields.float('MAY'),
#              'june':fields.float('JUNE'),
#              'july':fields.float('JULY'),
#              'aug':fields.float('AUG'),
#              'sep':fields.float('SEP'),
#              'oct':fields.float('OCT'),
#              'nov':fields.float('NOV'),
#              'dec':fields.float('DEC'),
#              'jan':fields.float('JAN'),
#              'feb':fields.float('FEB'),
#              'mar':fields.float('MAR'),
#              'apr_day':fields.float('APR DAY'),
#              'may_day':fields.float('MAY DAY'),
#              'june_day':fields.float('JUNE DAY'),
#              'july_day':fields.float('JULY DAY'),
#              'aug_day':fields.float('AUG DAY'),
#              'sep_day':fields.float('SEP DAY'),
#              'oct_day':fields.float('OCT DAY'),
#              'nov_day':fields.float('NOV DAY'),
#              'dec_day':fields.float('DEC DAY'),
#              'jan_day':fields.float('JAN DAY'),
#              'feb_day':fields.float('FEB DAY'),
#              'mar_day':fields.float('MAR DAY'),
#              'apr_salary':fields.float('APR SALARY'),
#              'may_salary':fields.float('MAY SALARY'),
#              'june_salary':fields.float('JUNE SALARY'),
#              'july_salary':fields.float('JULY SALARY'),
#              'aug_salary':fields.float('AUG SALARY'),
#              'sep_salary':fields.float('SEP SALARY'),
#              'oct_salary':fields.float('OCT SALARY'),
#              'nov_salary':fields.float('NOV SALARY'),
#              'dec_salary':fields.float('DEC SALARY'),
#              'jan_salary':fields.float('JAN SALARY'),
#              'feb_salary':fields.float('FEB SALARY'),
#              'mar_salary':fields.float('MAR SALARY'),
#              'total_day':fields.float('T.DAYS'),
#              'total_month_day':fields.float('MONTH DAYS'),
#              'total_salary':fields.float('TOTAL SALARY'),
#              'user_id':fields.many2one('res.users','Created By',readonly=True),
#              'month':fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),
#                ('8','August'),('9','September'),('10','October'),('11','November'),('12','December'),],'Month',readonly=True),
#              'year_id':fields.many2one('holiday.year','Year',readonly=True),
#              
#              }
#    
#    
#    _defaults={
#              'user_id': lambda obj, cr, uid, context: uid,
#              }

class professional_tax(osv.osv):
    _name='professional.tax'
    
    def create(self, cr, uid, vals, context=None):
        year_name = ''
        if 'tax_date' in vals and vals['tax_date']:
            tm_tuple = datetime.strptime(vals['tax_date'],'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                year_name = self.pool.get('holiday.year').browse(cr, uid,year_id[0]).name
                vals['year'] = year_name
                vals['state'] = 'done'
        res = super(professional_tax, self).create(cr, uid, vals, context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        year_name = ''
        if 'tax_date' in vals and vals['tax_date']:
            tm_tuple = datetime.strptime(vals['tax_date'],'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                year_name = self.pool.get('holiday.year').browse(cr, uid,year_id[0]).name
                vals['year'] = year_name

        res = super(professional_tax, self).write(cr, uid, ids, vals, context)
        return res
    
    def _calculate_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.tax_date,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            res[each.id] = month     
        return res
    
    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.tax_date,'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                res[each.id] = year_id[0]  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res
    
    
    _columns={
              'name':fields.date('Create Date',readonly=True),
              'tax_date':fields.date('Tax Date',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'employee_id':fields.many2one('hr.employee','Employee',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'month':fields.function(_calculate_month,method=True,type='integer',string='Month',store=True),
              'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
              'tax':fields.float('Tax',digits_compute= dp.get_precision('Account'),required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'user_id':fields.many2one('res.users','Created By',readonly=True),
              'state':fields.selection([('draft','Draft'),('done','Done')],'State',readonly=True),
              'year':fields.selection([('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),
                                         ('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),
                                         ('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),
                                         ('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),
                                         ('2030','2030'),('2031','2031'),('2032','2032'),('2033','2033'),
                                         ('2034','2034'),('2035','2035'),],'YEAR'),
              }
    
    _sql_constraints = [('unique_name_employee_id_month_year','unique(employee_id,month,year_id)','Tax line is already created for this date, employee, month and year.')]
    
    _defaults={
           'name':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
           'user_id': lambda obj, cr, uid, context: uid,
           'state':'draft',
           'year':time.strftime('%Y'),
           }
    
    def onchange_employee(self, cr, uid, ids, employee, context=None):
        res = {}
        if not employee:
            return res
        cr.execute("select tax_date from professional_tax order by id desc limit 1") 
        temp = cr.fetchall()
        for data in temp:
            if data and len(data) > 0 and data[0] != None:
                date1 = data[0]
                res['value'] = {'tax_date':date1}
        return res
    
    def onchange_month(self, cr, uid, ids, month, context=None):
        res = {}
        if not month:
            res['value'] = {'year_id':False}
            return res
        month_obj = self.pool.get('holiday.list')
        month_data = month_obj.browse(cr, uid, month)
        if not month_data.year_id:
            res['warning'] = {'title': _('Warning'), 'message': _('Unable to process request, year is not selected in month.')}
        res['value'] = {'year_id':month_data.year_id and month_data.year_id.id or False}
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        
        unlink_ids = []
        for line in self.browse(cr, uid, ids, context):
            if line.state in ['draft']:
                unlink_ids.append(line.id)
            else:
                raise osv.except_osv(_('Invalid action !'), _('You cannot delete posted entry.'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)


class payment_management_vpf(osv.osv):
    _name='payment.management.vpf'
    
    def create(self, cr, uid, vals, context=None):
        year_name = ''
        if 'vpf_date' in vals and vals['vpf_date']:
            tm_tuple = datetime.strptime(vals['vpf_date'],'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                year_name = self.pool.get('holiday.year').browse(cr, uid,year_id[0]).name
                vals['year'] = year_name
                vals['state'] = 'done'
        res = super(payment_management_vpf, self).create(cr, uid, vals, context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        year_name = ''
        if 'vpf_date' in vals and vals['vpf_date']:
            tm_tuple = datetime.strptime(vals['vpf_date'],'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                year_name = self.pool.get('holiday.year').browse(cr, uid,year_id[0]).name
                vals['year'] = year_name

        res = super(payment_management_vpf, self).write(cr, uid, ids, vals, context)
        return res
    
    def _calculate_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.vpf_date,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            res[each.id] = month     
        return res
    
    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.vpf_date,'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                res[each.id] = year_id[0]  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res
    
    
    _columns={
              'name':fields.date('Create Date',readonly=True),
              'vpf_date':fields.date('VPF Date',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'employee_id':fields.many2one('hr.employee','Employee',required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'month':fields.function(_calculate_month,method=True,type='integer',string='Month',store=True),
              'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
              'vpf':fields.float('VPF',digits_compute= dp.get_precision('Account'),required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
              'user_id':fields.many2one('res.users','Created By',readonly=True),
              'state':fields.selection([('draft','Draft'),('done','Done')],'State',readonly=True),
              'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),
              'year':fields.selection([('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),
                                         ('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),
                                         ('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),
                                         ('2026','2026'),('2027','2027'),('2028','2028'),('2029','2029'),
                                         ('2030','2030'),('2031','2031'),('2032','2032'),('2033','2033'),
                                         ('2034','2034'),('2035','2035'),],'YEAR'),
              }
    
    _sql_constraints = [('unique_name_employee_id_month_year_id','unique(employee_id,month,year_id)','VPF line is already created for this date, employee, month and year.')]
    
    _defaults={
           'name':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
           'user_id': lambda obj, cr, uid, context: uid,
           'state':'draft',
           'year':time.strftime('%Y'),
           }
    
    def onchange_employee(self, cr, uid, ids, employee, context=None):
        res = {}
        if not employee:
            return res
        cr.execute("select vpf_date from payment_management_vpf order by id desc limit 1") 
        temp = cr.fetchall()
        for data in temp:
            if data and len(data) > 0 and data[0] != None:
                date1 = data[0]
                res['value'] = {'vpf_date':date1}
        return res
    
    def onchange_month(self, cr, uid, ids, month, context=None):
        res = {}
        if not month:
            res['value'] = {'year_id':False}
            return res
        month_obj = self.pool.get('holiday.list')
        month_data = month_obj.browse(cr, uid, month)
        if not month_data.year_id:
            res['warning'] = {'title': _('Warning'), 'message': _('Unable to process request, year is not selected in month.')}
        res['value'] = {'year_id':month_data.year_id and month_data.year_id.id or False}
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        
        unlink_ids = []
        for line in self.browse(cr, uid, ids, context):
            if line.state in ['draft']:
                unlink_ids.append(line.id)
            else:
                raise osv.except_osv(_('Invalid action !'), _('You cannot delete posted entry.'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
  