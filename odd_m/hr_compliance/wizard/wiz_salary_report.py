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

class wiz_salary_register(osv.TransientModel):
    _name = 'wiz.salary.report'
    
    
    def _code_get(self, cr, uid, context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        ids = report_obj.search(cr, uid, [('model','=','wiz.salary.report')])
        res = report_obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'], r['name']) for r in res]
    
    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False
    
    _columns={
              'department_id':fields.many2one('hr.department','Department'),
              'company_id': fields.many2one('res.company', 'Company',required=True),
              'month':fields.many2one('holiday.list','Month',required=True),
              'employee_id':fields.many2one('hr.employee','Employee Name'),
              'report_type':fields.selection(_code_get,'Report',required=True),
              'user_id':fields.many2one('res.users',"User Id"),
              }
    _defaults={
               'name':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
               'company_id' : _get_company_id,
               'user_id' : lambda obj, cr, uid, context: uid,
               } 

    def print_report(self, cr, uid, ids ,context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        datas = {'ids' : ids}
        type_inv = self.read(cr, uid, ids, ['report_type'])[0]
        if not type_inv['report_type']:
            raise osv.except_osv(_('Invalid action !'), _('No report is found. !'))
        rpt_id =  report_obj.search(cr, uid, [('name','=',type_inv['report_type'])])[0]
        rpt_type = report_obj.read(cr, uid, rpt_id, ['report_name'])
        return {
            'type' : 'ir.actions.report.xml',
            'report_name':str(rpt_type['report_name']),
            'datas' : datas,
            'nodestroy':True,
        }



#                        CONTRACTOR SALARY REPORTS



class wiz_contractor_salary_report(osv.TransientModel):
    _name = 'wiz.contractor.salary.report'
    
    
    def _code_get(self, cr, uid, context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        ids = report_obj.search(cr, uid, [('model','=','wiz.contractor.salary.report')])
        res = report_obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'], r['name']) for r in res]
    
    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False
    
    _columns={
              'partner_id': fields.many2one('res.partner', 'Contractor',required=True),
              'month':fields.many2one('holiday.list','Month',required=True),
              'employee_id':fields.many2one('hr.employee','Employee Name'),
              'report_type':fields.selection(_code_get,'Report',required=True),
              }

    def print_report(self, cr, uid, ids ,context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        datas = {'ids' : ids}
        type_inv = self.read(cr, uid, ids, ['report_type'])[0]
        if not type_inv['report_type']:
            raise osv.except_osv(_('Invalid action !'), _('No report is found. !'))
        rpt_id =  report_obj.search(cr, uid, [('name','=',type_inv['report_type'])])[0]
        rpt_type = report_obj.read(cr, uid, rpt_id, ['report_name'])
        return {
            'type' : 'ir.actions.report.xml',
            'report_name':str(rpt_type['report_name']),
            'datas' : datas,
            'nodestroy':True,
        }
