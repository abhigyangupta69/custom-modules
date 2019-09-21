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


class wiz_salary_deduction_category(osv.TransientModel):
    _name = 'wiz.salary.deduction.category'
    
    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False
        
    _columns = {
                'month':fields.many2one('holiday.list','Month',required=True),
                'company_id':fields.many2one('res.company','Company'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'export_data':fields.binary('File',readonly=True),
                'filename':fields.char('File Name',size=250,readonly=True),
                'user_id':fields.many2one('res.users',"User Id"),
                'employee_type':fields.selection([('Staff','Staff'),('Worker','Worker')],'Employee Type'),
                'company_ids':fields.many2many('res.company','employee_company_table_rel','emp1','emp2','Employee'),
                'employment_type':fields.selection([('Employee','Employee'),('Labor','Labor')],'Employment Type'),
                }  
    _defaults={
               'company_id' : _get_company_id,
               'user_id' : lambda obj, cr, uid, context: uid,
               } 
    
    
    def salary_deduction_category(self,cr,uid,ids,context=None):
#============ ========= =============== =========================#        
        fnt = Font()
        fnt.name = 'Ubuntu Medium'
        fnt.size=16
        fnt.style= 'Regular'
#============ ======== ============= ============================#        
        #Define the font attributes for header
        content_fnt = Font()
        content_fnt.name ='Ubuntu Medium'
        content_fnt.size=16
        content_fnt.style= 'Regular'
        align_content = Alignment()
        align_content.horz= Alignment.HORZ_CENTER
        borders = Borders()
        borders.left = 0x01
        borders.right = 0x01
        borders.top = 0x01
        borders.bottom = 0x01
#==============================================================#        
        #The text should be centrally aligned
        
        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        align.vert = Alignment.VERT_CENTER
        #We set the backgroundcolour here
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour =  0x1F
        #apply the above settings to the row(0) header
        style_header= XFStyle()
        style_header.font= fnt
        style_header.pattern= pattern
        style_header.borders = borders
        style_header.alignment=align  

    #Define the font attributes for header
        fnt1 = Font()
        fnt1.name = 'Ubuntu Medium'
        fnt1.size =10
        fnt1.style='Regular'
        
        content_fnt1 = Font()
        content_fnt1.name ='Ubuntu Medium'
        content_fnt1.style='Regular'
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_LEFT
     
        borders1 = Borders()
        borders1.left = 0x1
        borders1.right = 0x1
        borders1.top = 0x1
        borders1.bottom = 0x1
        
        #The text should be centrally aligned
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern1 = Pattern()
        pattern1.pattern1 = Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour =  0x16
        #apply the above settings to the row(0) header
        style_header1= XFStyle()
        style_header1.font= fnt1
        style_header1.pattern= pattern1
        style_header1.borders = borders1
        style_header1.alignment=align1 
        
        
    #Define the font attributes for Content
        fnt3 = Font()
        fnt3.name = 'Arial'
        fnt3.size ='10'
        fnt3.style='Regular'
        
        content_fnt3 = Font()
        content_fnt3.name ='Arial'
        content_fnt3.style='Regular'
        align_content3 = Alignment()
        align_content3.horz= Alignment.HORZ_LEFT
     
        borders3 = Borders()
        borders3.left = 0x0
        borders3.right = 0x0
        borders3.top = 0x0
        borders3.bottom = 0x0
        
        #The text should be centrally aligned
        align3 = Alignment()
        align3.horz = Alignment.HORZ_CENTER
        align3.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern3 = Pattern()

        #apply the above settings to the row(0) header
        style_header3= XFStyle()
        style_header3.font= fnt3
        style_header3.pattern= pattern3
        style_header3.borders = borders3
        style_header3.alignment=align3   
        
        
        fnt5 = Font()
        fnt5.name = 'Arial'
        fnt.size=10
        content_fnt5 = Font()
        content_fnt5.name ='Arial'
        align_content5 = Alignment()
#         align_content5.horz= Alignment.HORZ_JUSTIFIED
        borders5 = Borders()
        borders5.left = 0x02
        borders5.right = 0x02
        borders5.top = 0x02

        
        borders5.bottom = 0x02
        align5 = Alignment()
#         align5.horz = Alignment.HORZ_JUSTIFIED
        align5.vert = Alignment.VERT_JUSTIFIED
        pattern5 = Pattern()
        pattern5.pattern = Pattern.SOLID_PATTERN
        pattern5.pattern_fore_colour =  0x16
        style_header5= XFStyle()
        style_header5.font= fnt5
        style_header5.pattern= pattern5
        style_header5.borders = borders5
        style_header5.alignment=align5
        
        fnt6 = Font()
        fnt6.name = 'Arial'
        fnt6.height= 300
        fnt6.bold=True
        align_content6 = Alignment()
        align_content6.horz= Alignment.HORZ_CENTER
        borders6 = Borders()
        borders6.left = 0x02
        borders6.right = 0x02
        borders6.top = 0x02
        borders6.bottom = 0x02
        align6 = Alignment()
        align6.horz = Alignment.HORZ_CENTER
        align6.vert = Alignment.VERT_CENTER
        pattern6 = Pattern()
        pattern6.pattern6 = Pattern.SOLID_PATTERN
        pattern6.pattern6_fore_colour=0x16
        style_header6= XFStyle()
        style_header6.font= fnt6
        style_header6.pattern= pattern6
        style_header6.borders = borders6
        style_header6.alignment=align6
        wb = Workbook()
        ws = wb.add_sheet('Category Wise Deduction')
        this=self.browse(cr,uid,ids[0],context=context)
        year=this.month.year_id.id
        month=this.month.month
        emp_id = this.employee_id.id
        company_id = this.company_id.id
        employee_type=this.employee_type
        employment_type=this.employment_type
        
        ws.row(0).height = 300
        ws.row(1).height = 300
        ws.row(2).height = 300
        ws.col(1).width = 8000
        ws.col(2).width = 6000
        ws.col(3).width = 6000
        ws.col(5).width = 4000
        ws.col(6).width = 4000
        ws.col(7).width = 4000
        ws.col(8).width = 4000
        ws.col(9).width = 5000
        ws.col(10).width = 5000

        ws.write_merge(0,0,0,11, 'COMPANY :  '+ this.company_id.name + '  ' + this.company_id.street  ,style_header)
        ws.write_merge(1,1,0,11, ('SALARY CHART FOR THE MONTH OF :',this.month.name),style_header)
        ws.write_merge(2,2,4,5, 'Income',style_header1)
        ws.write_merge(2,2,6,10, 'Deductions',style_header1)
        ws.write(2,11, 'Net Amount',style_header1)
        ws.write(3,0, 'PCard',style_header)
        ws.write(3,1, 'Employee Name',style_header)
        ws.write(3,2, 'Department Name',style_header)
        ws.write(3,3, 'Designation Name',style_header)
        ws.write(3,4, 'Total Salary',style_header)
        ws.write(3,5, 'OT Amount',style_header) 
        ws.write(3,6, 'PF Deducted',style_header) 
        ws.write(3,7, 'TDS Deducted',style_header)
        ws.write(3,8, 'ESI Deducted',style_header)
        ws.write(3,9, 'Professional Tax',style_header)
        ws.write(3,10, 'ADVANCE Deducted',style_header)
        ws.write(3,11, 'Net Amount',style_header)
           
        i=4
        total_epf=0.0
        total_tds=0.0
        total_esi=0.0
        total_kharcha=0.0
        total_ot_salary=0.0
        total_a_gross=0.0
        total_grand_payment=0.0
        total_professional_tax=0.0
        list_val=[]
        list_ids=[]
       
        emp_obj = self.pool.get('hr.employee') 
        
        if this.employee_id  and this.employee_type:
            ws.write_merge(2,2,1,2, ('Employee Type : ',this.employee_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('active','=',True),('employee_type','=',employee_type),('type','=','Employee')])
        elif this.employee_id  and this.employment_type:
            ws.write_merge(2,2,1,2, ('Employment Type : ',this.employment_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('active','=',True),('employment_type','=',employment_type),('type','=','Employee')])    
        elif this.company_ids and this.employee_type:
            ws.write_merge(2,2,1,2, ('Employee Type : ',this.employee_type),style_header1)
            for val in  this.company_ids :
                list_val=emp_obj.search(cr, uid, [('active','=',True),('company_id','=',val.id),('employee_type','=',employee_type),('type','=','Employee')])
                list_ids=list_val+list_ids
        elif this.company_ids and this.employment_type:
            ws.write_merge(2,2,1,2, ('Employment Type : ',this.employment_type),style_header1)
            for val in  this.company_ids :
                list_val=emp_obj.search(cr, uid, [('active','=',True),('company_id','=',val.id),('employment_type','=',employment_type),('type','=','Employee')])
                list_ids=list_val+list_ids        
        elif not this.employee_type and not this.employment_type :
             raise osv.except_osv(('Warning !'),("Please Select Employee or Employment Type !!!"))
        elif  this.employee_type :
            ws.write_merge(2,2,1,2, ('Employee Type : ',this.employee_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('employee_type','=',employee_type),('type','=','Employee')])
        elif  this.employment_type :
            ws.write_merge(2,2,1,2, ('Employment Type : ',this.employment_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('employment_type','=',employment_type),('type','=','Employee')])    
        else:
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('type','=','Employee')])
            
        if len(list_ids) == 0 :
            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))
        if len(list_ids) == 1 :
            query ="select spl.employee_name,spl.sinid,spl.department_name,spl.job_name,spl.epf,spl.tds,spl.esi,spl.kharcha,sum(spl.overtime_amount+spl.sun_overtime_amount),sum(spl.days_amount+spl.other_salary_amount),spl.grand_total,spl.pro_tax_amt"\
                   " from salary_payment_line as spl  where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"'  group by "\
                   " spl.employee_name,spl.sinid,spl.department_name,spl.job_name,spl.epf,spl.tds,spl.esi,spl.kharcha,spl.grand_total,spl.pro_tax_amt order by spl.sinid "                           
            cr.execute(query)
            temp = cr.fetchall()
        else :
            query ="select spl.employee_name,spl.sinid,spl.department_name,spl.job_name,spl.epf,spl.tds,spl.esi,spl.kharcha,sum(spl.overtime_amount+spl.sun_overtime_amount),sum(spl.days_amount+spl.other_salary_amount),spl.grand_total,spl.pro_tax_amt"\
                   " from salary_payment_line as spl  where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"'  group by " \
                   " spl.employee_name,spl.sinid,spl.department_name,spl.job_name,spl.epf,spl.tds,spl.esi,spl.kharcha,spl.grand_total,spl.pro_tax_amt  order by spl.sinid"                          
            cr.execute(query)
            temp = cr.fetchall()
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))    
        
        for val in temp :
            total_epf+=val[4]
            total_tds+=val[5]
            total_esi+=val[6]
            total_kharcha+=val[7]
            total_ot_salary+=val[8]
            total_a_gross+=val[9]
            total_grand_payment+=val[10]
            total_professional_tax+=val[11]
            
            ws.write(i,0,(val[1]),style_header3)
            ws.write(i,1,(val[0]),style_header3)
            ws.write(i,2,(val[2]),style_header3)
            ws.write(i,3,(val[3]),style_header3)
            ws.write(i,4,(val[9]),style_header3)
            ws.write(i,5,(val[8]),style_header3)
            ws.write(i,6,(val[4]),style_header3)
            ws.write(i,7,(val[5]),style_header3)
            ws.write(i,8,(val[6]),style_header3)
            ws.write(i,9,(val[11]),style_header3)
            ws.write(i,10,(val[7]),style_header3)
            ws.write(i,11,(val[10]),style_header3)
            
            i=i+1
             
        ws.write(i,3,'TOTAL',style_header5)    
        ws.write(i,4,total_a_gross,style_header5)
        ws.write(i,5,total_ot_salary,style_header5)
        ws.write(i,6,total_epf,style_header5)
        ws.write(i,7,total_tds,style_header5)
        ws.write(i,8,total_esi,style_header5)
        ws.write(i,9,total_professional_tax,style_header5)
        ws.write(i,10,total_kharcha,style_header5)
        ws.write(i,11,total_grand_payment,style_header5)
        

        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        
        ot_report = self.write(cr, uid, ids, {'export_data':out, 'filename':'Salary CHART.xls'}, context=context)
        return ot_report
    

#                                CONTRACTOR SALARY SUMMERY REPORT



class wiz_contractor_salary_summery_report(osv.TransientModel):
    _name = 'wiz.contractor.salary.summery.report'
    
    _columns = {
                'month':fields.many2one('holiday.list','Month',required=True),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'partner_id':fields.many2one('res.partner',"Contractor"),
                'user_id':fields.many2one('res.users',"User Id"),
                'employee_type':fields.selection([('Staff','Staff'),('Worker','Worker')],'Employee Type'),
                'employment_type':fields.selection([('Employee','Employee'),('Labor','Labor')],'Employment Type'),
                'export_data':fields.binary('File',readonly=True),
                'filename':fields.char('File Name',size=250,readonly=True),
                }  
    _defaults={
               'user_id' : lambda obj, cr, uid, context: uid,
               } 
    
    
    def salary_deduction_category(self,cr,uid,ids,context=None):
#============ ========= =============== =========================#        
        fnt = Font()
        fnt.name = 'Ubuntu Medium'
        fnt.size=16
        fnt.style= 'Regular'
#============ ======== ============= ============================#        
        #Define the font attributes for header
        content_fnt = Font()
        content_fnt.name ='Ubuntu Medium'
        content_fnt.size=16
        content_fnt.style= 'Regular'
        align_content = Alignment()
        align_content.horz= Alignment.HORZ_CENTER
        borders = Borders()
        borders.left = 0x01
        borders.right = 0x01
        borders.top = 0x01
        borders.bottom = 0x01
#==============================================================#        
        #The text should be centrally aligned
        
        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        align.vert = Alignment.VERT_CENTER
        #We set the backgroundcolour here
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour =  0x1F
        #apply the above settings to the row(0) header
        style_header= XFStyle()
        style_header.font= fnt
        style_header.pattern= pattern
        style_header.borders = borders
        style_header.alignment=align  

    #Define the font attributes for header
        fnt1 = Font()
        fnt1.name = 'Ubuntu Medium'
        fnt1.size =10
        fnt1.style='Regular'
        
        content_fnt1 = Font()
        content_fnt1.name ='Ubuntu Medium'
        content_fnt1.style='Regular'
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_LEFT
     
        borders1 = Borders()
        borders1.left = 0x1
        borders1.right = 0x1
        borders1.top = 0x1
        borders1.bottom = 0x1
        
        #The text should be centrally aligned
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern1 = Pattern()
        pattern1.pattern1 = Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour =  0x16
        #apply the above settings to the row(0) header
        style_header1= XFStyle()
        style_header1.font= fnt1
        style_header1.pattern= pattern1
        style_header1.borders = borders1
        style_header1.alignment=align1 
        
        
    #Define the font attributes for Content
        fnt3 = Font()
        fnt3.name = 'Arial'
        fnt3.size ='10'
        fnt3.style='Regular'
        
        content_fnt3 = Font()
        content_fnt3.name ='Arial'
        content_fnt3.style='Regular'
        align_content3 = Alignment()
        align_content3.horz= Alignment.HORZ_LEFT
     
        borders3 = Borders()
        borders3.left = 0x0
        borders3.right = 0x0
        borders3.top = 0x0
        borders3.bottom = 0x0
        
        #The text should be centrally aligned
        align3 = Alignment()
        align3.horz = Alignment.HORZ_CENTER
        align3.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern3 = Pattern()

        #apply the above settings to the row(0) header
        style_header3= XFStyle()
        style_header3.font= fnt3
        style_header3.pattern= pattern3
        style_header3.borders = borders3
        style_header3.alignment=align3   
        
        
        fnt5 = Font()
        fnt5.name = 'Arial'
        fnt.size=10
        content_fnt5 = Font()
        content_fnt5.name ='Arial'
        align_content5 = Alignment()
#         align_content5.horz= Alignment.HORZ_JUSTIFIED
        borders5 = Borders()
        borders5.left = 0x02
        borders5.right = 0x02
        borders5.top = 0x02

        
        borders5.bottom = 0x02
        align5 = Alignment()
#         align5.horz = Alignment.HORZ_JUSTIFIED
        align5.vert = Alignment.VERT_JUSTIFIED
        pattern5 = Pattern()
        pattern5.pattern = Pattern.SOLID_PATTERN
        pattern5.pattern_fore_colour =  0x16
        style_header5= XFStyle()
        style_header5.font= fnt5
        style_header5.pattern= pattern5
        style_header5.borders = borders5
        style_header5.alignment=align5
        
        fnt6 = Font()
        fnt6.name = 'Arial'
        fnt6.height= 300
        fnt6.bold=True
        align_content6 = Alignment()
        align_content6.horz= Alignment.HORZ_CENTER
        borders6 = Borders()
        borders6.left = 0x02
        borders6.right = 0x02
        borders6.top = 0x02
        borders6.bottom = 0x02
        align6 = Alignment()
        align6.horz = Alignment.HORZ_CENTER
        align6.vert = Alignment.VERT_CENTER
        pattern6 = Pattern()
        pattern6.pattern6 = Pattern.SOLID_PATTERN
        pattern6.pattern6_fore_colour=0x16
        style_header6= XFStyle()
        style_header6.font= fnt6
        style_header6.pattern= pattern6
        style_header6.borders = borders6
        style_header6.alignment=align6
        wb = Workbook()
        ws = wb.add_sheet('Contractor Salary Summery')
        this=self.browse(cr,uid,ids[0],context=context)
        
        ws.row(0).height = 300
        ws.row(1).height = 300
        ws.row(2).height = 300
        ws.col(1).width = 8000
        ws.col(2).width = 6000
        ws.col(3).width = 6000
        ws.col(5).width = 4000
        ws.col(6).width = 4000
        ws.col(7).width = 4000
        ws.col(8).width = 4000
        ws.col(9).width = 5000
        ws.col(10).width = 5000

        ws.write_merge(0,0,0,11, 'CONTRACTOR :  '+ this.partner_id.name + '  ' + this.partner_id.street  ,style_header)
        ws.write_merge(1,1,0,11, ('SALARY CHART FOR THE MONTH OF :',this.month.name),style_header)
        ws.write_merge(2,2,4,5, 'Income',style_header1)
        ws.write_merge(2,2,6,10, 'Deductions',style_header1)
        ws.write(2,11, 'Net Amount',style_header1)
        
        ws.write(3,0, 'PCard',style_header)
        ws.write(3,1, 'Employee Name',style_header)
        ws.write(3,2, 'Department Name',style_header)
        ws.write(3,3, 'Designation Name',style_header)
        ws.write(3,4, 'Total Salary',style_header)
        ws.write(3,5, 'OT Amount',style_header) 
        ws.write(3,6, 'PF Deducted',style_header) 
        ws.write(3,7, 'TDS Deducted',style_header)
        ws.write(3,8, 'ESI Deducted',style_header)
        ws.write(3,9, 'Professional Tax',style_header)
        ws.write(3,10, 'ADVANCE Deducted',style_header)
        ws.write(3,11, 'Net Amount',style_header)
           
        i=4
        total_epf=0.0
        total_tds=0.0
        total_esi=0.0
        total_kharcha=0.0
        total_ot_salary=0.0
        total_a_gross=0.0
        total_grand_payment=0.0
        total_professional_tax=0.0
        list_val=[]
        list_ids=[]
       
        emp_obj = self.pool.get('hr.employee') 
        
        if this.partner_id and this.employee_id  and this.employee_type:
            ws.write_merge(2,2,1,2, ('Employee Type : ',this.employee_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', this.partner_id.id),('id', '=', this.employee_id.id),('employee_type','=',employee_type),('active','=',True),('type','=','Contractor')])
        elif this.partner_id and this.employee_id  and this.employment_type:
            ws.write_merge(2,2,1,2, ('Employment Type : ',this.employment_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', this.partner_id.id),('id', '=', this.employee_id.id),('employment_type','=',employment_type),('active','=',True),('type','=','Contractor')])    
        elif this.partner_id and this.employee_id:
            ws.write_merge(2,2,1,2, ('Employee Type : ',this.employee_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', this.partner_id.id),('id', '=', this.employee_id.id),('active','=',True),('type','=','Contractor')])
        elif this.partner_id and this.employee_type:
            ws.write_merge(2,2,1,2, ('Employee Type : ',this.employee_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', this.partner_id.id),('employee_type','=',employee_type),('active','=',True),('type','=','Contractor')])
        elif this.partner_id and this.employment_type:
            ws.write_merge(2,2,1,2, ('Employment Type : ',this.employment_type),style_header1)
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', this.partner_id.id),('employment_type','=',employment_type),('active','=',True),('type','=','Contractor')])    
        elif  this.partner_id :
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', this.partner_id.id),('active','=',True),('type','=','Contractor')])
        else:
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('type','=','Contractor')])
            
        if len(list_ids) == 0 :
            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))
        if len(list_ids) == 1 :
            query ="select spl.employee_name,spl.sinid,spl.department_name,spl.job_name,spl.epf,spl.tds,spl.esi,spl.kharcha,sum(spl.overtime_amount+spl.sun_overtime_amount),sum(spl.days_amount+spl.other_salary_amount),spl.grand_total,spl.pro_tax_amt"\
                   " from salary_payment_line as spl  where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"'  group by "\
                   " spl.employee_name,spl.sinid,spl.department_name,spl.job_name,spl.epf,spl.tds,spl.esi,spl.kharcha,spl.grand_total,spl.pro_tax_amt order by spl.sinid "                           
            cr.execute(query)
            temp = cr.fetchall()
        else :
            query ="select spl.employee_name,spl.sinid,spl.department_name,spl.job_name,spl.epf,spl.tds,spl.esi,spl.kharcha,sum(spl.overtime_amount+spl.sun_overtime_amount),sum(spl.days_amount+spl.other_salary_amount),spl.grand_total,spl.pro_tax_amt"\
                   " from salary_payment_line as spl  where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"'  group by " \
                   " spl.employee_name,spl.sinid,spl.department_name,spl.job_name,spl.epf,spl.tds,spl.esi,spl.kharcha,spl.grand_total,spl.pro_tax_amt  order by spl.sinid"                          
            cr.execute(query)
            temp = cr.fetchall()
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))    
        
        for val in temp :
            total_epf+=val[4]
            total_tds+=val[5]
            total_esi+=val[6]
            total_kharcha+=val[7]
            total_ot_salary+=val[8]
            total_a_gross+=val[9]
            total_grand_payment+=val[10]
            total_professional_tax+=val[11]
            
            ws.write(i,0,(val[1]),style_header3)
            ws.write(i,1,(val[0]),style_header3)
            ws.write(i,2,(val[2]),style_header3)
            ws.write(i,3,(val[3]),style_header3)
            ws.write(i,4,(val[9]),style_header3)
            ws.write(i,5,(val[8]),style_header3)
            ws.write(i,6,(val[4]),style_header3)
            ws.write(i,7,(val[5]),style_header3)
            ws.write(i,8,(val[6]),style_header3)
            ws.write(i,9,(val[11]),style_header3)
            ws.write(i,10,(val[7]),style_header3)
            ws.write(i,11,(val[10]),style_header3)
            
            i=i+1
             
        ws.write(i,3,'TOTAL',style_header5)    
        ws.write(i,4,total_a_gross,style_header5)
        ws.write(i,5,total_ot_salary,style_header5)
        ws.write(i,6,total_epf,style_header5)
        ws.write(i,7,total_tds,style_header5)
        ws.write(i,8,total_esi,style_header5)
        ws.write(i,9,total_professional_tax,style_header5)
        ws.write(i,10,total_kharcha,style_header5)
        ws.write(i,11,total_grand_payment,style_header5)
        

        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        
        ot_report = self.write(cr, uid, ids, {'export_data':out, 'filename':'Contractor Salary CHART.xls'}, context=context)
        return ot_report
