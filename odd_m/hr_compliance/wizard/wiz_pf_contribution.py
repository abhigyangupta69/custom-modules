from openerp.osv import fields,osv
from openerp import tools
from openerp.tools import amount_to_text_en
from datetime import datetime
from datetime import date, timedelta
from openerp import pooler, tools
from openerp.tools import flatten
from dateutil.relativedelta import *
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp.tools.translate import _
import time


class wiz_pf_contribution(osv.TransientModel):
    _name = 'wiz.pf.contribution'
        
    _columns = {
                'month':fields.many2one('holiday.list','Month'),
                'company_id':fields.many2one('res.company','Company'),
                'department_id':fields.many2one('hr.department','Department'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                }
        
    
    def print_report(self,cr,uid,ids,context=None):
            wiz_obj=self.pool.get('wiz.pf.contribution').browse(cr,uid,ids[0])
            report_obj = self.pool.get('ir.actions.report.xml')
            datas = {'ids' : ids}
            rpt_id =  report_obj.search(cr, uid, [('model','=','wiz.pf.contribution')])
            if not rpt_id:
                raise osv.except_osv(_('Invalid action !'), _('Report for this name order not exist.'))
            rpt_type = report_obj.read(cr, uid, rpt_id, ['report_name'])[0]
            print " this is name of report ",rpt_type['report_name']
            return {
               'type' : 'ir.actions.report.xml',
               'report_name':str(rpt_type['report_name']),
               'datas' : datas,
               'nodestroy':True,
            }
              
              
