import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import rrule
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class form12_register(report_sxw.rml_parse):
    seq = 0
    def __init__(self, cr, uid, name, context):
        super(form12_register, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  })
        
    def get_sequence(self) :
        self.seq = self.seq + 1
        return self.seq
    
    def get_data(self,from_date,till_date,company,department,employee_ids) :
        lst1 = [] 
        emp_lst = []
        from_date = datetime.strptime(from_date,"%Y-%m-%d")
        from_date = from_date.strftime("%d-%m-%Y")
        till_date = datetime.strptime(till_date,"%Y-%m-%d")
        till_date = till_date.strftime("%d-%m-%Y")
        emp_obj = self.pool.get('hr.employee')
        for val in range(0,len(employee_ids)) :
            emp_res = emp_obj.browse(self.cr,1, employee_ids[val].id)
            emp_lst.append(emp_res.id)
        
        for emp in emp_lst :
            lst = []
            p_count = 0
            total_ot = 0
            status_lst = []
            emp_browse = emp_obj.browse(self.cr, 1, emp)
            emp_name = ' '
            sinid = ' ' 
            designation = ' '
            rel_name = ''
            department_name = ' '
            shift = ' '
            doj = emp_browse.doj

            emp_name = emp_browse.name
            sinid = emp_browse.sinid
            if emp_browse.job_id :
                designation = emp_browse.job_id.name
            if emp_browse.family_id :
                for val in emp_browse.family_id :
                    if val.relation == 'Father' :
                        rel_name = val.name
                    if val.relation == 'Husband' and rel_name == '' :
                        rel_name = val.name 
            if emp_browse.department_id :
                department_name = emp_browse.department_id.name
            if emp_browse.shift_lines :
                for shift_line in emp_browse.shift_lines :
                    shift = shift_line.shift_id.name
                if shift == 'GENERAL' :
                    shift = 'GEN'
                elif shift == 'STAFF' :
                    shift = 'STF'
                elif shift == 'GUARD A' :
                    shift = 'GRD A'
                elif shift == 'GUARD B' :
                    shift = 'GRD B'
                elif shift == 'GUARD C' :
                    shift = 'GRD C'
                else :
                    shift = shift[0:2]
            lst.append(emp_name)
            lst.append(sinid)
            lst.append(designation)
            lst.append(rel_name)
            lst.append(department_name)
            lst.append(shift)
            
            for val_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(from_date,'%d-%m-%Y'),until=datetime.strptime(till_date,'%d-%m-%Y')):
                q2 = self.cr.execute("select over_time,working from attendance_timing where employee_id='"+str(emp_browse.id)+"' and name='"+str(val_date)+"'  ")
                t2 = self.cr.fetchall()
                if t2 :   
                    status = t2[0][1]
                    if status == 'POW':
                        status = 'PW'
                    if status == 'POH':
                        status = 'PH'
                        
                    if status == 'P':
                        p_count += 1              
                    status_lst.append(status)
                    total_ot += t2[0][0]
                                
                if len(t2) == 0 :
                    q3 = self.cr.execute("select week from holiday_list_lines where leave_date='"+str(val_date)+"'  ")
                    t3 = self.cr.fetchall()
                    if t3 :
                        t3 = t3[0][0]
                        if t3 == 'Sunday' :
                            status = 'WO'
                            status_lst.append(status)
                        else :
                            status = 'HL'
                            status_lst.append(status)
                            
                if len(t2) == 0 and len(t3) == 0 : 
                    q4 = self.cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp_browse.id)+"' and state='validate' and type='remove' ")
                    t4 = self.cr.fetchall()
                    status = ''
                    if t4 :    
                        for val1 in t4 :
                            for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                if leave_date == val_date :
                                    if val1[2] == 'Earned Leaves' : 
                                        status = 'EL'
                                        status_lst.append(status)
                                    elif val1[2] == 'Compensatory Days' : 
                                        status = 'COM'
                                        status_lst.append(status)
                                    elif val1[2][0:4] == 'Sick' : 
                                        status = 'SL'
                                        status_lst.append(status)
                                    elif val1[2][0:4] == 'Casu' : 
                                        status = 'CL'
                                        status_lst.append(status)
                                    elif val1[2] == 'Factory Work': 
                                        status = 'FW'
                                        status_lst.append(status)
                                        
                    if status == '' :
                        if doj <= val_date.strftime("%Y-%m-%d") :
                            status = 'A'
                        else :
                            status = ''
                        status_lst.append(status)
            
            for val in status_lst :
                if len(status_lst) != 31 :
                    status_lst.append(' ')
            
            lst.append(status_lst)
            lst.append(p_count)
#             total_ot_hrs = float(total_ot)/60
#             total_ot_hrs = str(total_ot_hrs)
#             total_ot_hrs = total_ot_hrs.split('.')
#             total_ot_hrs = total_ot_hrs[0]
#             total_ot_min = (total_ot)%60
#             total_ot_min = int(total_ot_min)
#             total_ot_min = str(total_ot_min)
#             total_ot = total_ot_hrs + '.' + total_ot_min   
#             lst.append(total_ot)
            lst1.append(lst)
        return lst1
            
    
class report_form12_register(osv.AbstractModel):
    _name = 'report.hr_compliance.report_form12_register'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_form12_register'
    _wrapped_report_class = form12_register





#                                            CONTRACTOR FORM12 REGISTER


class contractor_form12_register(report_sxw.rml_parse):
    seq = 0
    def __init__(self, cr, uid, name, context):
        super(contractor_form12_register, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  })
        
    def get_sequence(self) :
        self.seq = self.seq + 1
        return self.seq
    
    def get_data(self,from_date,till_date,partner,employee_ids) :
        lst1 = [] 
        emp_lst = []
        from_date = datetime.strptime(from_date,"%Y-%m-%d")
        from_date = from_date.strftime("%d-%m-%Y")
        till_date = datetime.strptime(till_date,"%Y-%m-%d")
        till_date = till_date.strftime("%d-%m-%Y")
        emp_obj = self.pool.get('hr.employee')
        for val in range(0,len(employee_ids)) :
            emp_res = emp_obj.browse(self.cr,1, employee_ids[val].id)
            emp_lst.append(emp_res.id)
        
        for emp in emp_lst :
            lst = []
            p_count = 0
            total_ot = 0
            status_lst = []
            emp_browse = emp_obj.browse(self.cr, 1, emp)
            emp_name = ' '
            sinid = ' ' 
            designation = ' '
            rel_name = ''
            department_name = ' '
            shift = ' '
            doj = emp_browse.doj

            emp_name = emp_browse.name
            sinid = emp_browse.sinid
            if emp_browse.job_id :
                designation = emp_browse.job_id.name
            if emp_browse.family_id :
                for val in emp_browse.family_id :
                    if val.relation == 'Father' :
                        rel_name = val.name
                    if val.relation == 'Husband' and rel_name == '' :
                        rel_name = val.name 
            if emp_browse.department_id :
                department_name = emp_browse.department_id.name
            if emp_browse.shift_lines :
                for shift_line in emp_browse.shift_lines :
                    shift = shift_line.shift_id.name
                if shift == 'GENERAL' :
                    shift = 'GEN'
                elif shift == 'STAFF' :
                    shift = 'STF'
                elif shift == 'GUARD A' :
                    shift = 'GRD A'
                elif shift == 'GUARD B' :
                    shift = 'GRD B'
                elif shift == 'GUARD C' :
                    shift = 'GRD C'
                else :
                    shift = shift[0:2]
            lst.append(emp_name)
            lst.append(sinid)
            lst.append(designation)
            lst.append(rel_name)
            lst.append(department_name)
            lst.append(shift)
            
            for val_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(from_date,'%d-%m-%Y'),until=datetime.strptime(till_date,'%d-%m-%Y')):
                q2 = self.cr.execute("select over_time,working from attendance_timing where employee_id='"+str(emp_browse.id)+"' and name='"+str(val_date)+"'  ")
                t2 = self.cr.fetchall()
                if t2 :   
                    status = t2[0][1]
                    if status == 'POW':
                        status = 'PW'
                    if status == 'POH':
                        status = 'PH'
                        
                    if status == 'P':
                        p_count += 1              
                    status_lst.append(status)
                    total_ot += t2[0][0]
                                
                if len(t2) == 0 :
                    q3 = self.cr.execute("select week from holiday_list_lines where leave_date='"+str(val_date)+"'  ")
                    t3 = self.cr.fetchall()
                    if t3 :
                        t3 = t3[0][0]
                        if t3 == 'Sunday' :
                            status = 'WO'
                            status_lst.append(status)
                        else :
                            status = 'HL'
                            status_lst.append(status)
                            
                if len(t2) == 0 and len(t3) == 0 : 
                    q4 = self.cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp_browse.id)+"' and state='validate' and type='remove' ")
                    t4 = self.cr.fetchall()
                    status = ''
                    if t4 :    
                        for val1 in t4 :
                            for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                if leave_date == val_date :
                                    if val1[2] == 'Earned Leaves' : 
                                        status = 'EL'
                                        status_lst.append(status)
                                    elif val1[2] == 'Compensatory Days' : 
                                        status = 'COM'
                                        status_lst.append(status)
                                    elif val1[2][0:4] == 'Sick' : 
                                        status = 'SL'
                                        status_lst.append(status)
                                    elif val1[2][0:4] == 'Casu' : 
                                        status = 'CL'
                                        status_lst.append(status)
                                    elif val1[2] == 'Factory Work': 
                                        status = 'FW'
                                        status_lst.append(status)
                                        
                    if status == '' :
                        if doj <= val_date.strftime("%Y-%m-%d") :
                            status = 'A'
                        else :
                            status = ''
                        status_lst.append(status)
            
            for val in status_lst :
                if len(status_lst) != 31 :
                    status_lst.append(' ')
            
            lst.append(status_lst)
            lst.append(p_count)
            lst1.append(lst)
        return lst1
            
    
class report_contractor_form12_register(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_form12_register'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_form12_register'
    _wrapped_report_class = contractor_form12_register
