import time
import math
from openerp.report import report_sxw
from datetime import datetime
from datetime import date, timedelta
from openerp import pooler, tools
from openerp.tools import flatten
from dateutil.relativedelta import *
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp.tools import amount_to_text_en

class salary_sheet_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(salary_sheet_report, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
            'salary':self.salary,
            'get_time':self.get_time,
            'total_salary':self.total_salary,
            })
        
    def get_time(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
        
        return date1
    
    def salary(self, month, year):
        if month and year:
            qry = "select emp.sinid,res.name,sal.basic::integer,sal.days,sal.days_amount::integer," \
            "sal.over_time,sal.overtime_amount::integer,sal.sun_over_time,sal.sun_overtime_amount::integer,sal.total_amount::integer," \
            "sal.epf::integer,sal.esi::integer,sal.tds::integer,sal.kharcha::integer,sal.loan::integer,"\
            "(sal.epf::integer+sal.esi::integer+sal.tds::integer+sal.kharcha::integer+sal.loan::integer), " \
            "sal.grand_total::integer from salary_payment_line as sal left join hr_employee as emp on " \
            "(sal.employee_id=emp.id) left join resource_resource as res on (emp.resource_id=res.id) "\
            "left join  hr_job as desg on (emp.job_id=desg.id) where month='"+str(month)+"' and year_id='"+str(year)+"' " \
            "order by (substring(emp.sinid, '^[0-9]+'))::int ,substring(emp.sinid, '[^0-9_].*$')"
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            return temp
        
    def total_salary(self, month, year):
        if month and year:
            qry = "select sum(sal.days_amount::integer),sum(sal.total_amount::integer),sum(sal.grand_total::integer)," \
            "sum(sal.epf::integer+sal.esi::integer+sal.tds::integer+sal.kharcha::integer+sal.loan::integer) "\
            " from salary_payment_line as sal left join hr_employee as emp on " \
            "(sal.employee_id=emp.id) left join resource_resource as res on (emp.resource_id=res.id) "\
            "left join  hr_job as desg on (emp.job_id=desg.id) where month='"+str(month)+"' and year_id='"+str(year)+"' " 
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            return temp
            

        
report_sxw.report_sxw('report.salary.sheet.report', "wiz.salary", 'addons/hr_compliance/report/salary_sheet.rml', parser=salary_sheet_report, header="external")        
