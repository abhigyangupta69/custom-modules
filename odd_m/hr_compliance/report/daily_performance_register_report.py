import time
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp  import api ,models
from dateutil import rrule
from openerp.tools.translate import _

class daily_performance_register(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(daily_performance_register, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                 "get_date":self.get_date,
                                 "get_data":self.get_data,
                                  })
    
    def get_time(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
        return date1
     
    def get_date(self,date):
        date1=datetime.strptime(date,"%Y-%m-%d")
        date1 = date1.strftime("%d-%m-%Y") 
        return date1
    
    
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
      
    def get_data(self,date,company,department,chk_status):
        l = []
        list_ids = [] 
        date = datetime.strptime(date,"%Y-%m-%d")
        date_str = date.strftime('%Y-%m-%d')
        from_date_str = date_str + ' 00:00:00'
        from_date_str = datetime.strptime(from_date_str,"%Y-%m-%d %H:%M:%S")
        from_date_str = from_date_str - timedelta(hours=5,minutes=30)
        from_date_str = from_date_str.strftime("%Y-%m-%d %H:%M:%S")
        
        till_date_str = date_str + ' 23:59:59'
        till_date_str = datetime.strptime(till_date_str,"%Y-%m-%d %H:%M:%S")
        till_date_str = till_date_str - timedelta(hours=5,minutes=30)
        till_date_str = till_date_str.strftime("%Y-%m-%d %H:%M:%S")
        
        emp_obj = self.pool.get('hr.employee')
        if company and department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('active','=',True),('company_id','=',company.id),('type','=','Employee')])
        elif company:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id), ('active','=',True),('type','=','Employee')])
        elif department:
            raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
        else:
            list_ids = emp_obj.search(self.cr, 1, [('active','=',True),('type','=','Employee')])   
        for emp in list_ids :
            temp1 = []
            tup = ()
            designation = ''
            department_name = ''
            in_time = ''
            out_time = ''
            working_time = ''
            late = 0
            early = 0
            shift_from = ''
            shift_to = ''
            shift = ''
            status = ''
            emp_browse = emp_obj.browse(self.cr, 1, emp)
            doj = emp_browse.doj
            emp_name = emp_browse.name
            sinid = emp_browse.sinid
            paycode = emp_browse.paycode
            query1 = self.cr.execute("select shift.name,sline.from_time,sline.working_time,sline.to_time,sline.lunch_time from attendance_shift_line as sline left join attendance_shift as shift on (sline.shift_id=shift.id) "
                                     "left join hr_shift_line as hr_sline on (hr_sline.shift_id=shift.id) where hr_sline.employee_id='"+str(emp)+"' and hr_sline.name<='"+str(date)+"' order by hr_sline.name desc limit 1 ")
            temp1 = self.cr.fetchall()
            if len(temp1) > 0:
                shift = temp1[0][0]
                if shift == 'GENERAL':
                    shift = 'GEN'
                elif shift == 'STAFF':
                    shift = 'STF'
                elif shift == 'GUARD A':
                    shift = 'GRD A'
                elif shift == 'GUARD B':
                    shift = 'GRD B'
                elif shift == 'GUARD C':
                    shift = 'GRD C'
                elif shift == '2ND SHIFT':
                    shift = '2ND'
                else :
                    shift = shift[0:2]
                shift_from = str(temp1[0][1]).split('.')
                shift_from_min = int((int(shift_from[1])*60)/100)
                shift_from = shift_from[0] + ':' + str(shift_from_min)
                shift_to = str(temp1[0][3]).split('.')
                shift_to_min = int((int(shift_to[1])*60)/100)
                shift_to = shift_to[0] + ':' + str(shift_to_min)
            else:
                if doj <= date_str:
                    raise osv.except_osv(_('Warning !'), _("Shift is Missing for Employee %s" %(sinid)))

            if emp_browse.job_id :
                designation = emp_browse.job_id.name
            if emp_browse.department_id :
                department_name = emp_browse.department_id.name
            hr_atten_search = self.pool.get('hr.attendance').search(self.cr,1,[('search_date','>=',date_str),('search_date','<=',date_str),('employee_id','=',emp)])
            if len(hr_atten_search) == 1:
                raise osv.except_osv(_('Warning !!!!'),_("Only 1 Punch Found For Employee [ " +(sinid)+" ] " "on Date %s" % (date)))
            if hr_atten_search :
                hr_atten_lst = []
                for hr_atten_id in hr_atten_search :
                    hr_atten_browse = self.pool.get('hr.attendance').browse(self.cr,1,hr_atten_id).name
                    attendance = datetime.strptime(hr_atten_browse,"%Y-%m-%d %H:%M:%S")
                    attendance = attendance + timedelta(hours=5,minutes=30)
                    attendance = attendance.strftime("%d-%m-%Y %H:%M:%S")
                    hr_atten_lst.append(attendance)
                hr_atten_lst.sort()
                in_punch = hr_atten_lst[0]
                out_punch = hr_atten_lst[1]
                in_punch = datetime.strptime(in_punch,"%d-%m-%Y %H:%M:%S")
                out_punch = datetime.strptime(out_punch,"%d-%m-%Y %H:%M:%S")

                in_time = in_punch.strftime('%H:%M')
                out_time = out_punch.strftime('%H:%M')
                t11 = str(temp1[0][1])
                t11 = t11.split('.')
                t1_min = (int(t11[0])*60) + int((int(t11[1])*60)/100)
                in_time_min = in_time.split(':')
                in_time_min = (int(in_time_min[0])*60) + int(in_time_min[1])
                out_time_min = out_time.split(':')
                out_time_min = (int(out_time_min[0])*60) + int(out_time_min[1])

                if in_time_min > t1_min and in_punch.strftime('%Y-%m-%d') == date_str:
                    late = in_time_min - t1_min
                if t1_min > in_time_min :
                    early = t1_min - in_time_min
                    
                interval = temp1[0][4]
                
#                lunch_start = datetime.strptime('13:00',"%H:%M")
#                lunch_start = lunch_start.strftime('%H:%M')
#                lunch_end = datetime.strptime('13:45',"%H:%M")
#                lunch_end = lunch_end.strftime('%H:%M')

#                if (in_time < lunch_start) and (out_time >= lunch_end) and temp1[0][2] > 8 :
#                    interval = 45
#                elif (in_time < lunch_start) and (out_time < lunch_start) and temp1[0][2] > 8 :
#                    interval = 0
#                elif (in_time < lunch_start) and (out_time < lunch_end) and temp1[0][2] > 8 :
#                    interval = out_time_min - (13*60)
#                elif (in_time >= lunch_end) and temp1[0][2] > 8 :
#                    interval = 0
#                elif (in_time > lunch_start) and (in_time <= lunch_end) and temp1[0][2] > 8 :
#                    interval = ((13*60)+45) - in_time_min

                time_diff = out_punch - in_punch
                time_diff_lst = str(time_diff).split(':')
                time_diff_min = int(time_diff_lst[0])*60 + int(time_diff_lst[1]) - interval

                working_hrs = float(time_diff_min)/60
                working_hrs = str(working_hrs)
                working_hrs = working_hrs.split('.')
                working_hrs = working_hrs[0]
                working_min = time_diff_min%60
                working_min = str(working_min)
                if len(working_min) == 1 :
                    working_min = '0' + working_min
                working_time = working_hrs + '.' + working_min

            status = ''
            over_time = ''
            t2 = []
            t3 = []
            q2 = self.cr.execute("select over_time,working from attendance_timing where employee_id='"+str(emp)+"' and name='"+str(date_str)+"'  ")
            t2 = self.cr.fetchall()
            if t2 :
                ot_hrs = float(t2[0][0])/60
                ot_hrs = str(ot_hrs)
                ot_hrs = ot_hrs.split('.')
                ot_hrs = ot_hrs[0]
                ot_min = (t2[0][0])%60
                ot_min = int(ot_min)
                ot_min = str(ot_min)
                if len(ot_min) == 1 :
                    ot_min = '0' + ot_min
                over_time = ot_hrs + '.' + ot_min                
                status = t2[0][1]
                
            if len(t2) == 0 :
                q3 = self.cr.execute("select week from holiday_list_lines where leave_date='"+str(date_str)+"'  ")
                t3 = self.cr.fetchall()
                if t3 :
                    t3 = t3[0][0]
                    over_time = ''
                    if t3 == 'Sunday' :
                        status = 'WO'
                    else :
                        status = 'HLD'
                    
            if len(t2) == 0 and len(t3) == 0 : 
                q4 = self.cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp)+"' and state='validate' and type='remove' ")
                t4 = self.cr.fetchall()
                status = ''
                if t4 :    
                    for val1 in t4 :
                        for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                            if leave_date == date :
                                over_time = ''
                                if val1[2] == 'Earned Leaves' : status = 'EL'
                                elif val1[2] == 'Compensatory Days' : status = 'COM'
                                elif val1[2][0:4] == 'Sick' : status = 'SL'
                                elif val1[2][0:4] == 'Casu' : status = 'CL'
                if status == '' :
                    status = 'A'
                    over_time = ''
  
            if doj > date_str :
                tup = (paycode,sinid,emp_name,department_name,designation,shift,shift_from,shift_to,'N/A','N/A','N/A','N/A','N/A','N/A','N/A')             
                l.append(tup)
  
            elif chk_status and chk_status == 'P' :
                if status == 'P' :
                    tup = (paycode,sinid,emp_name,department_name,designation,shift,shift_from,shift_to,in_time,out_time,working_time,status,early,late,over_time)
                    l.append(tup)
            elif chk_status and chk_status == 'A' :
                if status == 'A' :
                    tup = (paycode,sinid,emp_name,department_name,designation,shift,shift_from,shift_to,in_time,out_time,working_time,status,early,late,over_time)             
                    l.append(tup)
                
            else:
                tup = (paycode,sinid,emp_name,department_name,designation,shift,shift_from,shift_to,in_time,out_time,working_time,status,early,late,over_time)
                l.append(tup)

        return l
                
    
class report_daily_performance_register(osv.AbstractModel):
    _name = 'report.hr_compliance.report_daily_performance_register'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_daily_performance_register'
    _wrapped_report_class = daily_performance_register

        
#                                           Daily Performance Register Contractor Report
        
class daily_performance_register_contractor(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(daily_performance_register_contractor, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                 "get_date":self.get_date,
                                 "get_data":self.get_data,
                                  })
    
    def get_time(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
        return date1
     
    def get_date(self,date):
        date1=datetime.strptime(date,"%Y-%m-%d")
        date1 = date1.strftime("%d-%m-%Y") 
        return date1
    
    
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
      
    def get_data(self,date,employee,chk_status,partner):
        l = []
        list_ids = []
        date = datetime.strptime(date,"%Y-%m-%d")
        date_str = date.strftime('%Y-%m-%d')
        from_date_str = date_str + ' 00:00:00'
        from_date_str = datetime.strptime(from_date_str,"%Y-%m-%d %H:%M:%S")
        from_date_str = from_date_str - timedelta(hours=5,minutes=30)
        from_date_str = from_date_str.strftime("%Y-%m-%d %H:%M:%S")

        till_date_str = date_str + ' 23:59:59'
        till_date_str = datetime.strptime(till_date_str,"%Y-%m-%d %H:%M:%S")
        till_date_str = till_date_str - timedelta(hours=5,minutes=30)
        till_date_str = till_date_str.strftime("%Y-%m-%d %H:%M:%S")

        emp_obj = self.pool.get('hr.employee')
        if partner and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id','=',employee.id),('partner_id','=',partner.id),('active','=',True),('type','=','Contractor')])
        elif partner:
            list_ids = emp_obj.search(self.cr, 1, [('partner_id','=',partner.id), ('active','=',True),('type','=','Contractor')])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('active','=',True),('type','=','Contractor')])
        for emp in list_ids :
            temp1 = []
            tup = ()
            designation = ''
            department_name = ''
            in_time = ''
            out_time = ''
            working_time = ''
            late = 0
            early = 0
            shift_from = ''
            shift_to = ''
            shift = ''
            status = ''
            emp_browse = emp_obj.browse(self.cr, 1, emp)
            doj = emp_browse.doj
            emp_name = emp_browse.name
            sinid = emp_browse.sinid
            paycode = emp_browse.paycode
            
            query1 = self.cr.execute("select shift.name,sline.from_time,sline.working_time,sline.to_time,sline.lunch_time from attendance_shift_line as sline left join attendance_shift as shift on (sline.shift_id=shift.id) "
                                     "left join hr_shift_line as hr_sline on (hr_sline.shift_id=shift.id) where hr_sline.employee_id='"+str(emp)+"' and hr_sline.name<='"+str(date)+"' order by hr_sline.name desc limit 1 ")
            temp1 = self.cr.fetchall()
            if len(temp1) > 0:
                shift = temp1[0][0]
                if shift == 'GENERAL':
                    shift = 'GEN'
                elif shift == 'STAFF':
                    shift = 'STF'
                elif shift == 'GUARD A':
                    shift = 'GRD A'
                elif shift == 'GUARD B':
                    shift = 'GRD B'
                elif shift == 'GUARD C':
                    shift = 'GRD C'
                elif shift == '2ND SHIFT':
                    shift = '2ND'
                else :
                    shift = shift[0:2]
                shift_from = str(temp1[0][1]).split('.')
                shift_from_min = int((int(shift_from[1])*60)/100)
                shift_from = shift_from[0] + ':' + str(shift_from_min)
                shift_to = str(temp1[0][3]).split('.')
                shift_to_min = int((int(shift_to[1])*60)/100)
                shift_to = shift_to[0] + ':' + str(shift_to_min)
            else:
                if doj <= date_str:
                    raise osv.except_osv(_('Warning !'), _("Shift is Missing for Employee %s" %(sinid)))
            
            if emp_browse.job_id :
                designation = emp_browse.job_id.name
            if emp_browse.department_id :
                department_name = emp_browse.department_id.name
            hr_atten_search = self.pool.get('hr.attendance').search(self.cr,1,[('search_date','>=',date_str),('search_date','<=',date_str),('employee_id','=',emp)])
            if len(hr_atten_search) == 1:
                raise osv.except_osv(_('Warning !!!!'),_("Only 1 Punch Found For Employee [ " +(sinid)+" ] " "on Date %s" % (date)))
            if hr_atten_search :
                hr_atten_lst = []
                for hr_atten_id in hr_atten_search :
                    hr_atten_browse = self.pool.get('hr.attendance').browse(self.cr,1,hr_atten_id).name
                    attendance = datetime.strptime(hr_atten_browse,"%Y-%m-%d %H:%M:%S")
                    attendance = attendance + timedelta(hours=5,minutes=30)
                    attendance = attendance.strftime("%d-%m-%Y %H:%M:%S")
                    hr_atten_lst.append(attendance)
                hr_atten_lst.sort()
                in_punch = hr_atten_lst[0]
                out_punch = hr_atten_lst[1]
                in_punch = datetime.strptime(in_punch,"%d-%m-%Y %H:%M:%S")
                out_punch = datetime.strptime(out_punch,"%d-%m-%Y %H:%M:%S")

                in_time = in_punch.strftime('%H:%M')
                out_time = out_punch.strftime('%H:%M')
                t11 = str(temp1[0][1])
                t11 = t11.split('.')
                t1_min = (int(t11[0])*60) + int((int(t11[1])*60)/100)
                in_time_min = in_time.split(':')
                in_time_min = (int(in_time_min[0])*60) + int(in_time_min[1])
                out_time_min = out_time.split(':')
                out_time_min = (int(out_time_min[0])*60) + int(out_time_min[1])

                if in_time_min > t1_min and in_punch.strftime('%Y-%m-%d') == date_str:
                    late = in_time_min - t1_min
                if t1_min > in_time_min :
                    early = t1_min - in_time_min
                    
                interval = temp1[0][4]
                
#                lunch_start = datetime.strptime('13:00',"%H:%M")
#                lunch_start = lunch_start.strftime('%H:%M')
#                lunch_end = datetime.strptime('13:45',"%H:%M")
#                lunch_end = lunch_end.strftime('%H:%M')

#                if (in_time < lunch_start) and (out_time >= lunch_end) and temp1[0][2] > 8 :
#                    interval = 45
#                elif (in_time < lunch_start) and (out_time < lunch_start) and temp1[0][2] > 8 :
#                    interval = 0
#                elif (in_time < lunch_start) and (out_time < lunch_end) and temp1[0][2] > 8 :
#                    interval = out_time_min - (13*60)
#                elif (in_time >= lunch_end) and temp1[0][2] > 8 :
#                    interval = 0
#                elif (in_time > lunch_start) and (in_time <= lunch_end) and temp1[0][2] > 8 :
#                    interval = ((13*60)+45) - in_time_min

                time_diff = out_punch - in_punch
                time_diff_lst = str(time_diff).split(':')
                time_diff_min = int(time_diff_lst[0])*60 + int(time_diff_lst[1]) - interval

                working_hrs = float(time_diff_min)/60
                working_hrs = str(working_hrs)
                working_hrs = working_hrs.split('.')
                working_hrs = working_hrs[0]
                working_min = time_diff_min%60
                working_min = str(working_min)
                if len(working_min) == 1 :
                    working_min = '0' + working_min
                working_time = working_hrs + '.' + working_min



            status = ''
            over_time = ''
            t2 = []
            t3 = []
            q2 = self.cr.execute("select over_time,working from attendance_timing where employee_id='"+str(emp)+"' and name='"+str(date_str)+"'  ")
            t2 = self.cr.fetchall()
            if t2 :
                ot_hrs = float(t2[0][0])/60
                ot_hrs = str(ot_hrs)
                ot_hrs = ot_hrs.split('.')
                ot_hrs = ot_hrs[0]
                ot_min = (t2[0][0])%60
                ot_min = int(ot_min)
                ot_min = str(ot_min)
                if len(ot_min) == 1 :
                    ot_min = '0' + ot_min
                over_time = ot_hrs + '.' + ot_min                
                status = t2[0][1]
                
            if len(t2) == 0 :
                q3 = self.cr.execute("select week from holiday_list_lines where leave_date='"+str(date_str)+"'  ")
                t3 = self.cr.fetchall()
                if t3 :
                    t3 = t3[0][0]
                    over_time = ''
                    if t3 == 'Sunday' :
                        status = 'WO'
                    else :
                        status = 'HLD'
                    
            if len(t2) == 0 and len(t3) == 0 : 
                q4 = self.cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp)+"' and state='validate' and type='remove' ")
                t4 = self.cr.fetchall()
                status = ''
                if t4 :    
                    for val1 in t4 :
                        for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                            if leave_date == date :
                                over_time = ''
                                if val1[2] == 'Earned Leaves' : status = 'EL'
                                elif val1[2] == 'Compensatory Days' : status = 'COM'
                                elif val1[2][0:4] == 'Sick' : status = 'SL'
                                elif val1[2][0:4] == 'Casu' : status = 'CL'
                if status == '' :
                    status = 'A'
                    over_time = ''


            if doj > date_str :
                tup = (paycode,sinid,emp_name,department_name,designation,shift,shift_from,shift_to,'N/A','N/A','N/A','N/A','N/A','N/A','N/A')
                l.append(tup)

            elif chk_status and chk_status == 'P' :
                if status == 'P' :
                    tup = (paycode,sinid,emp_name,department_name,designation,shift,shift_from,shift_to,in_time,out_time,working_time,status,early,late,over_time)
                    l.append(tup)
            elif chk_status and chk_status == 'A' :
                if status == 'A' :
                    tup = (paycode,sinid,emp_name,department_name,designation,shift,shift_from,shift_to,in_time,out_time,working_time,status,early,late,over_time)
                    l.append(tup)

            else:
                tup = (paycode,sinid,emp_name,department_name,designation,shift,shift_from,shift_to,in_time,out_time,working_time,status,early,late,over_time)
                l.append(tup)

        return l
                
    
class report_daily_performance_register_contractor(osv.AbstractModel):
    _name = 'report.hr_compliance.report_daily_performance_register_contractor'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_daily_performance_register_contractor'
    _wrapped_report_class = daily_performance_register_contractor
        
        
