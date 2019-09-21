from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
from datetime import datetime , timedelta
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT,float_compare
import base64,urllib
import time
import os
import re
import cStringIO
import xlwt
import math
import csv
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, Alignment,  easyxf
from dateutil import rrule
import calendar
import urllib2
import urllib



class wiz_employee_pf_upload_report(osv.TransientModel):
    _name = 'wiz.employee.pf.upload.report'
    _columns = {
                    'month':fields.many2one('holiday.list','Month',required=True),
                    'company_id':fields.many2one('res.company','Company'),
                    'export_data':fields.binary('File',readonly=True),
                    'filename':fields.char('File Name',size=250,readonly=True),
                }
    
    

    def pf_upload_report(self,cr,uid,ids,context=None):
#         req = urllib2.Request('http://www.voidspace.org.uk')
#         response = urllib2.urlopen(req)
#         the_page = response.read()
#         print " html===========================",the_page
        f_name =''
        d_name = ''
        wb = Workbook()
        ws = wb.add_sheet('PF UPLOAD')
        fnt1 = Font()
        fnt1.name = 'Arial'
        fnt1.height= 300
        fnt1.bold=True
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_CENTER
        borders1 = Borders()
        borders1.left = 0x02
        borders1.right = 0x02
        borders1.top = 0x02
        borders1.bottom = 0x02
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_CENTER
        pattern1 = Pattern()
        pattern1.pattern1 = Pattern.SOLID_PATTERN
        pattern1.pattern1_fore_colour=0x17
        style_header1= XFStyle()
        style_header1.font= fnt1
        style_header1.pattern= pattern1
        style_header1.borders = borders1
        style_header1.alignment=align1
        
        fnt2 = Font()
        fnt2.name = 'Arial'
        fnt2.height= 250
        fnt2.bold=False
        align_content2 = Alignment()
        align_content2.horz= Alignment.HORZ_CENTER
        borders2 = Borders()
        borders2.left = 0x02
        borders2.right = 0x02
        borders2.top = 0x02
        borders2.bottom = 0x02
        align2 = Alignment()
        align2.horz = Alignment.HORZ_CENTER
        align2.vert = Alignment.VERT_CENTER
        pattern2 = Pattern()
        pattern2.pattern2 = Pattern.SOLID_PATTERN
        pattern2.pattern2_fore_colour=0x09
        style_header2= XFStyle()
        style_header2.font= fnt2
        style_header2.pattern= pattern2
        style_header2.borders = borders2
        style_header2.alignment=align2

        fnt3 = Font()
        fnt3.name = 'Arial'
        fnt3.height= 275
        fnt3.bold=False
        align_content3 = Alignment()
        align_content3.horz= Alignment.HORZ_CENTER
        borders3 = Borders()
        borders3.left = 0x02
        borders3.right = 0x02
        borders3.top = 0x02
        borders3.bottom = 0x02
        align3 = Alignment()
        align3.horz = Alignment.HORZ_CENTER
        align3.vert = Alignment.VERT_CENTER
        pattern3 = Pattern()
        pattern3.pattern3 = Pattern.SOLID_PATTERN
        pattern3.pattern3_fore_colour =  0x09
        style_header3= XFStyle()
        style_header3.font= fnt3
        style_header3.pattern= pattern3
        style_header3.borders = borders3
        style_header3.alignment=align3
        
        fnt = Font()
        fnt.name = 'Arial' 
        fnt.height= 275
        content_fnt = Font()
        content_fnt.name ='Arial'
        content_fnt.height =150
        align_content = Alignment()
        align_content.horz= Alignment.HORZ_CENTER
        borders = Borders()
        borders.left = 0x02
        borders.right = 0x02
        borders.top = 0x02
        borders.bottom = 0x02
        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        align.vert = Alignment.VERT_CENTER
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour =  0x16
        style_header= XFStyle()
        style_header.font= fnt
        style_header.pattern= pattern
        style_header.borders = borders
        style_header.alignment=align

        fnt5 = Font()
        fnt5.name = 'Arial'
        fnt5.height= 275
        content_fnt5 = Font()
        content_fnt5.name ='Arial'
        content_fnt5.height =150
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

       
      
        ws.row(0).height=1500
        ws.col(0).width = 6500
        ws.col(1).width = 5000 
        ws.col(2).width = 10000 
        ws.col(3).width = 4000 
        ws.col(4).width = 4000 
        ws.col(5).width = 4500 
        ws.col(6).width = 4000   
        ws.col(7).width = 5500
        ws.col(8).width = 4000 
        ws.col(9).width = 4500 
        ws.col(10).width = 4000   
        ws.col(11).width = 4000 
#        ws.col(12).width = 6500
#        ws.col(13).width = 6500 
#        ws.col(14).width = 6500   
#        ws.col(15).width = 6500
#        ws.col(16).width = 4500
#        ws.col(17).width = 7500 
#        ws.col(18).width = 3000   
#        ws.col(19).width = 4000
#        ws.col(20).width = 3000 
#        ws.col(21).width = 6500
#        ws.col(22).width = 6500 
#        ws.col(23).width = 7500
#        ws.col(24).width = 7500
#        ws.col(25).width = 2500
#        ws.col(26).width = 5000
#        ws.col(27).width = 4000 
        
        ws.write(0,0,'Employee Pay Code',style_header)
        ws.write(0,1,'UAN Number',style_header)
        ws.write(0,2,'Member Name',style_header)
        ws.write(0,3,'Gross Wages',style_header)
        ws.write(0,4,'EPF Wages',style_header)
        ws.write(0,5,'EPS Wages',style_header)
        ws.write(0,6,'EDLI Wages',style_header)        
        ws.write(0,7,'EE Share',style_header)
        ws.write(0,8,'EPS Contribution',style_header)
        ws.write(0,9,'ER Share',style_header)
        ws.write(0,10,'NCP Days',style_header)
        ws.write(0,11,'Refund',style_header)
        
#        ws.write(0,1,'Member ID',style_header)
#        ws.write(0,6,'EPF Contribution (EE Share) being remitted',style_header5)   
#        ws.write(0,8,'EPS Contribution being remitted',style_header5)     
#        ws.write(0,10,'Diff EPF and EPS Contribution (ER Share) being remitted',style_header5)
#        ws.write(0,15,'Arrear EPF Wages',style_header)
#        ws.write(0,16,'Arrear EPF EE Share',style_header)
#        ws.write(0,17,'Arrear EPF ER Share',style_header)
#        ws.write(0,18,'Arrear EPS',style_header)
#        ws.write(0,19,'Father / Husband Name',style_header)
#        ws.write(0,20,'Relationship with the Member',style_header5)
#        ws.write(0,21,'Date of Birth',style_header)
#        ws.write(0,22,'Gender',style_header)
#        ws.write(0,23,'Date of Joining EPF',style_header)
#        ws.write(0,24,'Date of Joining EPS',style_header)
#        ws.write(0,25,'Date of Exit From EPF',style_header)
#        ws.write(0,26,'Date of Exit From EPS',style_header)
#        ws.write(0,27,'Reason for Leaving',style_header5)
        
        this=self.browse(cr,uid,ids[0],context=context)
        month=this.month.month
        company_id = this.company_id.id
        year=this.month.year_id.id
        year_name=this.month.year_id.name
        emp_obj = self.pool.get('hr.employee') 
#        pf_no=' '
        emp_name=' '
        epf_cont=0
        eps_cont=0
        calc_eps_epf=0
        diff_eps_epf=0
        full_date_month=[]
        total_epf_wages=0
        total_epf_cont=0
        total_eps_cont=0
        total_diff_calc=0
        total_diff_diff=0
        total_gross=0
        holiday_list=[]
        inact_list=[]
        inact_list1=[]
        hr_list=[]
        i=1
        val_zero=0
#        epf_date_start=''
        
        if len(str(month))==1:
            start_date = str(year_name) + '-' +'0'+ str(month) + '-' + '01'
            month_val='0'+str(month)
        else:
            start_date = str(year_name) + '-' + str(month) + '-' + '01'
            month_val=str(month)

        if int(this.month.month) in [1,3,5,7,8,10,12]:
            month_tup = 31
        if int(this.month.month) in [4,6,9,11]:
            month_tup = 30
        if int(this.month.month) in [2]:
            if int(this.month.year_id.name) % 4 == 0:
                month_tup = 29
            else:
                month_tup = 28
            
        month_val=int(month_val)
#        month_tup = calendar.monthrange(year,month_val)
        end_date = str(year_name) + '-' + str(month_val) + '-' + str(month_tup)
        
        for month_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(start_date,'%Y-%m-%d'),until=datetime.strptime(end_date,'%Y-%m-%d')):
            month_date = datetime.strftime(month_date,"%Y-%m-%d")
            full_date_month.append(month_date) 

        if this.company_id:
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',company_id),('epf_tick','=',True),('type','=','Employee')])
            inact_ids=emp_obj.search(cr, uid, [('active','=',False),('company_id','=',company_id),('epf_tick','=',True),('epf_end_date','>=',start_date),('epf_end_date','<=',end_date),('type','=','Employee')]) 
        if len(list_ids) == 0 :
            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))
        if inact_ids :
            for val in inact_ids :
                inact_emp_browse=emp_obj.browse(cr,uid,val)
                if inact_emp_browse :
                    inact_id=val
                    inact_emp_name=inact_emp_browse.name
                    inact_emp_sinid=inact_emp_browse.sinid
                    inact_days_amount=0
                    tup=(inact_id,inact_emp_name,inact_days_amount,inact_emp_sinid)
                    inact_list.append(tup)
                    inact_list1.append(val)
        if len(list_ids) == 1 :
            query ="select spl.employee_id,spl.employee_name,spl.gross,spl.sinid,spl.epf,spl.epf1,spl.epf2,spl.days_amount,spl.other_salary_amount from salary_payment_line as spl  where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' and spl.epf <> 0.00 order by spl.sinid "                           
            cr.execute(query)
            temp = cr.fetchall()
            query1 ="select spl.employee_id from salary_payment_line as spl  where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' and spl.epf <> 0.00 order by spl.sinid "                           
            cr.execute(query1)
            temp1 = cr.fetchall()
        else :
            query ="select spl.employee_id,spl.employee_name,spl.gross,spl.sinid,spl.epf,spl.epf1,spl.epf2,spl.days_amount,spl.other_salary_amount from salary_payment_line as spl  where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' and spl.epf <> 0.00 order by spl.sinid "                           
            cr.execute(query)
            temp = cr.fetchall()
            query1 ="select spl.employee_id from salary_payment_line as spl  where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' and spl.epf <> 0.00 order by spl.sinid "                           
            cr.execute(query1)
            temp1 = cr.fetchall()
            
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!")) 
        
        temp_add_value1=temp1 + inact_list1
        emp_list = emp_obj.search(cr, uid, [('id','not in',temp_add_value1),('active','=',True),('company_id','=',company_id),('epf_tick','=',True),('doj','<=',end_date),('type','=','Employee')])
        if emp_list:
            for valll in emp_list :
                emp_list_ids=emp_obj.browse(cr,uid,valll)
                hr_id=valll
                hr_name=emp_list_ids.name
                hr_sinid=emp_list_ids.sinid
                hr_days_amount=0
                tup=(hr_id,hr_name,hr_days_amount,hr_sinid)
                hr_list.append(tup)
        
        if temp:
            temp_add_value=temp + inact_list + hr_list
            temp_add_value=sorted(temp_add_value, key=lambda x: x[3])
            for val in temp_add_value :
                epf_cont=0
                eps_cont=0
                calc_eps_epf=0
                epf_gross_wages=0
                ws.row(i).height=500
                emp_browse=emp_obj.browse(cr,uid,val[0])
#                emp_pf=emp_browse.pf_number
                uan_number = emp_browse.uan
                if val[2]:
                    gross = val[7] + val[8]
                else:
                    gross = 0
                      
#                if '/' in emp_pf :
#                    emp_pf=emp_pf.upper().split('/')
#                    emp_pf_len=len(emp_pf)-1
#                    if emp_pf :
#                        pf_no=emp_pf[emp_pf_len]
                if len(val) > 5 :        
                    epf_cont=val[4]
                    eps_cont=val[5]
                    calc_eps_epf=val[6]
                    epf_gross_wages=round(val[2],0)
                diff_eps_epf=(epf_cont-eps_cont)
                date_of_join_epf=emp_browse.epf_start_date
                date_of_exit_epf=emp_browse.epf_end_date
#                f_name=''
#                relation_member = ''
#                date_of_birth=''
#                gender= ''
#                epf_date_start=''
#                leave_reason=' '
#                epf_end_date=' '
#                if  date_of_join_epf :
#                    if date_of_join_epf in full_date_month :
#                        epf_date_start=datetime.strptime(date_of_join_epf,'%Y-%m-%d')
#                        epf_date_start=epf_date_start.strftime('%d-%m-%Y')
#                        query1 = cr.execute("select name from family where employee_id='"+str(val[0])+"' and relation='Father'  ")
#                        temp1  = cr.fetchall()
#                        if temp1 :
#                            f_name = temp1[0][0] 
#                        relation_member='F'       
#                        date_of_birth=emp_browse.birthday
#                        date_of_birth=datetime.strptime(date_of_birth,'%Y-%m-%d')
#                        date_of_birth=date_of_birth.strftime('%d-%m-%Y')
#                        gender=emp_browse.gender
#                        gender=gender.upper()[0]
                        
#                if date_of_exit_epf  :
#                    leave_reason=emp_browse.leaving_reason[0]
#                    epf_end_date=datetime.strptime(date_of_exit_epf,'%Y-%m-%d')
#                    epf_end_date=epf_end_date.strftime('%d-%m-%Y')

#                if  date_of_join_epf and not  date_of_exit_epf :
#                    leave_reason='&'
#                    epf_end_date='&'
                    
#                if not  date_of_join_epf and  date_of_exit_epf :
#                    epf_date_start='&'
                    
                total_epf_wages+=val[2]
                total_epf_cont+=epf_cont
                total_eps_cont+=eps_cont
                total_diff_calc+=calc_eps_epf
                total_diff_diff+=diff_eps_epf
                total_gross+=gross 
                

                ws.write(i,0,(val[3]),style_header2)
                ws.write(i,1,uan_number,style_header2)         
#                ws.write(i,1,pf_no,style_header2)
                ws.write(i,2,(val[1]),style_header2)
                ws.write(i,3,gross,style_header2)
                ws.write(i,4,epf_gross_wages,style_header2)
                ws.write(i,5,epf_gross_wages,style_header2)
                ws.write(i,6,epf_gross_wages,style_header2)
                ws.write(i,7,epf_cont,style_header2)
#                ws.write(i,6,epf_cont,style_header2)
                ws.write(i,8,eps_cont,style_header2)
#                ws.write(i,8,eps_cont,style_header2)
                ws.write(i,9,calc_eps_epf,style_header2)
#                ws.write(i,10,diff_eps_epf,style_header2)
                ws.write(i,10,val_zero,style_header2)
                ws.write(i,11,val_zero,style_header2)
#                ws.write(i,15,val_zero,style_header2)
#                ws.write(i,16,val_zero,style_header2)
#                ws.write(i,17,val_zero,style_header2)
#                ws.write(i,18,val_zero,style_header2)
#                ws.write(i,19,f_name and  f_name or '&',style_header2)
#                ws.write(i,20,relation_member and relation_member or '&',style_header2)
#                ws.write(i,21,date_of_birth and date_of_birth or '&',style_header2)
#                ws.write(i,22,gender and gender or '&',style_header2)
#                ws.write(i,23,epf_date_start and epf_date_start or '&',style_header2)
#                ws.write(i,24,epf_date_start and epf_date_start or '&',style_header2)
#                ws.write(i,25,epf_end_date,style_header2)
#                ws.write(i,26,epf_end_date,style_header2)
#                ws.write(i,27,leave_reason,style_header2)
                i=i+1
                
        ws.row(i+1).height=500
        ws.write(i+1,2,'TOTAL',style_header1)
        ws.write(i+1,3,total_gross,style_header1)        
        ws.write(i+1,4,total_epf_wages,style_header1)
        ws.write(i+1,5,total_epf_wages,style_header1)
        ws.write(i+1,6,total_epf_wages,style_header1)
        ws.write(i+1,7,total_epf_cont,style_header1)
        ws.write(i+1,8,total_eps_cont,style_header1)
        ws.write(i+1,9,total_diff_calc,style_header1)
        
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        pf_upload_report = self.write(cr, uid, ids, {'export_data':out, 'filename':'employee_pf_upload.xls'}, context=context)
        return pf_upload_report
    
    
    
    
#                            Contractor Pf Upload Report
    
class wiz_contractor_pf_upload_report(osv.TransientModel):
    _name = 'wiz.contractor.pf.upload.report'
    _columns = {
                    'month':fields.many2one('holiday.list','Month',required=True),
                    'company_id':fields.many2one('res.company','Company'),
                    'partner_id':fields.many2one('res.partner','Contractor'),
                    'export_data':fields.binary('File',readonly=True),
                    'filename':fields.char('File Name',size=250,readonly=True),
                }
    
    def pf_upload_report(self,cr,uid,ids,context=None):
        f_name =''
        d_name = ''
        wb = Workbook()
        ws = wb.add_sheet('CONTRACTOR PF UPLOAD')
        fnt1 = Font()
        fnt1.name = 'Arial'
        fnt1.height= 300
        fnt1.bold=True
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_CENTER
        borders1 = Borders()
        borders1.left = 0x02
        borders1.right = 0x02
        borders1.top = 0x02
        borders1.bottom = 0x02
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_CENTER
        pattern1 = Pattern()
        pattern1.pattern1 = Pattern.SOLID_PATTERN
        pattern1.pattern1_fore_colour=0x17
        style_header1= XFStyle()
        style_header1.font= fnt1
        style_header1.pattern= pattern1
        style_header1.borders = borders1
        style_header1.alignment=align1
        
        fnt2 = Font()
        fnt2.name = 'Arial'
        fnt2.height= 250
        fnt2.bold=False
        align_content2 = Alignment()
        align_content2.horz= Alignment.HORZ_CENTER
        borders2 = Borders()
        borders2.left = 0x02
        borders2.right = 0x02
        borders2.top = 0x02
        borders2.bottom = 0x02
        align2 = Alignment()
        align2.horz = Alignment.HORZ_CENTER
        align2.vert = Alignment.VERT_CENTER
        pattern2 = Pattern()
        pattern2.pattern2 = Pattern.SOLID_PATTERN
        pattern2.pattern2_fore_colour=0x09
        style_header2= XFStyle()
        style_header2.font= fnt2
        style_header2.pattern= pattern2
        style_header2.borders = borders2
        style_header2.alignment=align2

        fnt3 = Font()
        fnt3.name = 'Arial'
        fnt3.height= 275
        fnt3.bold=False
        align_content3 = Alignment()
        align_content3.horz= Alignment.HORZ_CENTER
        borders3 = Borders()
        borders3.left = 0x02
        borders3.right = 0x02
        borders3.top = 0x02
        borders3.bottom = 0x02
        align3 = Alignment()
        align3.horz = Alignment.HORZ_CENTER
        align3.vert = Alignment.VERT_CENTER
        pattern3 = Pattern()
        pattern3.pattern3 = Pattern.SOLID_PATTERN
        pattern3.pattern3_fore_colour =  0x09
        style_header3= XFStyle()
        style_header3.font= fnt3
        style_header3.pattern= pattern3
        style_header3.borders = borders3
        style_header3.alignment=align3
        
        fnt = Font()
        fnt.name = 'Arial' 
        fnt.height= 275
        content_fnt = Font()
        content_fnt.name ='Arial'
        content_fnt.height =150
        align_content = Alignment()
        align_content.horz= Alignment.HORZ_CENTER
        borders = Borders()
        borders.left = 0x02
        borders.right = 0x02
        borders.top = 0x02
        borders.bottom = 0x02
        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        align.vert = Alignment.VERT_CENTER
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour =  0x16
        style_header= XFStyle()
        style_header.font= fnt
        style_header.pattern= pattern
        style_header.borders = borders
        style_header.alignment=align

        fnt5 = Font()
        fnt5.name = 'Arial'
        fnt5.height= 275
        content_fnt5 = Font()
        content_fnt5.name ='Arial'
        content_fnt5.height =150
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

       
      
        ws.row(0).height=1500
        ws.col(0).width = 6500
        ws.col(1).width = 5000 
        ws.col(2).width = 10000 
        ws.col(3).width = 4000 
        ws.col(4).width = 4000 
        ws.col(5).width = 4500 
        ws.col(6).width = 4000   
        ws.col(7).width = 5500
        ws.col(8).width = 4000 
        ws.col(9).width = 4500 
        ws.col(10).width = 4000   
        ws.col(11).width = 4000 
        
        ws.write(0,0,'Employee Pay Code',style_header)
        ws.write(0,1,'UAN Number',style_header)
        ws.write(0,2,'Member Name',style_header)
        ws.write(0,3,'Gross Wages',style_header)
        ws.write(0,4,'EPF Wages',style_header)
        ws.write(0,5,'EPS Wages',style_header)
        ws.write(0,6,'EDLI Wages',style_header)        
        ws.write(0,7,'EE Share',style_header)
        ws.write(0,8,'EPS Contribution',style_header)
        ws.write(0,9,'ER Share',style_header)
        ws.write(0,10,'NCP Days',style_header)
        ws.write(0,11,'Refund',style_header)
        
        this=self.browse(cr,uid,ids[0],context=context)
        month=this.month.month
        company_id = this.company_id.id
        year=this.month.year_id.id
        year_name=this.month.year_id.name
        partner_id = this.partner_id.id
        emp_obj = self.pool.get('hr.employee') 
#        pf_no=' '
        emp_name=' '
        epf_cont=0
        eps_cont=0
        calc_eps_epf=0
        diff_eps_epf=0
        full_date_month=[]
        total_epf_wages=0
        total_epf_cont=0
        total_eps_cont=0
        total_diff_calc=0
        total_diff_diff=0
        total_gross=0
        holiday_list=[]
        inact_list=[]
        inact_list1=[]
        hr_list=[]
        i=1
        val_zero=0
#        epf_date_start=''
        
        if len(str(month))==1:
            start_date = str(year_name) + '-' +'0'+ str(month) + '-' + '01'
            month_val='0'+str(month)
        else:
            start_date = str(year_name) + '-' + str(month) + '-' + '01'
            month_val=str(month)

        if int(this.month.month) in [1,3,5,7,8,10,12]:
            month_tup = 31
        if int(this.month.month) in [4,6,9,11]:
            month_tup = 30
        if int(this.month.month) in [2]:
            if int(this.month.year_id.name) % 4 == 0:
                month_tup = 29
            else:
                month_tup = 28
            
        month_val=int(month_val)
#        month_tup = calendar.monthrange(year,month_val)
        end_date = str(year_name) + '-' + str(month_val) + '-' + str(month_tup)
            
#        month_val=int(month_val)
#        month_tup = calendar.monthrange(year,month_val)
#        end_date = str(year_name) + '-' + str(month_val) + '-' + str(month_tup[1])
        
        for month_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(start_date,'%Y-%m-%d'),until=datetime.strptime(end_date,'%Y-%m-%d')):
            month_date = datetime.strftime(month_date,"%Y-%m-%d")
            full_date_month.append(month_date) 

        if this.company_id:
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',company_id),('epf_tick','=',True),('type','=','Contractor')])
            inact_ids=emp_obj.search(cr, uid, [('active','=',False),('company_id','=',company_id),('epf_tick','=',True),('epf_end_date','>=',start_date),('epf_end_date','<=',end_date),('type','=','Contractor')]) 
        elif this.partner_id:
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('partner_id','=',partner_id),('epf_tick','=',True),('type','=','Contractor')])
            inact_ids=emp_obj.search(cr, uid, [('active','=',False),('partner_id','=',partner_id),('epf_tick','=',True),('epf_end_date','>=',start_date),('epf_end_date','<=',end_date),('type','=','Contractor')]) 

        if len(list_ids) == 0 :
            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))
        if inact_ids :
            for val in inact_ids :
                inact_emp_browse=emp_obj.browse(cr,uid,val)
                if inact_emp_browse :
                    inact_id=val
                    inact_emp_name=inact_emp_browse.name
                    inact_emp_sinid=inact_emp_browse.sinid
                    inact_days_amount=0
                    tup=(inact_id,inact_emp_name,inact_days_amount,inact_emp_sinid)
                    inact_list.append(tup)
                    inact_list1.append(val)
        if len(list_ids) == 1 :
            query ="select spl.employee_id,spl.employee_name,spl.gross,spl.sinid,spl.epf,spl.epf1,spl.epf2,spl.days_amount,spl.other_salary_amount from salary_payment_line as spl  where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' and spl.epf <> 0.00 order by spl.sinid "                           
            cr.execute(query)
            temp = cr.fetchall()
            query1 ="select spl.employee_id from salary_payment_line as spl  where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' and spl.epf <> 0.00 order by spl.sinid "                           
            cr.execute(query1)
            temp1 = cr.fetchall()
        else :
            query ="select spl.employee_id,spl.employee_name,spl.gross,spl.sinid,spl.epf,spl.epf1,spl.epf2,spl.days_amount,spl.other_salary_amount from salary_payment_line as spl  where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' and spl.epf <> 0.00 order by spl.sinid "                           
            cr.execute(query)
            temp = cr.fetchall()
            query1 ="select spl.employee_id from salary_payment_line as spl  where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month)+"' and spl.year_id='"+str(year)+"' and spl.epf <> 0.00 order by spl.sinid "                           
            cr.execute(query1)
            temp1 = cr.fetchall()
            
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!")) 
        
        temp_add_value1=temp1 + inact_list1
        emp_list = emp_obj.search(cr, uid, [('id','not in',temp_add_value1),('active','=',True),('company_id','=',company_id),('epf_tick','=',True),('doj','<=',end_date),('type','=','Contractor')])
        if emp_list:
            for valll in emp_list :
                emp_list_ids=emp_obj.browse(cr,uid,valll)
                hr_id=valll
                hr_name=emp_list_ids.name
                hr_sinid=emp_list_ids.sinid
                hr_days_amount=0
                tup=(hr_id,hr_name,hr_days_amount,hr_sinid)
                hr_list.append(tup)
        
        if temp:
            temp_add_value=temp + inact_list + hr_list
            temp_add_value=sorted(temp_add_value, key=lambda x: x[3])
            for val in temp_add_value :
                epf_cont=0
                eps_cont=0
                calc_eps_epf=0
                epf_gross_wages=0
                ws.row(i).height=500
                emp_browse=emp_obj.browse(cr,uid,val[0])
                uan_number = emp_browse.uan
                if val[2]:
                    gross = val[7] + val[8]
                else:
                    gross = 0
                      
                if len(val) > 5 :        
                    epf_cont=val[4]
                    eps_cont=val[5]
                    calc_eps_epf=val[6]
                    epf_gross_wages=round(val[2],0)
                diff_eps_epf=(epf_cont-eps_cont)
                date_of_join_epf=emp_browse.epf_start_date
                date_of_exit_epf=emp_browse.epf_end_date
                    
                total_epf_wages+=val[2]
                total_epf_cont+=epf_cont
                total_eps_cont+=eps_cont
                total_diff_calc+=calc_eps_epf
                total_diff_diff+=diff_eps_epf
                total_gross+=gross 
                
                ws.write(i,0,(val[3]),style_header2)
                ws.write(i,1,uan_number,style_header2)         
                ws.write(i,2,(val[1]),style_header2)
                ws.write(i,3,gross,style_header2)
                ws.write(i,4,epf_gross_wages,style_header2)
                ws.write(i,5,epf_gross_wages,style_header2)
                ws.write(i,6,epf_gross_wages,style_header2)
                ws.write(i,7,epf_cont,style_header2)
                ws.write(i,8,eps_cont,style_header2)
                ws.write(i,9,calc_eps_epf,style_header2)
                ws.write(i,10,val_zero,style_header2)
                ws.write(i,11,val_zero,style_header2)
                i=i+1
                
        ws.row(i+1).height=500
        ws.write(i+1,2,'TOTAL',style_header1)
        ws.write(i+1,3,total_gross,style_header1)        
        ws.write(i+1,4,total_epf_wages,style_header1)
        ws.write(i+1,5,total_epf_wages,style_header1)
        ws.write(i+1,6,total_epf_wages,style_header1)
        ws.write(i+1,7,total_epf_cont,style_header1)
        ws.write(i+1,8,total_eps_cont,style_header1)
        ws.write(i+1,9,total_diff_calc,style_header1)
        
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        pf_upload_report = self.write(cr, uid, ids, {'export_data':out, 'filename':'contractor_pf_upload.xls'}, context=context)
        return pf_upload_report    