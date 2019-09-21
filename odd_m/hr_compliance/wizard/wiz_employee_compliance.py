from openerp.osv import osv, fields
import time

class wiz_employee_compliance(osv.TransientModel):
    _name = 'wiz.employee.compliance'
    
    def _code_get(self, cr, uid, context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        ids = report_obj.search(cr, uid, [('model','=','wiz.employee.compliance')])
        res = report_obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'], r['name']) for r in res]
    
    _columns = {
                'report_type':fields.selection(_code_get,'Report',required=True),
                'employee_no':fields.many2many('hr.employee','employes_compliance_table1','emp1','emp2','Employee',required=True),
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


#                        CONTRACTOR MASTER REPORTS

class wiz_contractor_compliance(osv.TransientModel):
    _name = 'wiz.contractor.compliance'
    
    def _code_get(self, cr, uid, context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        ids = report_obj.search(cr, uid, [('model','=','wiz.contractor.compliance')])
        res = report_obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'], r['name']) for r in res]
    
    _columns = {
                'report_type':fields.selection(_code_get,'Report',required=True),
                'employee_no':fields.many2many('hr.employee','contractor_compliance_table1','contractor1','contractor2','Employee',required=True),
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
