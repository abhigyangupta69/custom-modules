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

class wiz_earn_leave_report(osv.TransientModel):
    _name = 'wiz.earn.leave.report'
    
    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False
    
    _columns={
              'month':fields.many2one('holiday.list','Month'),
              'company_id': fields.many2one('res.company', 'Company'),
              'employee_id':fields.many2one('hr.employee','Employee'),
              'export_data':fields.binary('File'),
              'filename':fields.char('File Name',size=250),
              }
    
    _defaults={
               'company_id' : _get_company_id,
               }

    def print_report(self,cr,uid,ids,context=None):
        wb = Workbook()
        ws = wb.add_sheet('Earn Leave Report')
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
        borders5 = Borders()
        borders5.left = 0x02
        borders5.right = 0x02
        borders5.top = 0x02
        
        borders5.bottom = 0x02
        align5 = Alignment()
        align5.vert = Alignment.VERT_JUSTIFIED
        pattern5 = Pattern()
        pattern5.pattern = Pattern.SOLID_PATTERN
        pattern5.pattern_fore_colour =  0x16
        style_header5= XFStyle()
        style_header5.font= fnt5
        style_header5.pattern= pattern5
        style_header5.borders = borders5
        style_header5.alignment=align5
      
        ws.row(0).height=1000
        ws.col(0).width = 4000
        ws.col(1).width = 5000
        ws.col(2).width = 4000 
        ws.col(3).width = 5000 
        ws.col(4).width = 5000
        ws.col(5).width = 6500 
        ws.col(6).width = 4000 
        ws.col(7).width = 4000
        ws.col(8).width = 4000   
        
        ws.write(0,0,'Employee ID',style_header)
        ws.write(0,1,'Employee Code',style_header)
        ws.write(0,2,'Earn Date',style_header)
        ws.write(0,3,'Total Work Day',style_header)
        ws.write(0,4,'Allocation EL',style_header)
        ws.write(0,5,'Opening Earn Leave',style_header)
        ws.write(0,6,'Total EL Paid',style_header)
        ws.write(0,7,'Balance EL',style_header)        
        ws.write(0,8,'Import EL',style_header)
        
        this=self.browse(cr,uid,ids[0],context=context)
        company_id = this.company_id.id
        employee_id = this.employee_id.id
        emp_obj = self.pool.get('hr.employee')
        year=this.month.year_id.id
        balance1 = 0
        balance = 0
        import_el = 0 
        i=1
        
        if this.company_id and this.employee_id:
            list_ids = emp_obj.search(cr, uid, [('company_id','=',company_id),('id','=',employee_id),('active','=',True),('type','=','Employee')])
        elif this.company_id:
            list_ids = emp_obj.search(cr, uid, [('company_id','=',company_id),('active','=',True),('type','=','Employee')])
        
        if len(list_ids) == 0 :
            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))

        if len(list_ids) == 1 :
            query ="select spl.sinid,sum(spl.work_day),hr.earn_date,sum(spl.earned_leave),hr.earn_open,hr.id from salary_payment_line as spl left join hr_employee as hr on spl.employee_id = hr.id left join resource_resource as rr on hr.resource_id = rr.id where spl.employee_id = '"+str(list_ids[0])+"' and spl.year_id='"+str(year)+"' and rr.active = 'True' group by spl.sinid,hr.earn_date,hr.earn_open,hr.id order by spl.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
        else :
            query ="select spl.sinid,sum(spl.work_day),hr.earn_date,sum(spl.earned_leave),hr.earn_open,hr.id from salary_payment_line as spl left join hr_employee as hr on spl.employee_id = hr.id left join resource_resource as rr on hr.resource_id = rr.id where spl.employee_id in "+str(tuple(list_ids))+" and spl.year_id='"+str(year)+"' and rr.active = 'True' group by spl.sinid,hr.earn_date,hr.earn_open,hr.id order by spl.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
            
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!")) 
        
        for val in temp :
            day = format((val[1]/20),'.2f')
            b = str(day)
            c = b.split('.')
            d = c[0]
            e = c[1][0:2]
            if int(e) < 50:
                s = d + '.' + str(0)
                work_day = float(s)
            else:
                s = d + '.' + e
                t = float(s)
                work_day = math.ceil(t)
            
            if val[4] != None:
                balance1 = (work_day + val[4] - val[3])
                import_el = work_day + val[4]
            else:
                balance1 = (work_day  - val[3])
                import_el = work_day
                
            if balance1 >= 30:
                balance = 30
            else:
                balance = balance1
            
            
            ws.row(i).height=500
            ws.write(i,0,val[5],style_header2)
            ws.write(i,1,val[0],style_header2)
            ws.write(i,2,val[2],style_header2)
            ws.write(i,3,val[1],style_header2)
            ws.write(i,4,work_day,style_header2)
            ws.write(i,5,val[4],style_header2)
            ws.write(i,6,val[3],style_header2)
            ws.write(i,7,balance,style_header2)
            ws.write(i,8,import_el,style_header2)
            
            i=i+1
                
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        pf_upload_report = self.write(cr, uid, ids, {'export_data':out, 'filename':'Earn Leave Report.xls'}, context=context)
        
        return pf_upload_report
    
    
    
#                                        CONTRACTOR EARN LEAVE REPORT


class wiz_contractor_earn_leave_report(osv.TransientModel):
    _name = 'wiz.contractor.earn.leave.report'
    
    _columns={
              'month':fields.many2one('holiday.list','Month'),
              'partner_id': fields.many2one('res.partner', 'Contractor'),
              'employee_id':fields.many2one('hr.employee','Employee'),
              'export_data':fields.binary('File'),
              'filename':fields.char('File Name',size=250),
              }
    
    def print_report(self,cr,uid,ids,context=None):
        wb = Workbook()
        ws = wb.add_sheet('Contractor Earn Leave Report')
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
        borders5 = Borders()
        borders5.left = 0x02
        borders5.right = 0x02
        borders5.top = 0x02
        
        borders5.bottom = 0x02
        align5 = Alignment()
        align5.vert = Alignment.VERT_JUSTIFIED
        pattern5 = Pattern()
        pattern5.pattern = Pattern.SOLID_PATTERN
        pattern5.pattern_fore_colour =  0x16
        style_header5= XFStyle()
        style_header5.font= fnt5
        style_header5.pattern= pattern5
        style_header5.borders = borders5
        style_header5.alignment=align5
      
        ws.row(0).height=1000
        ws.col(0).width = 4000
        ws.col(1).width = 5000
        ws.col(2).width = 4000 
        ws.col(3).width = 5000 
        ws.col(4).width = 5000
        ws.col(5).width = 6500 
        ws.col(6).width = 4000 
        ws.col(7).width = 4000
        ws.col(8).width = 4000   
        
        ws.write(0,0,'Employee ID',style_header)
        ws.write(0,1,'Employee Code',style_header)
        ws.write(0,2,'Earn Date',style_header)
        ws.write(0,3,'Total Work Day',style_header)
        ws.write(0,4,'Allocation EL',style_header)
        ws.write(0,5,'Opening Earn Leave',style_header)
        ws.write(0,6,'Total EL Paid',style_header)
        ws.write(0,7,'Balance EL',style_header)        
        ws.write(0,8,'Import EL',style_header)
        
        this=self.browse(cr,uid,ids[0],context=context)
        partner_id = this.partner_id.id
        employee_id = this.employee_id.id
        emp_obj = self.pool.get('hr.employee')
        year=this.month.year_id.id
        balance1 = 0
        balance = 0
        import_el = 0 
        i=1
        
        if this.partner_id and this.employee_id:
            list_ids = emp_obj.search(cr, uid, [('partner_id','=',partner_id),('id','=',employee_id),('active','=',True),('type','=','Contractor')])
        elif this.partner_id:
            list_ids = emp_obj.search(cr, uid, [('partner_id','=',partner_id),('active','=',True),('type','=','Contractor')])
        
        if len(list_ids) == 0 :
            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))

        if len(list_ids) == 1 :
            query ="select spl.sinid,sum(spl.work_day),hr.earn_date,sum(spl.earned_leave),hr.earn_open,hr.id from salary_payment_line as spl left join hr_employee as hr on spl.employee_id = hr.id left join resource_resource as rr on hr.resource_id = rr.id where spl.employee_id = '"+str(list_ids[0])+"' and spl.year_id='"+str(year)+"' and rr.active = 'True' group by spl.sinid,hr.earn_date,hr.earn_open,hr.id order by spl.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
        else :
            query ="select spl.sinid,sum(spl.work_day),hr.earn_date,sum(spl.earned_leave),hr.earn_open,hr.id from salary_payment_line as spl left join hr_employee as hr on spl.employee_id = hr.id left join resource_resource as rr on hr.resource_id = rr.id where spl.employee_id in "+str(tuple(list_ids))+" and spl.year_id='"+str(year)+"' and rr.active = 'True' group by spl.sinid,hr.earn_date,hr.earn_open,hr.id order by spl.sinid"                           
            cr.execute(query)
            temp = cr.fetchall()
            
        if not temp :
            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!")) 
        
        for val in temp :
            day = format((val[1]/20),'.2f')
            b = str(day)
            c = b.split('.')
            d = c[0]
            e = c[1][0:2]
            if int(e) < 50:
                s = d + '.' + str(0)
                work_day = float(s)
            else:
                s = d + '.' + e
                t = float(s)
                work_day = math.ceil(t)
            
            if val[4] != None:
                balance1 = (work_day + val[4] - val[3])
                import_el = work_day + val[4]
            else:
                balance1 = (work_day  - val[3])
                import_el = work_day
                
            if balance1 >= 30:
                balance = 30
            else:
                balance = balance1
            
            
            ws.row(i).height=500
            ws.write(i,0,val[5],style_header2)
            ws.write(i,1,val[0],style_header2)
            ws.write(i,2,val[2],style_header2)
            ws.write(i,3,val[1],style_header2)
            ws.write(i,4,work_day,style_header2)
            ws.write(i,5,val[4],style_header2)
            ws.write(i,6,val[3],style_header2)
            ws.write(i,7,balance,style_header2)
            ws.write(i,8,import_el,style_header2)
            
            i=i+1
                
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        earn_leave_report = self.write(cr, uid, ids, {'export_data':out, 'filename':'Contractor Earn Leave Report.xls'}, context=context)
        
        return earn_leave_report    