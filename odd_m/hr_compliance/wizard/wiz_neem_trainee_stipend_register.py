from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp import tools
import time
from datetime import datetime , timedelta
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import cStringIO
import base64
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, Alignment,  easyxf
import calendar
from dateutil.relativedelta import relativedelta
import psycopg2


class wiz_neem_trainee_stipend_register(osv.TransientModel):
    _name = 'wiz.neem.trainee.stipend.register'


    _columns = {
                'month_id':fields.many2one('holiday.list', 'Month'),
                'from_date':fields.date('From Date'),
                'till_date':fields.date('Till Date'),
                'partner_id': fields.many2one('res.partner', 'Contractor'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'export_data':fields.binary('File',readonly=True),
                'filename':fields.char('File Name',size=250,readonly=True),
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
        
        

    
    
    def neem_trainee_stipend_register_report(self,cr,uid,ids,context=None):
      
        
        #Define the font attributes for header
        fnt = Font()
        fnt.name = 'Ubuntu Medium'
        fnt.size=15
        fnt.Style= 'Regular'
        
        content_fnt = Font()
        content_fnt.name ='Ubuntu Medium'
        content_fnt.size=15
        content_fnt.Style= 'Regular'
        align_content = Alignment()
        align_content.horz= Alignment.HORZ_CENTER
     
        borders = Borders()
        
        #The text should be centrally aligned
        align = Alignment()
        align.horz = Alignment.HORZ_CENTER
        align.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern = Pattern()

        #apply the above settings to the row(0) header
        style_header= XFStyle()
        style_header.font= fnt
        style_header.pattern= pattern
        style_header.borders = borders
        style_header.alignment=align    
        
        #Define the font attributes for header
        fnt1 = Font()
        fnt1.name = 'Arial'
        fnt1.size=15
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
        
        
        #Define the font attributes for header
        fnt2 = Font()
        fnt2.name = 'Ubuntu Medium'
        fnt2.size =10
        fnt2.style='Regular'
        
        content_fnt2 = Font()
        content_fnt2.name ='Ubuntu Medium'
        content_fnt2.style='Regular'
        align_content2 = Alignment()
        align_content2.horz= Alignment.HORZ_LEFT
     
        borders2 = Borders()
        borders2.left = 0x0
        borders2.right = 0x0
        borders2.top = 0x0
        borders2.bottom = 0x0
        
        #The text should be centrally aligned
        align2 = Alignment()
        align2.horz = Alignment.HORZ_CENTER
        align2.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern2 = Pattern()

        #apply the above settings to the row(0) header
        style_header2= XFStyle()
        style_header2.font= fnt2
        style_header2.pattern= pattern2
        style_header2.borders = borders2
        style_header2.alignment=align2  
         
        wb = Workbook()
        ws = wb.add_sheet('Neem Trainee Stipend Register')
#        style_pass = xlwt.easyxf('pattern: pattern solid, Font.name:Arial ,Bold: True, fore_colour black;')
#        ws.row(0).height=500

        ws.col(0).width = 1800
        ws.col(1).width = 6000
        ws.col(2).width = 6000
        ws.col(3).width = 6000
        ws.col(4).width = 6000
        ws.col(5).width = 7200
        ws.col(6).width = 6000
        ws.col(7).width = 7200
        ws.col(8).width = 6000
        ws.col(9).width = 6000
        ws.col(10).width = 2200
        ws.col(11).width = 2200
        ws.col(12).width = 2200
        ws.col(13).width = 2200
        ws.col(14).width = 2200
        ws.col(15).width = 2200
        ws.col(16).width = 2200
        ws.col(17).width = 2500
        ws.col(18).width = 2500
        ws.col(19).width = 3200
        ws.col(20).width = 2500
        ws.col(21).width = 2500
        ws.col(22).width = 2500
        ws.col(23).width = 3500
        
        i = 3
        
        this = self.browse(cr, uid, ids)
        from_date = this.from_date
        from_date1 = datetime.strptime(from_date, "%Y-%m-%d")
        from_date1 = from_date1.strftime('%d-%m-%Y')
        till_date = this.till_date
        till_date1 = datetime.strptime(till_date, "%Y-%m-%d")
        till_date1 = till_date1.strftime('%d-%m-%Y')
        

        partner_id = this.partner_id
        emp_id = this.employee_id

        ws.write_merge(0, 1, 8, 12, 'NEEM  TRAINEE  STIPEND  REGISTER  FOR' + this.month_id.name +
                                    ' ( ' + from_date1 + ' to ' + till_date1 + ' ) ' , style_header)
        
        
        ws.write(i, 0,  'S.No.', style_header1)
        ws.write(i, 1,  'Emp Code', style_header1)
        ws.write(i, 2, 'Punch Code', style_header1) 
        ws.write(i, 3,  'Emp Name', style_header1)
        ws.write(i, 4,  'Department', style_header1)
        ws.write(i, 5,  'Designation', style_header1)
        ws.write(i, 6,  'DOJ', style_header1)
        ws.write(i, 7,  'Bank Name', style_header1)
        ws.write(i, 8,  'Bank Acc. Number', style_header1)
        ws.write(i, 9,  'IFS Code', style_header1)
        ws.write(i, 10,  'Stipend \n Rate', style_header1)
        ws.write(i, 11, 'Total \n Days', style_header1)
        ws.write(i, 12, 'Working \n Days', style_header1)
        ws.write(i, 13, 'Casual \n Leave', style_header1)
        ws.write(i, 14, 'Earn \n Leave', style_header1)
        ws.write(i, 15, 'Holiday', style_header1)
        ws.write(i, 16, 'Absent \n Days', style_header1)
        ws.write(i, 17, 'Payable \n Days', style_header1)
        ws.write(i, 18, 'Stipend \n Payable', style_header1)
        ws.write(i, 19, 'Performance \n Incentive', style_header1)
        ws.write(i, 20, 'Total \n Earnings', style_header1)
        ws.write(i, 21, 'Deduction \n If Any', style_header1)
        ws.write(i, 22, 'Net \n Payable', style_header1)
        ws.write(i, 23, 'Signature \n Thumb \n Impression', style_header1) 
        
        
        ws.row(23).height=500        
        ws.row(22).height=500
        ws.row(21).height=500     
        ws.row(20).height=500
        ws.row(19).height=500   
        ws.row(18).height=500
        ws.row(17).height=500 
        ws.row(16).height=500
        ws.row(15).height=500   
        ws.row(14).height=500
        ws.row(13).height=500  
        ws.row(12).height=500
        ws.row(11).height=500   
        ws.row(10).height=500
        ws.row(9).height=500   
        ws.row(8).height=500
        ws.row(7).height=500
        ws.row(6).height=500
        ws.row(4).height=500
        ws.row(4).height=500
        ws.row(3).height=500
        ws.row(2).height=500
        ws.row(1).height=500
        ws.row(0).height=500
        

        i += 1
        emp_obj = self.pool.get('hr.employee')
        if this.employee_id:
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', partner_id.id),('id', '=', emp_id.id),('active','=',True),
                                                ('doj','<=',till_date),('employment_type','=','Trainee')])

        else:
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', partner_id.id),('active','=',True),
                                                ('doj','<=',till_date),('employment_type','=','Trainee')])

        if not list_ids:
            raise osv.except_osv(_('Warning !'), _("No Record Found !!!"))

        i1 = 0
        
        for emp in list_ids:
            
            i1 += 1
            bank_name = ''
            acc_no = ''
            ifs_code = ''
            month_days = work_day = casual_leave = earned_leave = holiday = absent_days = days = stipend_pay = other_earns = total_amt = deduction = net_pay = 0.0
            emp_browse = emp_obj.browse(cr, uid, emp)
            sinid = emp_browse.sinid
            name = emp_browse.name
            dept = emp_browse.department_id.name
            desg = emp_browse.job_id.name
            doj = datetime.strptime(emp_browse.doj, "%Y-%m-%d")
            doj = doj.strftime('%d-%m-%Y')
            salary = emp_browse.total_salary
            punch_code = emp_browse.paycode
            query1 = "select bank_name,id_no,ifsc_code from verification where employee_id='"+str(emp)+"' " \
                     "and proof_id = 'Bank_ Account_ No' "
            cr.execute(query1)
            temp1 = cr.fetchall()
            bank_name= ''
            if temp1:
                bank_name = temp1[0][0]
                acc_no = temp1[0][1]
                ifs_code = self.pool.get('res.bank').browse(cr, uid, temp1[0][2]).bic

            if bank_name :
                paid_msg='Paid In Bank'
            else:
                paid_msg=''    
                
            ws.write(i, 0, i1, style_header)
            ws.write(i, 1, sinid, style_header)
            ws.write(i, 2, punch_code, style_header)
            ws.write(i, 3, name, style_header)
            ws.write(i, 4, dept, style_header)
            ws.write(i, 5, desg, style_header)
            ws.write(i, 6, doj, style_header)
            ws.write(i, 7, bank_name, style_header)
            ws.write(i, 8, acc_no, style_header)
            ws.write(i, 9, ifs_code, style_header)
            ws.write(i, 10, salary, style_header)
            sal_line_search = self.pool.get('salary.payment.line').search(cr, uid, [('employee_id','=',emp),('month','=',this.month_id.month),
                                                                             ('year_id','=',this.month_id.year_id.id)])
            if sal_line_search:
                sal_line = self.pool.get('salary.payment.line').browse(cr, uid, sal_line_search[0])
                month_days = sal_line.month_days
                work_day = sal_line.work_day + sal_line.factory_work
                casual_leave = sal_line.casual_leave
                earned_leave = sal_line.earned_leave
                holiday = sal_line.week_leave + sal_line.holiday_leave
                absent_days = sal_line.month_days - sal_line.days
                days = sal_line.days
                stipend_pay = sal_line.days_amount + sal_line.other_salary_amount
                other_earns = sal_line.overtime_amount + sal_line.sun_overtime_amount
                total_amt = stipend_pay + other_earns
                deduction = sal_line.kharcha + sal_line.loan
                net_pay = total_amt - deduction

            
            ws.write(i, 11, month_days, style_header)
            ws.write(i, 12, work_day, style_header)
            ws.write(i, 13, casual_leave, style_header)
            ws.write(i, 14, earned_leave, style_header)
            ws.write(i, 15, holiday, style_header)
            ws.write(i, 16, absent_days, style_header)
            ws.write(i, 17, days, style_header)
            ws.write(i, 18, stipend_pay, style_header)
            ws.write(i, 19, other_earns, style_header)
            ws.write(i, 20, total_amt, style_header)
            ws.write(i, 21, deduction, style_header)
            ws.write(i, 22, net_pay, style_header)
            ws.write(i, 23, paid_msg, style_header)
            
            ws.row(i).height=500
            i += 1

        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        return self.write(cr, uid, ids, {'export_data':out, 'filename':'Neem Trainee Stipend Register.xls'}, context=context)
