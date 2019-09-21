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

class wiz_salary(osv.TransientModel):
    _name = 'wiz.salary'
    
    _columns = {
                'name':fields.datetime('Creation Date',readonly=True),
                'month':fields.many2one('holiday.list','Month',required=True),
                }
    _defaults = {
                 'name':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                 }
    
    def print_report(self,cr,uid,ids,context=None):
        sales_obj=self.pool.get('wiz.salary').browse(cr,1,ids[0])
        report_obj = self.pool.get('ir.actions.report.xml')
        datas = {'ids' : ids}
        rpt_id =  report_obj.search(cr, uid, [('model','=','wiz.salary')])
        if not rpt_id:
            raise osv.except_osv(_('Invalid action !'), _('Report for this name order no exist.'))
        rpt_type = report_obj.read(cr, uid, rpt_id, ['report_name'])[0]
        
        return {
           'type' : 'ir.actions.report.xml',
           'report_name':str(rpt_type['report_name']),
           'datas' : datas,
           'nodestroy':True,
        }
                
    