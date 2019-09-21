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


class wiz_employee_bonus_report(osv.TransientModel):
    _name = 'wiz.employee.bonus.report'
    
    _columns = {
                'from_date':fields.date('From Date',required=True),
                'till_date':fields.date('Till Date',required=True),
                'company_id':fields.many2one('res.company','Company'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'export_data':fields.binary('File',readonly=True),
                'filename':fields.char('File Name',size=250,readonly=True),
               }

    def performance_register_report(self, cr, uid, ids, data, context=None):
        obj = self.browse(cr,uid,ids)
        emp_obj = self.pool.get('hr.employee') 
        f_name = ''
        d_name = ''
        wb = Workbook()
        ws = wb.add_sheet('Payment Bonus')
        total_salary=apr_salary=may_salary=june_salary=july_salary=aug_salary=sep_salary=oct_salary=nov_salary=dec_salary=jan_salary=feb_salary=mar_salary=0
        
        fnt1 = Font()
        fnt1.name = 'Arial'
        fnt1.height= 300
        fnt1.bold=True
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_CENTER
        borders1 = Borders()
        borders1.left = 0x00
        borders1.right = 0x00
        borders1.top = 0x00
        borders1.bottom = 0x00
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_CENTER
        pattern1 = Pattern()
        pattern1.pattern1 = Pattern.SOLID_PATTERN
        pattern1.pattern1_fore_colour =  0x1F
        style_header1= XFStyle()
        style_header1.font= fnt1
        style_header1.pattern= pattern1
        style_header1.borders = borders1
        style_header1.alignment=align1
        
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
        borders.bottom = 0x00
        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        align.vert = Alignment.VERT_CENTER
        pattern = Pattern()
        pattern.pattern = Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour =  0x1F
        style_header= XFStyle()
        style_header.font= fnt
        style_header.pattern= pattern
        style_header.borders = borders
        style_header.alignment=align
        
        
        fnt7 = Font()
        fnt7.name = 'Arial'
        fnt7.height= 275
        content_fnt7 = Font()
        content_fnt7.name ='Arial'
        content_fnt7.height =150
        align_content7 = Alignment()
        align_content7.horz= Alignment.HORZ_CENTER
        borders7 = Borders()
        borders7.left = 0x02
        borders7.right = 0x02
        borders7.top = 0x02
        borders7.bottom = 0x02
        align7 = Alignment()
        align7.horz = Alignment.HORZ_CENTER
        align7.vert = Alignment.VERT_CENTER
        pattern7 = Pattern()
        pattern7.pattern7 = Pattern.SOLID_PATTERN
        pattern7.pattern7_fore_colour =  0x1F
        style_header7= XFStyle()
        style_header7.font= fnt
        style_header7.pattern= pattern
        style_header7.borders = borders
        style_header7.alignment=align
        
        fnt2 = Font()
        fnt2.name = 'Arial'
        fnt2.height= 275
        content_fnt2 = Font()
        content_fnt2.name ='Arial'
        content_fnt2.height =150
        fnt2.bold=True
        align_content2 = Alignment()
        align_content2.horz= Alignment.HORZ_CENTER
        borders2 = Borders()
        borders2.left = 0x00
        borders2.right = 0x02
        borders2.top = 0x02
        borders2.bottom = 0x02
        align2 = Alignment()
        align2.horz = Alignment.HORZ_CENTER
        align2.vert = Alignment.VERT_CENTER
        pattern2 = Pattern()
        pattern2.pattern2 = Pattern.SOLID_PATTERN
        pattern2.pattern2_fore_colour =  0x1F
        style_header2= XFStyle()
        style_header2.font= fnt2
        style_header2.pattern= pattern2
        style_header2.borders = borders2
        style_header2.alignment=align2

        fnt3 = Font()
        fnt3.name = 'Arial'
        fnt3.height= 300
        fnt3.bold=True
        align_content3 = Alignment()
        align_content3.horz= Alignment.HORZ_CENTER
        borders3 = Borders()
        borders3.left = 0x00
        borders3.right = 0x02
        borders3.top = 0x02
        borders3.bottom = 0x02
        align3 = Alignment()
        align3.horz = Alignment.HORZ_CENTER
        align3.vert = Alignment.VERT_CENTER
        pattern3 = Pattern()
        pattern3.pattern3 = Pattern.SOLID_PATTERN
        pattern3.pattern3_fore_colour =  0x1F
        style_header3= XFStyle()
        style_header3.font= fnt3
        style_header3.pattern= pattern3
        style_header3.borders = borders3
        style_header3.alignment=align3
        
        
        
        fnt6 = Font()
        fnt6.name = 'Arial'
        fnt6.height= 275
        content_fnt6 = Font()
        content_fnt6.name ='Arial'
        content_fnt6.height =150
        align_content6 = Alignment()
        align_content6.horz= Alignment.HORZ_CENTER
        borders6 = Borders()
        borders6.left = 0x02
        borders6.right = 0x02
#         borders6.top = 0x00
#         borders6.bottom = 0x00
        align6 = Alignment()
        align6.horz = Alignment.HORZ_CENTER
        align6.vert = Alignment.VERT_CENTER
        pattern6 = Pattern()
        pattern6.pattern = Pattern.SOLID_PATTERN
        pattern6.pattern_fore_colour =  0x1F
        style_header6= XFStyle()
        style_header6.font= fnt
        style_header6.pattern= pattern
        style_header6.borders = borders6
     
        style_header6.alignment=align

        fnt5 = Font()
        fnt5.name = 'Arial'
        fnt5.height= 200
        content_fnt5 = Font()
        content_fnt5.name ='Arial'
        content_fnt5.height =150
        align_content5 = Alignment()
        align_content5.horz= Alignment.HORZ_CENTER
        borders5 = Borders()
        borders5.left = 0x02
        borders5.right = 0x02
        borders5.top = 0x02
        borders5.bottom = 0x02
        align5 = Alignment()
        align5.horz = Alignment.HORZ_CENTER
        align5.vert = Alignment.VERT_CENTER
        pattern5 = Pattern()
#        pattern5.pattern = Pattern.SOLID_PATTERN
#        pattern5.pattern_fore_colour =  0x1F
        style_header5= XFStyle()
        style_header5.font= fnt5
        style_header5.pattern= pattern5
        style_header5.borders = borders5
        style_header5.alignment=align5

        if obj.company_id:
            get_name = obj.company_id.name + ' ' + obj.company_id.street + ' ' + ','+ obj.company_id.city + ' ' + '-' + obj.company_id.zip
        else:
            get_name = obj.employee_id.resource_id.company_id.name + ' ' + obj.employee_id.resource_id.company_id.street + ' ' + ','+ obj.employee_id.resource_id.company_id.city + ' ' + '-' + obj.employee_id.resource_id.company_id.zip

        date1 = datetime.strptime(obj.from_date,"%Y-%m-%d").timetuple().tm_year
        date2 = datetime.strptime(obj.till_date,"%Y-%m-%d").timetuple().tm_year
        if date1 == date2 :
            d_name = 'BONUS PAID TO EMPLOYEES FOR THE ACCOUNTING YEAR ON THE' +' - '+ str(date1) + ' ' + '[See Rule 4(b)]'
        else:
            d_name = 'BONUS PAID TO EMPLOYEES FOR THE ACCOUNTING YEAR ON THE' +'  '+ str(date1) + ' ' + '-' + ' ' +  str(date2) + ' ' + '[See Rule 4(b)]'
               
                      
        ws.row(0).height=500
        ws.row(1).height=500
        ws.write_merge(0,0,0,2,'FORM C',style_header1)
        ws.write_merge(0,0,3,10,d_name,style_header1)
        ws.write_merge(1,1,0,2,'Name of the Establishment',style_header1)
        ws.write_merge(1,1,3,10,get_name,style_header1) 
        ws.write_merge(1,1,11,19,'No. of Working days in the Year',style_header1)        
        


        ws.col(0).width = 5000 
        ws.col(1).width = 7500
        ws.col(2).width = 5000    
        ws.col(3).width = 7000 
        ws.col(4).width = 5000 
        ws.col(5).width = 8000
        ws.col(6).width = 6000   
        ws.col(7).width = 8000 
        ws.col(8).width = 8000 
        ws.col(9).width = 9000 
        ws.col(10).width = 8000   
        ws.col(11).width = 9000 
        ws.col(12).width = 7000 
        ws.col(13).width = 7000 
        ws.col(14).width = 5000   
        ws.col(15).width = 5000 
        ws.col(16).width = 7000 
        ws.col(17).width = 3000 
        ws.col(18).width = 3000   
        ws.col(19).width = 3000 
        ws.col(20).width = 3000 
        ws.col(21).width = 3000 
        ws.col(22).width = 3000   
        ws.col(23).width = 3000 
        ws.col(24).width = 3000 
        ws.col(25).width = 3000 
        ws.col(26).width = 3000   
        ws.col(27).width = 3000 
        ws.col(28).width = 3000 
        ws.col(29).width = 4000
        
        ws.row(2).height=400
        ws.write(2,0,'EMP. CODE',style_header)
        ws.write(2,1,'NAME',style_header)
        ws.write(2,2,'JOINING DATE',style_header)
        ws.write(2,3,'Father Name',style_header)
        ws.write(2,4,'Designation',style_header)
        ws.write(2,5,'Whether he has ',style_header)  
        ws.write(2,6,'No.of days',style_header)
        ws.write(2,7,'Total Salary or wages',style_header)
        ws.write(2,8,'Account of bonus payable',style_header)
        ws.write_merge(2,2,9,12,'Deduction',style_header7)
        ws.write(2,13,'Net amount payable',style_header)
        ws.write(2,14,'Amount actualy',style_header)
        ws.write(2,15,'Date on which ',style_header)
        ws.write(2,16,'Signature/ Thumb ',style_header)
        ws.write(2,17,'Remarks',style_header)
        ws.write_merge(2,2,18,19,'APRIL',style_header7)
        ws.write_merge(2,2,20,21,'MAY',style_header7)
        ws.write_merge(2,2,22,23,'JUNE',style_header7)
        ws.write_merge(2,2,24,25,'JULY',style_header7)
        ws.write_merge(2,2,26,27,'AUGUST',style_header7)
        ws.write_merge(2,2,28,29,'SEPTEMBER',style_header7)
        ws.write_merge(2,2,30,31,'OCTOBER',style_header7)
        ws.write_merge(2,2,32,33,'NOVEMBER',style_header7)
        ws.write_merge(2,2,34,35,'DECEMBER',style_header7)
        ws.write_merge(2,2,36,37,'JANUARY',style_header7)
        ws.write_merge(2,2,38,39,'FEBRUARY',style_header7)
        ws.write_merge(2,2,40,41,'MARCH',style_header7)
        ws.write_merge(2,2,42,43,'TOTAL',style_header7)
        ws.write(2,44,'BONUS',style_header)

        ws.row(3).height=400
        ws.write(3,0,'',style_header6)
        ws.write(3,1,'',style_header6)
        ws.write(3,2,'',style_header6)
        ws.write(3,3,'',style_header6)
        ws.write(3,4,'',style_header6)
        ws.write(3,5,'completed 15 year of',style_header6)
        ws.write(3,6,'worked in the',style_header6)
        ws.write(3,7,'in respect of',style_header6)
        ws.write(3,8,'under section 10',style_header6)
        ws.write(3,9,'Puja bonus or other customary',style_header7)
        ws.write(3,10,'Interim bonus',style_header7)
        ws.write(3,11,'Deduction on account of financial',style_header7)
        ws.write(3,12,'Total sum deducted',style_header7)
        ws.write(3,13,'(Col.8 minus Col.12)',style_header6)
        ws.write(3,14,'paid',style_header6)
        ws.write(3,15,'paid',style_header6)
        ws.write(3,16,'impression',style_header6)
        ws.write(3,17,'',style_header6)       
        ws.write(3,18,'',style_header7)
        ws.write(3,19,'',style_header7)
        ws.write(3,20,'',style_header7)
        ws.write(3,21,'',style_header7)
        ws.write(3,22,'',style_header7)
        ws.write(3,23,'',style_header7)
        ws.write(3,24,'',style_header7)
        ws.write(3,25,'',style_header7)
        ws.write(3,26,'',style_header7)
        ws.write(3,27,'',style_header7)
        ws.write(3,28,'',style_header7)
        ws.write(3,29,'',style_header7)
        ws.write(3,30,'',style_header7)
        ws.write(3,31,'',style_header7)
        ws.write(3,32,'',style_header7)
        ws.write(3,33,'',style_header7)
        ws.write(3,34,'',style_header7)
        ws.write(3,35,'',style_header7)
        ws.write(3,36,'',style_header7)
        ws.write(3,37,'',style_header7)
        ws.write(3,38,'',style_header7)
        ws.write(3,39,'',style_header7)
        ws.write(3,40,'',style_header7)
        ws.write(3,41,'',style_header7)
        ws.write(3,42,'',style_header7)
        ws.write(3,43,'',style_header7)
        ws.write(3,44,'',style_header7)
        
        ws.row(4).height=400
        ws.write(4,0,'',style_header6)
        ws.write(4,1,'',style_header6)
        ws.write(4,2,'',style_header6)
        ws.write(4,3,'',style_header6)
        ws.write(4,4,'',style_header6)
        ws.write(4,5,'age at the beginning',style_header6)
        ws.write(4,6,'Establishment',style_header6)
        ws.write(4,7,'the accounting year',style_header6)
        ws.write(4,8,'or section 11',style_header6)
        ws.write(4,9,'bonus paid during',style_header6)
        ws.write(4,10,'or bonus paid in ',style_header6)
        ws.write(4,11,'loss if any caused by',style_header6)
        ws.write(4,12,'(Col.9,10 and 11)',style_header6)
        ws.write(4,13,'',style_header6)
        ws.write(4,14,'',style_header6)
        ws.write(4,15,'',style_header6)
        ws.write(4,16,'of the employee',style_header6)
        ws.write(4,17,'',style_header6)       
        ws.write(4,18,'',style_header6)
        ws.write(4,19,'',style_header6)
        ws.write(4,20,'',style_header6)
        ws.write(4,21,'',style_header6)
        ws.write(4,22,'',style_header6)
        ws.write(4,23,'',style_header6)
        ws.write(4,24,'',style_header6)
        ws.write(4,25,'',style_header6)
        ws.write(4,26,'',style_header6)
        ws.write(4,27,'',style_header6)
        ws.write(4,28,'',style_header6)
        ws.write(4,29,'',style_header6)
        ws.write(4,30,'',style_header6)
        ws.write(4,31,'',style_header6)
        ws.write(4,32,'',style_header6)
        ws.write(4,33,'',style_header6)
        ws.write(4,34,'',style_header6)
        ws.write(4,35,'',style_header6)
        ws.write(4,36,'',style_header6)
        ws.write(4,37,'',style_header6)
        ws.write(4,38,'',style_header6)
        ws.write(4,39,'',style_header6)
        ws.write(4,40,'',style_header6)
        ws.write(4,41,'',style_header6)
        ws.write(4,42,'',style_header6)
        ws.write(4,43,'',style_header6)
        ws.write(4,44,'',style_header6)
        
        ws.row(5).height=400
        ws.write(5,0,'',style_header6)
        ws.write(5,1,'',style_header6)
        ws.write(5,2,'',style_header6)
        ws.write(5,3,'',style_header6)
        ws.write(5,4,'',style_header6)
        ws.write(5,5,'of the accounting year',style_header6)
        ws.write(5,6,'',style_header6)
        ws.write(5,7,'',style_header6)
        ws.write(5,8,'as the case may be',style_header6)
        ws.write(5,9,'the accounting year',style_header6)
        ws.write(5,10,'advance',style_header6)
        ws.write(5,11,'misconduct of the employee',style_header6)
        ws.write(5,12,'',style_header6)
        ws.write(5,13,'',style_header6)
        ws.write(5,14,'',style_header6)
        ws.write(5,15,'',style_header6)
        ws.write(5,16,'',style_header6)
        ws.write(5,17,'',style_header6)       
        ws.write(5,18,'DAYS',style_header6)
        ws.write(5,19,'SALARY',style_header6)
        ws.write(5,20,'DAYS',style_header6)
        ws.write(5,21,'SALARY',style_header6)
        ws.write(5,22,'DAYS',style_header6)
        ws.write(5,23,'SALARY',style_header6)
        ws.write(5,24,'DAYS',style_header6)
        ws.write(5,25,'SALARY',style_header6)
        ws.write(5,26,'DAYS',style_header6)
        ws.write(5,27,'SALARY',style_header6)
        ws.write(5,28,'DAYS',style_header6)
        ws.write(5,29,'SALARY',style_header6)
        ws.write(5,30,'DAYS',style_header6)
        ws.write(5,31,'SALARY',style_header6)
        ws.write(5,32,'DAYS',style_header6)
        ws.write(5,33,'SALARY',style_header6)
        ws.write(5,34,'DAYS',style_header6)
        ws.write(5,35,'SALARY',style_header6)
        ws.write(5,36,'DAYS',style_header6)
        ws.write(5,37,'SALARY',style_header6)
        ws.write(5,38,'DAYS',style_header6)
        ws.write(5,39,'SALARY',style_header6)
        ws.write(5,40,'DAYS',style_header6)
        ws.write(5,41,'SALARY',style_header6)
        ws.write(5,42,'DAYS',style_header6)
        ws.write(5,43,'SALARY',style_header6)
        ws.write(5,44,'',style_header6)

        if obj.company_id:
            list_ids = emp_obj.search(cr, uid, [('company_id','=',obj.company_id.id),('active','=',True),('type','=','Employee')])
            list_ids1 = emp_obj.search(cr, uid, [('company_id','=',obj.company_id.id),('active','=',False),('type','=','Employee')])
            list_ids = list_ids + list_ids1
        elif obj.employee_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', obj.employee_id.id),('active','=',True),('type','=','Employee')])
        
        else:
            raise osv.except_osv(_('Warning !'),_("Please Select Atleast Company Or Employee."))                

        if len(list_ids) == 1 :
            query ="select hr.sinid,rr.name,hr.doj,job.name,hr.id,sum(pmbl.apr),sum(pmbl.may),sum(pmbl.june),sum(pmbl.july),sum(pmbl.aug),sum(pmbl.sep),sum(pmbl.oct),"\
                   "sum(pmbl.nov),sum(pmbl.dec),sum(pmbl.jan),sum(pmbl.feb),sum(pmbl.mar),sum(pmbl.total_day),sum(pmbl.bonus),sum(pmbl.apr_salary),"\
                   "sum(pmbl.may_salary),sum(pmbl.june_salary),sum(pmbl.july_salary),sum(pmbl.aug_salary),sum(pmbl.sep_salary),sum(pmbl.oct_salary),"\
                   "sum(pmbl.nov_salary),sum(pmbl.dec_salary),sum(pmbl.jan_salary),sum(pmbl.feb_salary),sum(pmbl.mar_salary),sum(pmbl.total_salary)"\
                   "from payment_management_bonus_line as pmbl left join hr_employee as hr on pmbl.employee_id = hr.id left join resource_resource as rr on hr.resource_id = rr.id left join hr_job as job on hr.job_id=job.id "\
                    "where pmbl.employee_id = '"+str(list_ids[0])+"' and pmbl.bonus_from >= '"+str(obj.from_date)+"' and pmbl.bonus_till <= '"+str(obj.till_date)+"' group by hr.sinid,rr.name,hr.doj,job.name,hr.id order by hr.sinid "                           
            cr.execute(query)
            temp = cr.fetchall()
        else :
            query ="select hr.sinid,rr.name,hr.doj,job.name,hr.id,sum(pmbl.apr),sum(pmbl.may),sum(pmbl.june),sum(pmbl.july),sum(pmbl.aug),sum(pmbl.sep),sum(pmbl.oct),"\
                   "sum(pmbl.nov),sum(pmbl.dec),sum(pmbl.jan),sum(pmbl.feb),sum(pmbl.mar),sum(pmbl.total_day),sum(pmbl.bonus),sum(pmbl.apr_salary),"\
                   "sum(pmbl.may_salary),sum(pmbl.june_salary),sum(pmbl.july_salary),sum(pmbl.aug_salary),sum(pmbl.sep_salary),sum(pmbl.oct_salary),"\
                   "sum(pmbl.nov_salary),sum(pmbl.dec_salary),sum(pmbl.jan_salary),sum(pmbl.feb_salary),sum(pmbl.mar_salary),sum(pmbl.total_salary)"\
                   "from payment_management_bonus_line as pmbl left join hr_employee as hr on pmbl.employee_id = hr.id left join resource_resource as rr on hr.resource_id = rr.id left join hr_job as job on hr.job_id=job.id "\
                    "where pmbl.employee_id  in "+str(tuple(list_ids))+" and pmbl.bonus_from >= '"+str(obj.from_date)+"' and pmbl.bonus_till <= '"+str(obj.till_date)+"' group by hr.sinid,rr.name,hr.doj,job.name,hr.id order by hr.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))    
        
        columnno = 6
        no=6
        for val in temp :
            father_name=''
            if val[4]:
                 father_qry = "select name from family where relation='Father' and employee_id='"+str(val[4])+"'  "
                 cr.execute(father_qry)
                 father_temp = cr.fetchall()
                 if father_temp:
                     father_name = father_temp[0][0]
                 else:
                     father_name = ' ' 
                     
            ws.row(no).height=500    
            doj = datetime.strptime(val[2],"%Y-%m-%d").strftime("%d-%m-%Y")
            ws.write(columnno,0,val[0],style_header5)
            ws.write(columnno,1,val[1],style_header5)
            ws.write(columnno,2,doj,style_header5)
            ws.write(columnno,3,father_name,style_header5)
            ws.write(columnno,4,val[3],style_header5)
            ws.write(columnno,5,'Yes',style_header5)
            ws.write(columnno,6,'',style_header5)
            ws.write(columnno,7,'',style_header5)
            ws.write(columnno,8,'',style_header5)
            ws.write(columnno,9,'',style_header5)
            ws.write(columnno,10,'',style_header5)
            ws.write(columnno,11,'',style_header5)
            ws.write(columnno,12,'',style_header5)
            ws.write(columnno,13,'',style_header5)
            ws.write(columnno,14,'',style_header5)
            ws.write(columnno,15,'',style_header5)
            ws.write(columnno,16,'',style_header5)
            ws.write(columnno,17,'',style_header5)
            ws.write(columnno,18,val[5],style_header5)
            ws.write(columnno,19,val[19],style_header5)
            ws.write(columnno,20,val[6],style_header5)
            ws.write(columnno,21,val[20],style_header5)
            ws.write(columnno,22,val[7],style_header5)
            ws.write(columnno,23,val[21],style_header5)
            ws.write(columnno,24,val[8],style_header5)
            ws.write(columnno,25,val[22],style_header5)
            ws.write(columnno,26,val[9],style_header5)
            ws.write(columnno,27,val[23],style_header5)
            ws.write(columnno,28,val[10],style_header5)
            ws.write(columnno,29,val[24],style_header5)
            ws.write(columnno,30,val[11],style_header5)
            ws.write(columnno,31,val[25],style_header5)
            ws.write(columnno,32,val[12],style_header5)
            ws.write(columnno,33,val[26],style_header5)
            ws.write(columnno,34,val[13],style_header5)
            ws.write(columnno,35,val[27],style_header5)
            ws.write(columnno,36,val[14],style_header5)
            ws.write(columnno,37,val[28],style_header5)
            ws.write(columnno,38,val[15],style_header5)
            ws.write(columnno,39,val[29],style_header5)
            ws.write(columnno,40,val[16],style_header5)
            ws.write(columnno,41,val[30],style_header5)
            ws.write(columnno,42,val[17],style_header5)
            ws.write(columnno,43,val[31],style_header5)
            ws.write(columnno,44,val[18],style_header5)
            columnno += 1
            no += 1
                
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        
        return self.write(cr, uid, ids, {'export_data':out,'filename':'Payment Bonus.xls'}, context=context)
    
    


#                                           Contractor Bonus Report


class wiz_contractor_bonus_report(osv.TransientModel):
    _name = 'wiz.contractor.bonus.report'
    
    _columns = {
                'from_date':fields.date('From Date',required=True),
                'till_date':fields.date('Till Date',required=True),
                'partner_id':fields.many2one('res.partner','Contractor'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'export_data':fields.binary('File',readonly=True),
                'filename':fields.char('File Name',size=250,readonly=True),
                'company_id':fields.many2one('res.company','Company'),
               }

    def performance_register_report(self, cr, uid, ids, data, context=None):
        obj = self.browse(cr,uid,ids)
        emp_obj = self.pool.get('hr.employee') 
        f_name = ''
        d_name = ''
        wb = Workbook()
        ws = wb.add_sheet('Contractor Payment Bonus')
        total_salary=apr_salary=may_salary=june_salary=july_salary=aug_salary=sep_salary=oct_salary=nov_salary=dec_salary=jan_salary=feb_salary=mar_salary=0
        
        fnt1 = Font()
        fnt1.name = 'Arial'
        fnt1.height= 300
        fnt1.bold=True
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_CENTER
        borders1 = Borders()
        borders1.left = 0x00
        borders1.right = 0x00
        borders1.top = 0x00
        borders1.bottom = 0x00
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_CENTER
        pattern1 = Pattern()
        pattern1.pattern1 = Pattern.SOLID_PATTERN
        pattern1.pattern1_fore_colour =  0x1F
        style_header1= XFStyle()
        style_header1.font= fnt1
        style_header1.pattern= pattern1
        style_header1.borders = borders1
        style_header1.alignment=align1
        
        fnt2 = Font()
        fnt2.name = 'Arial'
        fnt2.height= 300
        fnt2.bold=True
        align_content2 = Alignment()
        align_content2.horz= Alignment.HORZ_CENTER
        borders2 = Borders()
        borders2.left = 0x00
        borders2.right = 0x00
        borders2.top = 0x00
        borders2.bottom = 0x00
        align2 = Alignment()
        align2.horz = Alignment.HORZ_CENTER
        align2.vert = Alignment.VERT_CENTER
        pattern2 = Pattern()
        pattern2.pattern2 = Pattern.SOLID_PATTERN
        pattern2.pattern2_fore_colour =  0x1F
        style_header2= XFStyle()
        style_header2.font= fnt2
        style_header2.pattern= pattern2
        style_header2.borders = borders2
        style_header2.alignment=align2

        fnt3 = Font()
        fnt3.name = 'Arial'
        fnt3.height= 300
        fnt3.bold=True
        align_content3 = Alignment()
        align_content3.horz= Alignment.HORZ_CENTER
        borders3 = Borders()
        borders3.left = 0x00
        borders3.right = 0x00
        borders3.top = 0x00
        borders3.bottom = 0x00
        align3 = Alignment()
        align3.horz = Alignment.HORZ_CENTER
        align3.vert = Alignment.VERT_CENTER
        pattern3 = Pattern()
        pattern3.pattern3 = Pattern.SOLID_PATTERN
        pattern3.pattern3_fore_colour =  0x1F
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
        pattern.pattern_fore_colour =  0x1F
        style_header= XFStyle()
        style_header.font= fnt
        style_header.pattern= pattern
        style_header.borders = borders
        style_header.alignment=align

        fnt5 = Font()
        fnt5.name = 'Arial'
        fnt5.height= 200
        content_fnt5 = Font()
        content_fnt5.name ='Arial'
        content_fnt5.height =150
        align_content5 = Alignment()
        align_content5.horz= Alignment.HORZ_CENTER
        borders5 = Borders()
        borders5.left = 0x02
        borders5.right = 0x02
        borders5.top = 0x02
        borders5.bottom = 0x02
        align5 = Alignment()
        align5.horz = Alignment.HORZ_CENTER
        align5.vert = Alignment.VERT_CENTER
        pattern5 = Pattern()
#        pattern5.pattern = Pattern.SOLID_PATTERN
#        pattern5.pattern_fore_colour =  0x1F
        style_header5= XFStyle()
        style_header5.font= fnt5
        style_header5.pattern= pattern5
        style_header5.borders = borders5
        style_header5.alignment=align5

        if obj.partner_id:
            get_name = obj.partner_id.name
        elif obj.company_id:
            get_name = obj.company_id.name + ' ' + obj.company_id.street + ' ' + ','+ obj.company_id.city + ' ' + '-' + obj.company_id.zip
        else:
            get_name = obj.employee_id.partner_id.name
                      
        ws.row(0).height=500
        ws.write_merge(0,0,0,19,get_name,style_header1)
        
        date1 = datetime.strptime(obj.from_date,"%Y-%m-%d").timetuple().tm_year
        date2 = datetime.strptime(obj.till_date,"%Y-%m-%d").timetuple().tm_year
        if date1 == date2 :
           d_name = 'BONUS' +' - '+ str(date1)
        else:
            d_name = 'BONUS' +'  '+ str(date1) + ' ' + '-' + ' ' +  str(date2)
              
        ws.row(1).height=500
        ws.write_merge(1,1,0,19,d_name,style_header2)


        ws.col(0).width = 5000 
        ws.col(1).width = 7500
        ws.col(2).width = 5000    
        ws.col(3).width = 3000 
        ws.col(4).width = 3000 
        ws.col(5).width = 3000 
        ws.col(6).width = 3000   
        ws.col(7).width = 3000 
        ws.col(8).width = 3000 
        ws.col(9).width = 3000 
        ws.col(10).width = 3000   
        ws.col(11).width = 3000 
        ws.col(12).width = 3000 
        ws.col(13).width = 3000 
        ws.col(14).width = 3000   
        ws.col(15).width = 3000 
        ws.col(16).width = 3000 
        ws.col(17).width = 3000 
        ws.col(18).width = 3000   
        ws.col(19).width = 3000 
        ws.col(20).width = 3000 
        ws.col(21).width = 3000 
        ws.col(22).width = 3000   
        ws.col(23).width = 3000 
        ws.col(24).width = 3000 
        ws.col(25).width = 3000 
        ws.col(26).width = 3000   
        ws.col(27).width = 3000 
        ws.col(28).width = 3000 
        ws.col(29).width = 4000
        
        ws.row(2).height=400
        ws.write(2,0,'EMP. CODE',style_header)
        ws.write(2,1,'NAME',style_header)
        ws.write(2,2,'JOINING DATE',style_header)
        ws.write_merge(2,2,3,4,'APRIL',style_header)
        ws.write_merge(2,2,5,6,'MAY',style_header)
        ws.write_merge(2,2,7,8,'JUNE',style_header)
        ws.write_merge(2,2,9,10,'JULY',style_header)
        ws.write_merge(2,2,11,12,'AUGUST',style_header)
        ws.write_merge(2,2,13,14,'SEPTEMBER',style_header)
        ws.write_merge(2,2,15,16,'OCTOBER',style_header)
        ws.write_merge(2,2,17,18,'NOVEMBER',style_header)
        ws.write_merge(2,2,19,20,'DECEMBER',style_header)
        ws.write_merge(2,2,21,22,'JANUARY',style_header)
        ws.write_merge(2,2,23,24,'FEBRUARY',style_header)
        ws.write_merge(2,2,25,26,'MARCH',style_header)
        ws.write_merge(2,2,27,28,'TOTAL',style_header)
        ws.write(2,29,'BONUS',style_header)

        ws.row(3).height=400
        ws.write(3,0,'',style_header)
        ws.write(3,1,'',style_header)
        ws.write(3,2,'',style_header)
        ws.write(3,3,'DAYS',style_header)
        ws.write(3,4,'SALARY',style_header)
        ws.write(3,5,'DAYS',style_header)
        ws.write(3,6,'SALARY',style_header)
        ws.write(3,7,'DAYS',style_header)
        ws.write(3,8,'SALARY',style_header)
        ws.write(3,9,'DAYS',style_header)
        ws.write(3,10,'SALARY',style_header)
        ws.write(3,11,'DAYS',style_header)
        ws.write(3,12,'SALARY',style_header)
        ws.write(3,13,'DAYS',style_header)
        ws.write(3,14,'SALARY',style_header)
        ws.write(3,15,'DAYS',style_header)
        ws.write(3,16,'SALARY',style_header)
        ws.write(3,17,'DAYS',style_header)
        ws.write(3,18,'SALARY',style_header)
        ws.write(3,19,'DAYS',style_header)
        ws.write(3,20,'SALARY',style_header)
        ws.write(3,21,'DAYS',style_header)
        ws.write(3,22,'SALARY',style_header)
        ws.write(3,23,'DAYS',style_header)
        ws.write(3,24,'SALARY',style_header)
        ws.write(3,25,'DAYS',style_header)
        ws.write(3,26,'SALARY',style_header)
        ws.write(3,27,'DAYS',style_header)
        ws.write(3,28,'SALARY',style_header)
        ws.write(3,29,'',style_header)

        if obj.partner_id:
            list_ids = emp_obj.search(cr, uid, [('partner_id','=',obj.partner_id.id),('active','=',True),('type','=','Contractor')])
            list_ids1 = emp_obj.search(cr, uid, [('partner_id','=',obj.partner_id.id),('active','=',False),('type','=','Contractor')])
            list_ids = list_ids + list_ids1
        elif obj.employee_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', obj.employee_id.id),('active','=',True),('type','=','Contractor')])
        elif obj.company_id:
            list_ids = emp_obj.search(cr, uid, [('company_id','=',obj.company_id.id),('active','=',True),('type','=','Contractor')])
            list_ids1 = emp_obj.search(cr, uid, [('company_id','=',obj.company_id.id),('active','=',False),('type','=','Contractor')])
            list_ids = list_ids + list_ids1
        
        else:
            raise osv.except_osv(_('Warning !'),_("Please Select Atleast Company Or Employee."))                

        if len(list_ids) == 1 :
            query ="select hr.sinid,rr.name,hr.doj,sum(pmbl.apr),sum(pmbl.may),sum(pmbl.june),sum(pmbl.july),sum(pmbl.aug),sum(pmbl.sep),sum(pmbl.oct),"\
                   "sum(pmbl.nov),sum(pmbl.dec),sum(pmbl.jan),sum(pmbl.feb),sum(pmbl.mar),sum(pmbl.total_day),sum(pmbl.bonus),sum(pmbl.apr_salary),"\
                   "sum(pmbl.may_salary),sum(pmbl.june_salary),sum(pmbl.july_salary),sum(pmbl.aug_salary),sum(pmbl.sep_salary),sum(pmbl.oct_salary),"\
                   "sum(pmbl.nov_salary),sum(pmbl.dec_salary),sum(pmbl.jan_salary),sum(pmbl.feb_salary),sum(pmbl.mar_salary),sum(pmbl.total_salary)"\
                   "from payment_management_bonus_line as pmbl left join hr_employee as hr on pmbl.employee_id = hr.id left join resource_resource as rr on hr.resource_id = rr.id "\
                    "where pmbl.employee_id = '"+str(list_ids[0])+"' and pmbl.bonus_from >= '"+str(obj.from_date)+"' and pmbl.bonus_till <= '"+str(obj.till_date)+"' group by hr.sinid,rr.name,hr.doj order by hr.sinid "                           
            cr.execute(query)
            temp = cr.fetchall()
        else :
            query ="select hr.sinid,rr.name,hr.doj,sum(pmbl.apr),sum(pmbl.may),sum(pmbl.june),sum(pmbl.july),sum(pmbl.aug),sum(pmbl.sep),sum(pmbl.oct),"\
                   "sum(pmbl.nov),sum(pmbl.dec),sum(pmbl.jan),sum(pmbl.feb),sum(pmbl.mar),sum(pmbl.total_day),sum(pmbl.bonus),sum(pmbl.apr_salary),"\
                   "sum(pmbl.may_salary),sum(pmbl.june_salary),sum(pmbl.july_salary),sum(pmbl.aug_salary),sum(pmbl.sep_salary),sum(pmbl.oct_salary),"\
                   "sum(pmbl.nov_salary),sum(pmbl.dec_salary),sum(pmbl.jan_salary),sum(pmbl.feb_salary),sum(pmbl.mar_salary),sum(pmbl.total_salary)"\
                   "from payment_management_bonus_line as pmbl left join hr_employee as hr on pmbl.employee_id = hr.id left join resource_resource as rr on hr.resource_id = rr.id "\
                    "where pmbl.employee_id  in "+str(tuple(list_ids))+" and pmbl.bonus_from >= '"+str(obj.from_date)+"' and pmbl.bonus_till <= '"+str(obj.till_date)+"' group by hr.sinid,rr.name,hr.doj order by hr.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))    
        
        columnno = 4
        for val in temp :
            doj = datetime.strptime(val[2],"%Y-%m-%d").strftime("%d-%m-%Y")
            ws.write(columnno,0,val[0],style_header5)
            ws.write(columnno,1,val[1],style_header5)
            ws.write(columnno,2,doj,style_header5)
            ws.write(columnno,3,val[3],style_header5)
            ws.write(columnno,4,val[17],style_header5)
            ws.write(columnno,5,val[4],style_header5)
            ws.write(columnno,6,val[18],style_header5)
            ws.write(columnno,7,val[5],style_header5)
            ws.write(columnno,8,val[19],style_header5)
            ws.write(columnno,9,val[6],style_header5)
            ws.write(columnno,10,val[20],style_header5)
            ws.write(columnno,11,val[7],style_header5)
            ws.write(columnno,12,val[21],style_header5)
            ws.write(columnno,13,val[8],style_header5)
            ws.write(columnno,14,val[22],style_header5)
            ws.write(columnno,15,val[9],style_header5)
            ws.write(columnno,16,val[23],style_header5)
            ws.write(columnno,17,val[10],style_header5)
            ws.write(columnno,18,val[24],style_header5)
            ws.write(columnno,19,val[11],style_header5)
            ws.write(columnno,20,val[25],style_header5)
            ws.write(columnno,21,val[12],style_header5)
            ws.write(columnno,22,val[26],style_header5)
            ws.write(columnno,23,val[13],style_header5)
            ws.write(columnno,24,val[27],style_header5)
            ws.write(columnno,25,val[14],style_header5)
            ws.write(columnno,26,val[28],style_header5)
            ws.write(columnno,27,val[15],style_header5)
            ws.write(columnno,28,val[29],style_header5)
            ws.write(columnno,29,val[16],style_header5)

            columnno += 1
                
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        
        return self.write(cr, uid, ids, {'export_data':out,'filename':'Contractor Payment Bonus.xls'}, context=context)
