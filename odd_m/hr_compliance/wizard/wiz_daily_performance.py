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

class wiz_daily_performance(osv.TransientModel):
    _name = 'wiz.daily.performance'
    
    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False
    
    _columns={
              'name':fields.datetime('Creation Date',readonly=True),
              'company_id': fields.many2one('res.company', 'Company',required=True),
              'date':fields.date('Date',),
              'department_id':fields.many2one('hr.department','Department'),
              'status':fields.selection([('P','P'),('A','A')],'Status'),
              'user_id':fields.many2one('res.users',"User ID")
              }
    _defaults={
               'name':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
               'company_id' : _get_company_id,
               'user_id' : lambda obj, cr, uid, context: uid,
               } 

    def print_report(self,cr,uid,ids,context=None):
            wiz_obj=self.pool.get('wiz.daily.performance').browse(cr,uid,ids[0])
            report_obj = self.pool.get('ir.actions.report.xml')
            datas = {'ids' : ids}
            rpt_id =  report_obj.search(cr, uid, [('model','=','wiz.daily.performance')])
            if not rpt_id:
                raise osv.except_osv(_('Invalid action !'), _('Report for this name order not exist.'))
            rpt_type = report_obj.read(cr, uid, rpt_id, ['report_name'])[0]
            return {
               'type' : 'ir.actions.report.xml',
               'report_name':str(rpt_type['report_name']),
               'datas' : datas,
               'nodestroy':True,
            }
            
            
#            Daily Performance Contractor Report
            
class wiz_daily_performance_contractor(osv.TransientModel):
    _name = 'wiz.daily.performance.contractor'
    
    _columns={
              'name':fields.datetime('Creation Date',readonly=True),
              'date':fields.date('Date',),
              'status':fields.selection([('P','P'),('A','A')],'Status'),
              'employee_id':fields.many2one('hr.employee','Employee'),
              'partner_id':fields.many2one('res.partner','Contractor'),
              'user_id':fields.many2one('res.users',"User ID")
              }
    _defaults={
               'name':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
               'user_id' : lambda obj, cr, uid, context: uid,
               } 

    def print_report(self,cr,uid,ids,context=None):
            wiz_obj=self.pool.get('wiz.daily.performance.contractor').browse(cr,uid,ids[0])
            report_obj = self.pool.get('ir.actions.report.xml')
            datas = {'ids' : ids}
            rpt_id =  report_obj.search(cr, uid, [('model','=','wiz.daily.performance.contractor')])
            if not rpt_id:
                raise osv.except_osv(_('Invalid action !'), _('Report for this name order not exist.'))
            rpt_type = report_obj.read(cr, uid, rpt_id, ['report_name'])[0]
            return {
               'type' : 'ir.actions.report.xml',
               'report_name':str(rpt_type['report_name']),
               'datas' : datas,
               'nodestroy':True,
            }
            
            
     