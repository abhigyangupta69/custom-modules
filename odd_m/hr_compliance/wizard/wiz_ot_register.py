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


class wiz_ot_register(osv.TransientModel):
    _name = 'wiz.ot.register'
    
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
                }
    
    _defaults={
               'company_id' : _get_company_id,
               'user_id' : lambda obj, cr, uid, context: uid,
               } 
    
    
    def ot_register_report(self,cr,uid,ids,context=None):
        fnt = Font()
        fnt.name = 'Ubuntu Medium'
        fnt.size=16
        fnt.style= 'Regular'
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
        pattern1.pattern1_fore_colour =  0x1F
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
        
        wb = Workbook()
        ws = wb.add_sheet('OT Register Report')
        
        this=self.browse(cr,uid,ids[0],context=context)
        year=this.month.year_id.id
        month=this.month.month
        emp_id = this.employee_id.id
        company_id = this.company_id.id
        
        ws.row(0).height=300
        ws.row(1).height=300
        ws.row(2).height=300
        ws.col(20).width = 6000

        ws.write_merge(0,0,4,10, 'COMPANY :  '+ this.company_id.name + '  ' + this.company_id.street  ,style_header)
        ws.write_merge(1,1,4,10, ('SALARY REPORT FOR THE MONTH OF : ',this.month.name),style_header)
        
        ws.write(2,0,'PCard',style_header)
        ws.col(0).width = 4000
        ws.write(2,1,'Employee Name',style_header)
        ws.col(1).width = 8000
        ws.write(2,2,'Department Name',style_header)
        ws.col(2).width = 5000
        ws.write(2,3,'Designation Name',style_header)
        ws.col(3).width = 5000
        ws.write(2,4,'Total Working Day',style_header)
        ws.col(4).width = 5000
        ws.write(2,5,'CL + EL',style_header)
        ws.col(5).width = 3000
        ws.write(2,6,'Compensatory Leave',style_header)
        ws.col(6).width = 5000
        ws.write(2,7,'Sick Leave',style_header)
        ws.col(7).width = 4000
        ws.write(2,8,'Absent',style_header)
        ws.col(8).width = 4000
        ws.write(2,9,'Shift Hours Worked',style_header)
        ws.col(9).width = 5000
        ws.write(2,10,'Overtime Hours',style_header)
        ws.col(10).width = 5000
        ws.write(2,11,'Total Working Hours',style_header)
        ws.col(11).width = 5000
        ws.write(2,12,'Avg Weekly Working Hour',style_header)
        ws.col(12).width = 6000
        ws.write(2,13,'Avg Daily Working Hour',style_header)
        ws.col(13).width = 6000
        ws.write(2,14,'Total Monthly Gross',style_header)
        ws.col(14).width = 5000
        ws.write(2,15,'Gross Salary Paid',style_header)
        ws.col(15).width = 5000
        ws.write(2,16,'OT Salary',style_header)
        ws.col(16).width = 5000
        ws.write(2,17,'Total Gross Salary',style_header)
        ws.col(17).width = 5000
           
        i=3
        total_days=0.0
        total_cl_el=0.0
        total_compensatory=0.0
        total_sick=0.0
        total_absent=0.0
        total_shift_hours=0.0
        total_ot_hours=0.0
        total_working_hours=0.0
        total_weekly_working_hour=0.0
        total_daily_working_hour=0.0
        total_monthly_gross=0.0
        total_gross_salary_paid=0.0
        total_ot_salary=0.0
        total_gross_salary=0.0
        emp_obj = self.pool.get('hr.employee')
         
        if this.employee_id and this.company_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('company_id','=',company_id),('type','=','Employee'),('active','=',True)])
        elif this.company_id:
            list_ids = emp_obj.search(cr, uid, [('company_id','=',company_id),('type','=','Employee'),('active','=',True)])
            list_ids1 = emp_obj.search(cr, uid, [('company_id','=',company_id),('type','=','Employee'),('active','=',False)])
            list_ids = list_ids + list_ids1
        elif this.employee_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('type','=','Employee'),('active','=',True)])

        if len(list_ids) == 1 :
            query ="select spl.sinid,spl.employee_name,spl.department_name,spl.job_name,(spl.work_day+spl.factory_work),(spl.casual_leave+spl.earned_leave),spl.compensatory_leave,spl.sick_leave,(spl.month_days-(spl.work_day+spl.factory_work+spl.casual_leave+spl.earned_leave+spl.compensatory_leave+spl.sick_leave+spl.holiday_leave+spl.week_leave)),"\
                    "((spl.work_day+spl.factory_work) * 8),(spl.over_time + spl.sun_over_time),(((spl.work_day+spl.factory_work) * 8)+(spl.over_time + spl.sun_over_time)),"\
                    "spl.month_days,"\
                    "round(((((spl.work_day+spl.factory_work) * 8)+(spl.over_time + spl.sun_over_time))/(spl.work_day+spl.factory_work)),2) ,(spl.basic + spl.other_salary),(spl.days_amount+spl.other_salary_amount),spl.total_overtime_amount,"\
                    "(spl.days_amount+spl.other_salary_amount+spl.total_overtime_amount) from salary_payment_line as spl  where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' order by spl.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
        else:
            query ="select spl.sinid,spl.employee_name,spl.department_name,spl.job_name,(spl.work_day+spl.factory_work),(spl.casual_leave+spl.earned_leave),spl.compensatory_leave,spl.sick_leave,(spl.month_days-(spl.work_day+spl.factory_work+spl.casual_leave+spl.earned_leave+spl.compensatory_leave+spl.sick_leave+spl.holiday_leave+spl.week_leave)),"\
                    "((spl.work_day+spl.factory_work) * 8),(spl.over_time + spl.sun_over_time),(((spl.work_day+spl.factory_work) * 8)+(spl.over_time + spl.sun_over_time)),"\
                    "spl.month_days,"\
                    "round(((((spl.work_day+spl.factory_work) * 8)+(spl.over_time + spl.sun_over_time))/(spl.work_day+spl.factory_work)),2) ,(spl.basic + spl.other_salary),(spl.days_amount+spl.other_salary_amount),spl.total_overtime_amount,"\
                    "(spl.days_amount+spl.other_salary_amount+spl.total_overtime_amount) from salary_payment_line as spl  where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' order by spl.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
                
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))    
        
        for val in temp :
            if val[4] >= 7:
                working_hour = round((val[11]/(val[12]-val[8]))*7,2)
            else:
                working_hour = 0.00
            
            
            total_days+= val[4]
            total_cl_el+=val[5]
            total_compensatory+=val[6]
            total_sick+=val[7]
            total_absent+=val[8]
            total_shift_hours+=val[9]
            total_ot_hours+=val[10]
            total_working_hours+=val[11]
            total_daily_working_hour+=val[13]
            total_monthly_gross+=val[14]
            total_gross_salary_paid+=val[15]
            total_ot_salary+=val[16]
            total_gross_salary+=val[17]
            total_weekly_working_hour+= working_hour
            
            ws.write(i,0,val[0],style_header3)
            ws.write(i,1,val[1],style_header3)
            ws.write(i,2,val[2],style_header3)
            ws.write(i,3,val[3],style_header3)
            ws.write(i,4,val[4],style_header3)
            ws.write(i,5,val[5],style_header3)
            ws.write(i,6,val[6],style_header3)
            ws.write(i,7,val[7],style_header3)
            ws.write(i,8,val[8],style_header3)
            ws.write(i,9,val[9],style_header3)
            ws.write(i,10,val[10],style_header3)
            ws.write(i,11,val[11],style_header3)
            ws.write(i,12,working_hour,style_header3)
            ws.write(i,13,val[13],style_header3)
            ws.write(i,14,val[14],style_header3)
            ws.write(i,15,val[15],style_header3)
            ws.write(i,16,val[16],style_header3)
            ws.write(i,17,val[17],style_header3)
            i=i+1
            
        ws.write(i,0,'',style_header3)
        ws.write(i,1,'',style_header3)
        ws.write(i,2,'',style_header3)
        ws.write(i,3,'TOTAL',style_header1)
        ws.write(i,4,total_days,style_header1)
        ws.write(i,5,total_cl_el,style_header1)
        ws.write(i,6,total_compensatory,style_header1)
        ws.write(i,7,total_sick,style_header1)
        ws.write(i,8,total_absent,style_header1)
        ws.write(i,9,total_shift_hours,style_header1)
        ws.write(i,10,total_ot_hours,style_header1)
        ws.write(i,11,total_working_hours,style_header1)
        ws.write(i,12,total_weekly_working_hour,style_header1)
        ws.write(i,13,total_daily_working_hour,style_header1)
        ws.write(i,14,total_monthly_gross,style_header1)
        ws.write(i,15,total_gross_salary_paid,style_header1)
        ws.write(i,16,total_ot_salary,style_header1)
        ws.write(i,17,total_gross_salary,style_header1)
        
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
               
        ot_report = self.write(cr, uid, ids, {'export_data':out, 'filename':'OT Register Report.xls'}, context=context)
        return ot_report
    


#                                        Contractor Ot Register


class wiz_contractor_ot_register(osv.TransientModel):
    _name = 'wiz.contractor.ot.register'
    
    _columns = {
                'month':fields.many2one('holiday.list','Month',required=True),
                'partner_id':fields.many2one('res.partner','Contractor'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'export_data':fields.binary('File',readonly=True),
                'filename':fields.char('File Name',size=250,readonly=True),
                'user_id':fields.many2one('res.users',"User Id"),
                'company_id':fields.many2one('res.company','Company'),
                }
    
    _defaults={
               'user_id' : lambda obj, cr, uid, context: uid,
               } 
    
    def ot_register_report(self,cr,uid,ids,context=None):
        fnt = Font()
        fnt.name = 'Ubuntu Medium'
        fnt.size=16
        fnt.style= 'Regular'
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
        pattern1.pattern1_fore_colour =  0x1F
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
        
        wb = Workbook()
        ws = wb.add_sheet('Contractor OT Register Report')
        
        this=self.browse(cr,uid,ids[0],context=context)
        year=this.month.year_id.id
        month=this.month.month
        emp_id = this.employee_id.id
        partner_id = this.partner_id.id
        company_id = this.company_id.id
        
        ws.row(0).height=300
        ws.row(1).height=300
        ws.row(2).height=300
        ws.col(20).width = 6000
        
        if partner_id and emp_id:
            company = 'CONTRACTOR :'
        elif company_id and emp_id:
            company = 'COMPANY :'
        elif emp_id:
            company = 'CONTRACTOR :'
        elif partner_id:
            company = 'CONTRACTOR :'
        elif company_id:
            company = 'COMPANY :'

        if partner_id and emp_id:
            name = this.partner_id.name
        elif company_id and emp_id:
            name = this.company_id.name
        elif emp_id:
            name = this.employee_id.partner_id.name
        elif partner_id:
            name = this.partner_id.name
        elif company_id:
            name = this.company_id.name
            
        if partner_id and emp_id:
            street = this.partner_id.street
        elif company_id and emp_id:
            street = this.company_id.street
        elif emp_id:
            street = this.employee_id.partner_id.street
        elif partner_id:
            street = this.partner_id.street
        elif company_id:
            street = this.company_id.street
        
        ws.write_merge(0,0,4,10, company + ' ' +  name + '  ' + street  ,style_header)
        ws.write_merge(1,1,4,10, ('SALARY REPORT FOR THE MONTH OF : ',this.month.name),style_header)
        
        ws.write(2,0,'PCard',style_header)
        ws.col(0).width = 4000
        ws.write(2,1,'Employee Name',style_header)
        ws.col(1).width = 8000
        ws.write(2,2,'Department Name',style_header)
        ws.col(2).width = 5000
        ws.write(2,3,'Designation Name',style_header)
        ws.col(3).width = 5000
        ws.write(2,4,'Total Working Day',style_header)
        ws.col(4).width = 5000
        ws.write(2,5,'CL + EL',style_header)
        ws.col(5).width = 3000
        ws.write(2,6,'Compensatory Leave',style_header)
        ws.col(6).width = 5000
        ws.write(2,7,'Sick Leave',style_header)
        ws.col(7).width = 4000
        ws.write(2,8,'Absent',style_header)
        ws.col(8).width = 4000
        ws.write(2,9,'Shift Hours Worked',style_header)
        ws.col(9).width = 5000
        ws.write(2,10,'Overtime Hours',style_header)
        ws.col(10).width = 5000
        ws.write(2,11,'Total Working Hours',style_header)
        ws.col(11).width = 5000
        ws.write(2,12,'Avg Weekly Working Hour',style_header)
        ws.col(12).width = 6000
        ws.write(2,13,'Avg Daily Working Hour',style_header)
        ws.col(13).width = 6000
        ws.write(2,14,'Total Monthly Gross',style_header)
        ws.col(14).width = 5000
        ws.write(2,15,'Gross Salary Paid',style_header)
        ws.col(15).width = 5000
        ws.write(2,16,'OT Salary',style_header)
        ws.col(16).width = 5000
        ws.write(2,17,'Total Gross Salary',style_header)
        ws.col(17).width = 5000
           
        i=3
        total_days=0.0
        total_cl_el=0.0
        total_compensatory=0.0
        total_sick=0.0
        total_absent=0.0
        total_shift_hours=0.0
        total_ot_hours=0.0
        total_working_hours=0.0
        total_weekly_working_hour=0.0
        total_daily_working_hour=0.0
        total_monthly_gross=0.0
        total_gross_salary_paid=0.0
        total_ot_salary=0.0
        total_gross_salary=0.0
        emp_obj = self.pool.get('hr.employee')
         
        if this.employee_id and this.partner_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('partner_id','=',partner_id),('type','=','Contractor'),('active','=',True)])
        elif this.employee_id and this.company_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('company_id','=',company_id),('type','=','Contractor'),('active','=',True)])
        elif this.partner_id:
            list_ids = emp_obj.search(cr, uid, [('partner_id','=',partner_id),('type','=','Contractor'),('active','=',True)])
            list_ids1 = emp_obj.search(cr, uid, [('partner_id','=',partner_id),('type','=','Contractor'),('active','=',False)])
            list_ids = list_ids + list_ids1
        elif this.company_id:
            list_ids = emp_obj.search(cr, uid, [('company_id','=',company_id),('type','=','Contractor'),('active','=',True)])
            list_ids1 = emp_obj.search(cr, uid, [('company_id','=',company_id),('type','=','Contractor'),('active','=',False)])
            list_ids = list_ids + list_ids1
        elif this.employee_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('type','=','Contractor'),('active','=',True)])

        if len(list_ids) == 1 :
            query ="select spl.sinid,spl.employee_name,spl.department_name,spl.job_name,(spl.work_day+spl.factory_work),(spl.casual_leave+spl.earned_leave),spl.compensatory_leave,spl.sick_leave,(spl.month_days-(spl.work_day+spl.factory_work+spl.casual_leave+spl.earned_leave+spl.compensatory_leave+spl.sick_leave+spl.holiday_leave+spl.week_leave)),"\
                    "((spl.work_day+spl.factory_work) * 8),(spl.over_time + spl.sun_over_time),(((spl.work_day+spl.factory_work) * 8)+(spl.over_time + spl.sun_over_time)),spl.month_days,"\
                    "round(((((spl.work_day+spl.factory_work) * 8)+(spl.over_time + spl.sun_over_time))/(spl.work_day+spl.factory_work)),2) ,(spl.basic + spl.other_salary),(spl.days_amount+spl.other_salary_amount),spl.total_overtime_amount,"\
                    "(spl.days_amount+spl.other_salary_amount+spl.total_overtime_amount) from salary_payment_line as spl  where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' order by spl.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
        else:
            query ="select spl.sinid,spl.employee_name,spl.department_name,spl.job_name,(spl.work_day+spl.factory_work),(spl.casual_leave+spl.earned_leave),spl.compensatory_leave,spl.sick_leave,(spl.month_days-(spl.work_day+spl.factory_work+spl.casual_leave+spl.earned_leave+spl.compensatory_leave+spl.sick_leave+spl.holiday_leave+spl.week_leave)),"\
                    "((spl.work_day+spl.factory_work) * 8),(spl.over_time + spl.sun_over_time),(((spl.work_day+spl.factory_work) * 8)+(spl.over_time + spl.sun_over_time)),spl.month_days,"\
                    "round(((((spl.work_day+spl.factory_work) * 8)+(spl.over_time + spl.sun_over_time))/(spl.work_day+spl.factory_work)),2) ,(spl.basic + spl.other_salary),(spl.days_amount+spl.other_salary_amount),spl.total_overtime_amount,"\
                    "(spl.days_amount+spl.other_salary_amount+spl.total_overtime_amount) from salary_payment_line as spl  where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' order by spl.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
                
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))    
        
        for val in temp :
            if val[4] >= 7:
                working_hour = round((val[11]/(val[12]-val[8]))*7,2)
            else:
                working_hour = 0.00
            
            
            
            
            total_days+= val[4]
            total_cl_el+=val[5]
            total_compensatory+=val[6]
            total_sick+=val[7]
            total_absent+=val[8]
            total_shift_hours+=val[9]
            total_ot_hours+=val[10]
            total_working_hours+=val[11]
            total_weekly_working_hour+=working_hour
            total_daily_working_hour+=val[13]
            total_monthly_gross+=val[14]
            total_gross_salary_paid+=val[15]
            total_ot_salary+=val[16]
            total_gross_salary+=val[17]
            
            ws.write(i,0,val[0],style_header3)
            ws.write(i,1,val[1],style_header3)
            ws.write(i,2,val[2],style_header3)
            ws.write(i,3,val[3],style_header3)
            ws.write(i,4,val[4],style_header3)
            ws.write(i,5,val[5],style_header3)
            ws.write(i,6,val[6],style_header3)
            ws.write(i,7,val[7],style_header3)
            ws.write(i,8,val[8],style_header3)
            ws.write(i,9,val[9],style_header3)
            ws.write(i,10,val[10],style_header3)
            ws.write(i,11,val[11],style_header3)
            ws.write(i,12,working_hour,style_header3)
            ws.write(i,13,val[13],style_header3)
            ws.write(i,14,val[14],style_header3)
            ws.write(i,15,val[15],style_header3)
            ws.write(i,16,val[16],style_header3)
            ws.write(i,17,val[17],style_header3)
            i=i+1
            
        ws.write(i,0,'',style_header3)
        ws.write(i,1,'',style_header3)
        ws.write(i,2,'',style_header3)
        ws.write(i,3,'TOTAL',style_header1)
        ws.write(i,4,total_days,style_header1)
        ws.write(i,5,total_cl_el,style_header1)
        ws.write(i,6,total_compensatory,style_header1)
        ws.write(i,7,total_sick,style_header1)
        ws.write(i,8,total_absent,style_header1)
        ws.write(i,9,total_shift_hours,style_header1)
        ws.write(i,10,total_ot_hours,style_header1)
        ws.write(i,11,total_working_hours,style_header1)
        ws.write(i,12,total_weekly_working_hour,style_header1)
        ws.write(i,13,total_daily_working_hour,style_header1)
        ws.write(i,14,total_monthly_gross,style_header1)
        ws.write(i,15,total_gross_salary_paid,style_header1)
        ws.write(i,16,total_ot_salary,style_header1)
        ws.write(i,17,total_gross_salary,style_header1)
        
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
               
        ot_report = self.write(cr, uid, ids, {'export_data':out, 'filename':'Contractor OT Register.xls'}, context=context)
        return ot_report
    
