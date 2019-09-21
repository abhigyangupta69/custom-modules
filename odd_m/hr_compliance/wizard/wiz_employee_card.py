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

class wiz_employee_icard(osv.osv):
    _name = 'wiz.employee.icard'
    
    def _code_get(self, cr, uid, context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        ids = report_obj.search(cr, uid, [('model','=','wiz.employee.icard')])
        res = report_obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'], r['name']) for r in res]
    
    _columns = {
                'report_type':fields.selection(_code_get,'Report'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'company_id':fields.many2one('res.company','Company'),
                'department_id':fields.many2one('hr.department','Department'),
                'employee_no':fields.many2many('hr.employee','employee_icard_table_rel','emp1','emp2','Employee'),
                }
    
    def unlink(self, cr, uid, ids, context=None):
        return osv.osv.unlink(self, cr, uid, ids, context=context)
    
    def add_employee(self, cr, uid, ids, context=None):
        for each in self.browse(cr, uid, ids):
            print ""
            if each.employee_id:
                self.write(cr, uid, ids, {'employee_no':[(4,each.employee_id.id)],'employee_id':False})
            else:
                raise osv.except_osv(_('Invalid action !'), _('Please check card number. !'))
        return True
    
    def on_change_company_id(self, cr, uid, ids,company_id,department_id,context=None):
        res={}
        emp_obj = self.pool.get('hr.employee')
        if department_id:
            emp_id = emp_obj.search(cr, uid, [('department_id', '=', department_id),('active','=',True),('type','=','Employee')])
            employee = emp_obj.browse(cr, uid, emp_id)   
            if employee:
                for val in employee:
                        res['value'] = {'employee_no' : employee}
        elif company_id:
            emp_id = emp_obj.search(cr, uid, [('company_id', '=', company_id),('active','=',True),('type','=','Employee')])
            employee = emp_obj.browse(cr, uid, emp_id)   
            if employee:
                for val in employee:
                    res['value'] = {'employee_no' : employee}  
        
                     
        return res
    
    def clear_employee(self, cr, uid, ids, context=None):
        self.unlink(cr, uid, ids, context)
        return {
                'name':'ICard Report',
                'res_model':'wiz.employee.icard',
                'type':'ir.actions.act_window',
                'view_type':'form',
                'view_mode':'form',
                }
        
    def get_report_id(self, cr, uid, ids ,context=None):
        this = self.browse(cr, uid, ids[0])
        card_type = this.report_type
        if not card_type :
            raise osv.except_osv(_('Invalid action !'), _('Please Select Report Type. !!!'))
        if this.employee_no :
            for val in this.employee_no :
                self.pool.get('icard.history').create(cr, uid, {'employee_id':val.id,'card_name':card_type,'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid})
        else :
            raise osv.except_osv(_('Invalid action !'), _('Please Add Atleast One Employee. !!!'))
        
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
         
#                                        CONTRACTOR ICARD WIZARD
 
class wiz_contractor_icard(osv.osv):
    _name = 'wiz.contractor.icard'

    def _code_get(self, cr, uid, context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        ids = report_obj.search(cr, uid, [('model','=','wiz.contractor.icard')])
        res = report_obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'], r['name']) for r in res]
    
    _columns = {
                'partner_id':fields.many2one('res.partner','Contractor'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'employee_no':fields.many2many('hr.employee','employee_icard_table_rel_contractor','contractor1','contractor2','Employee'),
                'report_type':fields.selection(_code_get,'Report'),
                }

    def unlink(self, cr, uid, ids, context=None):
        return osv.osv.unlink(self, cr, uid, ids, context=context)
    
    def add_employee(self, cr, uid, ids, context=None):
        for each in self.browse(cr, uid, ids):
            print ""
            if each.employee_id:
                self.write(cr, uid, ids, {'employee_no':[(4,each.employee_id.id)],'employee_id':False})
            else:
                raise osv.except_osv(_('Invalid action !'), _('Please check card number. !'))
        return True
    
    def on_change_partner_id(self, cr, uid, ids,partner_id,context=None):
        res={}
        emp_obj = self.pool.get('hr.employee')
        if partner_id:
            emp_id = emp_obj.search(cr, uid, [('partner_id', '=', partner_id),('active','=',True),('type','=','Contractor')])
            employee = emp_obj.browse(cr, uid, emp_id)   
            if employee:
                for val in employee:
                        res['value'] = {'employee_no' : employee}
        return res
    
    def clear_employee(self, cr, uid, ids, context=None):
        self.unlink(cr, uid, ids, context)
        return {
                'name':'Contractor ICard Report',
                'res_model':'wiz.contractor.icard',
                'type':'ir.actions.act_window',
                'view_type':'form',
                'view_mode':'form',
                }
        
    def get_report_id(self, cr, uid, ids ,context=None):
        this = self.browse(cr, uid, ids[0])
        card_type = this.report_type
        if not card_type :
            raise osv.except_osv(_('Invalid action !'), _('Please Select Report Type. !!!'))
        if this.employee_no :
            for val in this.employee_no :
                self.pool.get('icard.history').create(cr, uid, {'employee_id':val.id,'card_name':card_type,'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid})
        else :
            raise osv.except_osv(_('Invalid action !'), _('Please Add Atleast One Employee. !!!'))
        
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
        