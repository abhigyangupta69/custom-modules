from openerp.osv import osv, fields
import time
from openerp.tools.translate import _

class wiz_employee_pf_form(osv.TransientModel):
    _name = 'wiz.employee.pf.form'
    
    def _code_get(self, cr, uid, context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        ids = report_obj.search(cr, uid, [('model','=','wiz.employee.pf.form')])
        res = report_obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'], r['name']) for r in res]
    
    
    _columns = {
                'report_type':fields.selection(_code_get,' Employee PF Reports',required=True),
                'month':fields.many2one('holiday.list','Month (Only For FnF )',),
                'employee_no':fields.many2many('hr.employee','employes_compliance_table_1','emp1','emp2','Employee',required=True),
                'pre_year':fields.selection([('2015-2016','2015-2016'),('2016-2017','2016-2017'),('2017-2018','2017-2018'),('2018-2019','2018-2019'),('2019-2020','2019-2020')],'Previous Year',),
                'curr_year':fields.selection([('2015-2016','2015-2016'),('2016-2017','2016-2017'),('2017-2018','2017-2018'),('2018-2019','2018-2019'),('2019-2020','2019-2020')],'Current Year',),
                }
    

    def clear_employee1(self, cr, uid, ids, context=None):
        cr.execute("delete from employes_compliance_table_1 where emp1='"+str(ids[0])+"' " )
        
        return True  
       
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
        



#                                         Contractor PF Form


class wiz_contractor_pf_form(osv.TransientModel):
    _name = 'wiz.contractor.pf.form'
    
    def _code_get(self, cr, uid, context=None):
        report_obj = self.pool.get('ir.actions.report.xml')
        ids = report_obj.search(cr, uid, [('model','=','wiz.contractor.pf.form')])
        res = report_obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'], r['name']) for r in res]
    
    
    _columns = {
                'report_type':fields.selection(_code_get,' Contractor PF Reports',required=True),
                'month':fields.many2one('holiday.list','Month (Only For FnF)',),
                'employee_no':fields.many2many('hr.employee','contractor_pf_compliance_table_1','cont1','cont2','Employee',required=True),
                'pre_year':fields.selection([('2015-2016','2015-2016'),('2016-2017','2016-2017'),('2017-2018','2017-2018'),('2018-2019','2018-2019'),('2019-2020','2019-2020')],'Previous Year',),
                'curr_year':fields.selection([('2015-2016','2015-2016'),('2016-2017','2016-2017'),('2017-2018','2017-2018'),('2018-2019','2018-2019'),('2019-2020','2019-2020')],'Current Year',),
                }
    
    def clear_employee1(self, cr, uid, ids, context=None):
        cr.execute("delete from contractor_pf_compliance_table_1 where cont1='"+str(ids[0])+"' " )
        return True  
       
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
