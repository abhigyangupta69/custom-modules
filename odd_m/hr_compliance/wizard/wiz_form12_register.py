import re
from openerp import addons
import logging
from itertools import groupby
from operator import itemgetter
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
import time
import math
from datetime import datetime , timedelta
_logger = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import base64, urllib
import time
import os
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import cStringIO
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, Alignment,  easyxf
from PIL import Image
import csv
from openerp.tools import amount_to_text_en
from dateutil import rrule
import calendar

class wiz_form12_register(osv.TransientModel):
    _name = 'wiz.form12.register'

    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False
                
    _columns = {
                'from_date':fields.date('From Date'),
                'till_date':fields.date('Till Date'),
                'company_id':fields.many2one('res.company','Company'),
                'department_id':fields.many2one('hr.department','Department'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'user_id':fields.many2one('res.users','User Id'),
                'month_id':fields.many2one('holiday.list', 'Month'),
                'employee_ids':fields.many2many('hr.employee','employee_form12_table_rel','emp1','emp2','Employee'),

               }
    _defaults={
                'company_id' : _get_company_id,
                'user_id': lambda obj, cr, uid, context: uid,
               }

    def onchange_month_id(self, cr, uid, ids, month_id, context=None):
        if month_id :
            month_browse = self.pool.get('holiday.list').browse(cr, uid, month_id)
            month = int(month_browse.month)
            year = int(month_browse.year_id.name)
            tup = calendar.monthrange(year,month)
            start_date = str(year) + '-' + str(month) + '-' + '01'
            end_date = str(year) + '-' + str(month) + '-' + str(tup[1])
            from_date = datetime.strptime(start_date,"%Y-%m-%d")
            from_date = from_date.strftime("%Y-%m-%d")
            till_date = datetime.strptime(end_date,"%Y-%m-%d")
            till_date = till_date.strftime("%Y-%m-%d")            
             
            return {'value': {'from_date': from_date,'till_date':till_date}}  
        
    def add_employee(self, cr, uid, ids, context=None) :
        list_ids = []
        for each in self.browse(cr, uid, ids):
            emp_obj = self.pool.get('hr.employee')
            if each.employee_id and each.department_id and each.company_id :
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj','<=',each.till_date),('type','=','Employee')])                  
            elif each.employee_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj','<=',each.till_date),('type','=','Employee')])
            elif each.department_id and each.company_id:
                list_ids = emp_obj.search(cr, uid, [('department_id', '=', each.department_id.id),('active','=',True),('company_id','=',each.company_id.id),('doj','<=',each.till_date),('type','=','Employee')])
            elif each.company_id:
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',each.company_id.id),('doj','<=',each.till_date),('type','=','Employee')])
            elif each.employee_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('doj','<=',each.till_date),('type','=','Employee')])
            elif each.department_id:
                raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
            else:
                list_ids = emp_obj.search(cr, uid, [('active','=',True),('doj','<=',each.till_date),('type','=','Employee')])
            
            if list_ids:
                for val in list_ids :
                    self.write(cr, uid, ids, {'employee_ids':[(4,val)],'employee_id':False})
            else:
                raise osv.except_osv(_('Invalid action !'), _('No Employee Found !!!'))
        return True
        
    def clear_employee(self, cr, uid, ids, context=None):
        self.unlink(cr, uid, ids, context)
        return {
                'name':'Form12 Report',
                'res_model':'wiz.form12.register',
                'type':'ir.actions.act_window',
                'view_type':'form',
                'view_mode':'form',
                }
    
    def print_report(self,cr,uid,ids,context=None):
        wiz_obj=self.pool.get('wiz.form12.register').browse(cr,uid,ids[0])
        report_obj = self.pool.get('ir.actions.report.xml')
        datas = {'ids' : ids}
        rpt_id =  report_obj.search(cr, uid, [('model','=','wiz.form12.register')])
        if not rpt_id:
            raise osv.except_osv(_('Invalid action !'), _('Report for this Record Not Exist.'))
        rpt_type = report_obj.read(cr, uid, rpt_id, ['report_name'])[0]
        
        return {
               'type' : 'ir.actions.report.xml',
               'report_name':str(rpt_type['report_name']),
               'datas' : datas,
               'nodestroy':True,
               }
    
  
  
#                                                CONTRACTOR FORM12 REGISTER
    
class wiz_contractor_form12_register(osv.TransientModel):
    _name = 'wiz.contractor.form12.register'

    _columns = {
                'from_date':fields.date('From Date'),
                'till_date':fields.date('Till Date'),
                'partner_id':fields.many2one('res.partner','Contractor'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'month_id':fields.many2one('holiday.list', 'Month'),
                'employee_ids':fields.many2many('hr.employee','contractor_form12_table_rel','cont1','cont2','Employee'),
               }

    def onchange_month_id(self, cr, uid, ids, month_id, context=None):
        if month_id :
            month_browse = self.pool.get('holiday.list').browse(cr, uid, month_id)
            month = int(month_browse.month)
            year = int(month_browse.year_id.name)
            tup = calendar.monthrange(year,month)
            start_date = str(year) + '-' + str(month) + '-' + '01'
            end_date = str(year) + '-' + str(month) + '-' + str(tup[1])
            from_date = datetime.strptime(start_date,"%Y-%m-%d")
            from_date = from_date.strftime("%Y-%m-%d")
            till_date = datetime.strptime(end_date,"%Y-%m-%d")
            till_date = till_date.strftime("%Y-%m-%d")            
             
            return {'value': {'from_date': from_date,'till_date':till_date}}  
        
    def add_employee(self, cr, uid, ids, context=None) :
        list_ids = []
        for each in self.browse(cr, uid, ids):
            emp_obj = self.pool.get('hr.employee')
            if each.partner_id:
                list_ids = emp_obj.search(cr, uid, [('partner_id','=',each.partner_id.id),('active','=',True),('doj','<=',each.till_date),('type','=','Contractor')])
            elif each.employee_id:
                list_ids = emp_obj.search(cr, uid, [('id', '=', each.employee_id.id),('active','=',True),('doj','<=',each.till_date),('type','=','Contractor')])
            
            if list_ids:
                for val in list_ids :
                    self.write(cr, uid, ids, {'employee_ids':[(4,val)],'employee_id':False})
            else:
                raise osv.except_osv(_('Invalid action !'), _('No Employee Found !!!'))
        return True
        
    def clear_employee(self, cr, uid, ids, context=None):
        self.unlink(cr, uid, ids, context)
        return {
                'name':'Contractor Form12 Register Report',
                'res_model':'wiz.contractor.form12.register',
                'type':'ir.actions.act_window',
                'view_type':'form',
                'view_mode':'form',
                }
    
    def print_report(self,cr,uid,ids,context=None):
        wiz_obj=self.pool.get('wiz.contractor.form12.register').browse(cr,uid,ids[0])
        report_obj = self.pool.get('ir.actions.report.xml')
        datas = {'ids' : ids}
        rpt_id =  report_obj.search(cr, uid, [('model','=','wiz.contractor.form12.register')])
        if not rpt_id:
            raise osv.except_osv(_('Invalid action !'), _('Report for this Record Not Exist.'))
        rpt_type = report_obj.read(cr, uid, rpt_id, ['report_name'])[0]
        
        return {
               'type' : 'ir.actions.report.xml',
               'report_name':str(rpt_type['report_name']),
               'datas' : datas,
               'nodestroy':True,
               }
