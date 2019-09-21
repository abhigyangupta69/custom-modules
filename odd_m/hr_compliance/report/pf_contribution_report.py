import time
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.report import report_sxw
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class pf_contribution(report_sxw.rml_parse):
    
    seq = 0
    epf_wages = 0
    epf = 0
    eps = 0
    diff = 0
    def __init__(self, cr, uid, name, context):
        super(pf_contribution, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  "get_epf_wages":self.get_epf_wages,
                                  "get_epf":self.get_epf,
                                  "get_eps":self.get_eps,
                                  "get_diff":self.get_diff,
                                  })
        
    def get_sequence(self):
        self.seq = self.seq + 1
        return self.seq
        
        
    def get_data(self,month,company,department,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if department and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('department_id', '=', department.id),('company_id','=',company.id),('active','=',True)])
        elif department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('company_id','=',company.id),('active','=',True)])
        elif employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('company_id','=',company.id),('active','=',True)])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id),('active','=',True)])

        if len(list_ids) == 0 :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
         
        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,hr.pf_number,spl.employee_name,spl.gross,spl.epf,spl.epf1,spl.epf2 from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' order by spl.employee_name ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,hr.pf_number,spl.employee_name,spl.gross,spl.epf,spl.epf1,spl.epf2 from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' order by spl.employee_name ")
            temp = self.cr.fetchall()
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        for val in temp :
            if val[3]:
                self.epf_wages = self.epf_wages + val[3]
            if val[4]:    
                self.epf = self.epf + val[4]
            if val[5]:    
                self.eps = self.eps + val[5]
            if val[6]:    
                self.diff = self.diff + val[6]
        return temp
    
    def get_epf_wages(self) :
        return self.epf_wages
    
    def get_epf(self) :
        return self.epf

    def get_eps(self) :
        return self.eps

    def get_diff(self) :
        return self.diff
    
    
class report_pf_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_pf_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_pf_contribution_temp_id'
    _wrapped_report_class = pf_contribution


