from openerp import addons
import logging
from itertools import groupby
from operator import itemgetter
from openerp.osv import fields, osv
from openerp import tools
import time
import math
from datetime import datetime , timedelta
_logger = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp
import base64, urllib
import os
import re
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import cStringIO
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, Alignment,  easyxf
from PIL import Image
import csv
from openerp.tools import amount_to_text_en
from dateutil import rrule
import calendar
from dateutil.relativedelta import relativedelta
import dateutil.relativedelta as relativedelta
import dateutil.rrule as rrule


class wiz_performance_register(osv.TransientModel):
    _name = 'wiz.performance.register'

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
                'export_data':fields.binary('File',readonly=True),
                'filename':fields.char('File Name',size=250,readonly=True),
                'user_id':fields.many2one('res.users','User Id'),
                'month_id':fields.many2one('holiday.list', 'Month'),
                'seq_from': fields.integer('From Seq.'),
                'seq_to': fields.integer('To Seq.'),

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
    
    
    def performance_register_report(self,cr,uid,ids,context=None):

    #Define the font attributes for header
        fnt = Font()
        fnt.name = 'Arial Black'
        fnt.size=10
        fnt.Style= 'Regular'
        
        content_fnt = Font()
        content_fnt.name ='Arial Black'
        content_fnt.size=10
        content_fnt.Style= 'Regular'
        align_content = Alignment()
        align_content.horz= Alignment.HORZ_CENTER
     
        borders = Borders()
        
        #The text should be centrally aligned
        align = Alignment()
        align.horz = Alignment.HORZ_LEFT
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
        fnt1.name = 'Ubuntu Medium'
        fnt1.size =10
        fnt1.style='Regular'
        
        content_fnt1 = Font()
        content_fnt1.name ='Ubuntu Medium'
        content_fnt1.style='Regular'
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_LEFT
     
        borders1 = Borders()
        borders1.left = 0x00
        borders1.right = 0x00
        borders1.top = 0x03
        borders1.bottom = 0x03
        
        #The text should be centrally aligned
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern1 = Pattern()

        #apply the above settings to the row(0) header
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
        
    #Define the font attributes for header
        fnt4 = Font()
        fnt4.name = 'Arial'
        fnt4.size ='10'
        fnt4.style='Regular'
        
        content_fnt4 = Font()
        content_fnt4.name ='Arial'
        content_fnt4.style='Regular'
        align_content4 = Alignment()
        align_content4.horz= Alignment.HORZ_LEFT
     
        borders4 = Borders()
        borders4.left = 0x01
        borders4.right = 0x01
        
        #The text should be centrally aligned
        align4 = Alignment()
        align4.horz = Alignment.HORZ_LEFT
        align4.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern4 = Pattern()

        #apply the above settings to the row(0) header
        style_header4= XFStyle()
        style_header4.font= fnt4
        style_header4.pattern= pattern4
        style_header4.borders = borders4
        style_header4.alignment=align4
                
        wb = Workbook()
        ws = wb.add_sheet('Performance Register')
#        style_pass = xlwt.easyxf('pattern: pattern solid, Font.name:Arial ,Bold: True, fore_colour black;')
#        ws.row(0).height=500

        ws.col(1).width = 2200
        ws.col(2).width = 2200
        ws.col(3).width = 2200
        ws.col(4).width = 2500
        ws.col(5).width = 2200
        ws.col(6).width = 2200
        ws.col(7).width = 2200
        ws.col(8).width = 2200
        ws.col(9).width = 2200
        ws.col(10).width = 2200
        ws.col(11).width = 2200
        ws.col(12).width = 2200
        ws.col(13).width = 2200
        ws.col(14).width = 2200
        ws.col(15).width = 2200
        ws.col(16).width = 2200
        ws.col(17).width = 2200
        ws.col(18).width = 2200
        ws.col(19).width = 2200
        ws.col(20).width = 2200
        ws.col(21).width = 2200
        ws.col(22).width = 2200
        ws.col(23).width = 2200
        ws.col(24).width = 2200
        ws.col(25).width = 2200
        ws.col(26).width = 2200
        ws.col(27).width = 2200
        ws.col(28).width = 2200
        ws.col(29).width = 2200
        ws.col(30).width = 2200

        this = self.browse(cr,uid,ids)
        if this.seq_from > this.seq_to:
            raise osv.except_osv(_('Warning !'), _("Sequence From cannot be greater than Sequence To !!!"))

        emp_id = this.employee_id.id
        department_id =this.department_id.id
        company_id = this.company_id.id
        from_date = datetime.strptime(this.from_date,"%Y-%m-%d")
        var1 = from_date
        from_date = from_date.strftime("%d-%m-%Y")
        
        till_date = datetime.strptime(this.till_date,"%Y-%m-%d")
        var2 = till_date
        till_date = till_date.strftime("%d-%m-%Y")
        
        var = var2 - var1
        var = str(var)
        var = var.split(' ')
        var = int(int(var[0])/2) + 1
        if this.company_id and not this.department_id:
            ws.write_merge(1,1,var-3,var+3, this.company_id.name,style_header2)
        elif this.department_id :
            ws.write_merge(1,1,var-4,var+4, this.department_id.name + ' , ' + this.company_id.name,style_header2)
        else :
            ws.write_merge(1,1,var-3,var+3, '  ' ,style_header2)

        ws.write_merge(3,3,var-3,var+3, 'Performance Register from ' + from_date + ' to ' + till_date ,style_header2)

        emp_obj = self.pool.get('hr.employee')
        if this.employee_id and this.department_id and this.company_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('department_id', '=', department_id),('active','=',True),('company_id','=',company_id),('doj','<=',var2),('type','=','Employee')])
        elif this.employee_id and this.company_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('active','=',True),('company_id','=',company_id),('doj','<=',var2),('type','=','Employee')])
        elif this.department_id and this.company_id:
            list_ids = emp_obj.search(cr, uid, [('department_id', '=', department_id),('active','=',True),('company_id','=',company_id),('doj','<=',var2),('type','=','Employee')])
        elif this.company_id:
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('company_id','=',company_id),('doj','<=',var2),('type','=','Employee')])
        elif this.employee_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', emp_id),('active','=',True),('doj','<=',var2),('type','=','Employee')])
        elif this.department_id:
            raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
        else:
            list_ids = emp_obj.search(cr, uid, [('active','=',True),('doj','<=',var2),('type','=','Employee')])

        if this.seq_from == 0 and this.seq_to == 0 and len(list_ids) > 300:
            raise osv.except_osv(_('Warning !'), _("More than 300 employee cannot be processed !!!"))
        if (this.seq_to - this.seq_from) > 300:
            raise osv.except_osv(_('Warning !'), _("Range cannot be greater than 300 !!!"))
        if this.seq_from != 0 and this.seq_to != 0:
            list_ids = list_ids[int(this.seq_from - 1):this.seq_to]

        r1 = 5
        r2 = 6
        r3 = 8
        r4 = 10
        r5 = 11
#        r6 = 12
        r7 = 13
        r8 = 14
        r9 = 15
        r10 = 16
        i1 = 0
#  	list_ids = list_ids[750:1500]
	
        print"list_ids ================",len(list_ids)
        for emp in list_ids :
            i = 0
            i1 += 1
            print"Performance Register emp =============================================================>",emp,i1
            p_count = 0
            a_count = 0
            h_count = 0
            wo_count = 0
            l_count = 0
            total_ot = 0
            total_ot1 = 0
            total_hrs = 0
            total_hrs1 = 0
            
            if i1 >= 1 :
                if (i1-1)%5 == 0  and i1 != 1 :
                    r1 = r1 + 23
                    r2 = r2 + 23
                    r3 = r3 + 23
                    r4 = r4 + 23
                    r5 = r5 + 23
#                    r6 = r6 + 23
                    r7 = r7 + 23
                    r8 = r8 + 23
                    r9 = r9 + 23
                    r10 = r10 + 23 
                    
                    if this.company_id and not this.department_id:
                        ws.write_merge(r1-4,r1-4,var-3,var+3, this.company_id.name,style_header2)
                    elif this.department_id :
                        ws.write_merge(r1-4,r1-4,var-4,var+4, this.department_id.name + ' , ' + this.company_id.name,style_header2)
                    else :
                        ws.write_merge(r1-4,r1-4,var-3,var+3, '  ' ,style_header2)
                    ws.write_merge(r1-2,r1-2,var-3,var+3, 'Performance Register from ' + from_date + ' to ' + till_date, style_header2)
                else :
                    if i1 > 1 :
                        r1 = r1 + 14
                        r2 = r2 + 14
                        r3 = r3 + 14
                        r4 = r4 + 14
                        r5 = r5 + 14
#                        r6 = r6 + 14
                        r7 = r7 + 14
                        r8 = r8 + 14
                        r9 = r9 + 14
                        r10 = r10 + 14
                                    
            ws.write(r4,0, 'In Time', style_header2)
            ws.write(r5,0, 'Out Time', style_header2)
#            ws.write(r6,0, 'Late', style_header2)
            ws.write(r7,0, 'Hrs. Wkd.', style_header2)
            ws.write(r8,0, 'Over Time', style_header2)
            ws.write(r9,0, 'Status', style_header2)
            ws.write(r10,0, 'Shift Att.', style_header2)                
            
            emp_browse = emp_obj.browse(cr, uid, emp)
            doj = emp_browse.doj
            ws.write(r3,0, 'Card No :', style_header2)
            ws.write(r3,1, emp_browse.sinid, style_header2)
            ws.write(r3,3, 'Name :', style_header2)
            ws.write_merge(r3,r3,4,9, emp_browse.name, style_header2)
       
            ws.write(r1,0, '', style_header1)
            ws.write(r2,0, '', style_header1)

            start_dat = datetime.strptime(from_date,'%d-%m-%Y')
            end_dat = datetime.strptime(till_date,'%d-%m-%Y')
            s_date = start_dat.strftime('%Y-%m-%d')
            tm_tuple = datetime.strptime(s_date,'%Y-%m-%d').timetuple()
            month1 = tm_tuple.tm_mon
            year1 = tm_tuple.tm_year
            start1 = tm_tuple.tm_mday
            e_date = end_dat.strftime('%Y-%m-%d')
            tm_tuple1 = datetime.strptime(e_date,'%Y-%m-%d').timetuple()
            end1 = tm_tuple1.tm_mday
            
            before=datetime(year1,month1,start1)
            after=datetime(year1,month1,end1)
            if emp_browse.week.upper()[0:2]=='SU':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.SU,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True) 
            elif emp_browse.week.upper()[0:2]=='MO':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.MO,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='TU':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.TU,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='WE':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.WE,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='TH':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.TH,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='FR':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.FR,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='SA':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.SA,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)

            for val_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(from_date,'%d-%m-%Y'),until=datetime.strptime(till_date,'%d-%m-%Y')):
                val_date_str = val_date.strftime('%Y-%m-%d')
                q1 = cr.execute("select sline.from_time from attendance_shift_line as sline left join attendance_shift as shift on (sline.shift_id=shift.id) "
                                "left join hr_shift_line as hr_sline on (hr_sline.shift_id=shift.id) where hr_sline.employee_id='"+str(emp)+"' ")
                t1 = cr.fetchall()
                
                val_from_date_hrs = str(t1[0][0])
                val_from_date_hrs_lst = val_from_date_hrs.split('.')
                val_from_date_hrs_str1 = val_from_date_hrs_lst[0]
                if len(val_from_date_hrs_str1) == 1 :
                    val_from_date_hrs_str1 = '0' + val_from_date_hrs_str1

                val_from_date_hrs_str2 = str(int(int(val_from_date_hrs_lst[1]) * 60)/100)
                if len(val_from_date_hrs_str2) == 1 :
                    val_from_date_hrs_str2 = '0' + val_from_date_hrs_str2
                
                val_from_date_hrs = str(val_from_date_hrs)
                if len(val_from_date_hrs) == 1 :
                    val_from_date_hrs = '0' + val_from_date_hrs
                val_from_date_str = val_date_str + ' ' + val_from_date_hrs_str1 + ':' + val_from_date_hrs_str2 + ':' + '00'
#                val_from_date_str = val_date_str + ' 00:00:00'
                val_from_date_str = datetime.strptime(val_from_date_str,"%Y-%m-%d %H:%M:%S")
                val_from_date_str = val_from_date_str - timedelta(hours=5,minutes=30)
# Here we have to minus 30 minutes from employee start shift .
                val_from_date_str11 = val_from_date_str - timedelta(hours=0,minutes=30)
                val_from_date_str = val_from_date_str11.strftime("%Y-%m-%d %H:%M:%S")
                
#                val_till_date_str = val_date_str + ' 23:59:59'
#                val_till_date_str = datetime.strptime(val_till_date_str,"%Y-%m-%d %H:%M:%S")
                val_till_date_str = val_from_date_str11 + timedelta(hours=22,minutes=0)
                val_till_date_str = val_till_date_str.strftime("%Y-%m-%d %H:%M:%S")
                
                i += 1
                date = val_date.strftime('%d')
                week_day = val_date.strftime('%a')
                
                ws.write(r1,i, date, style_header1)
                ws.write(r2,i, week_day, style_header1)
                
                # hr_atten_search = self.pool.get('hr.attendance').search(cr,uid,[('search_date','>=',val_date_str),('search_date','<=',val_date_str),('employee_id','=',emp)])

                q11 = cr.execute("select name from hr_attendance where search_date >= '"+str(val_date_str)+"' and search_date <='"+str(val_date_str)+"' and employee_id = '"+str(emp)+"' ")
                t11 = cr.fetchall()

                if len(t11) == 1:
                    raise osv.except_osv(_('Warning !!!!'),_("Only 1 Punch Found For Employee [ " +(emp_browse.sinid)+" ] " "on Date %s" % (val_date_str)))
                
                if t11 :
                    hr_atten_lst = []
                    hr_atten_lst1 = []
                    for hr_atten_id in t11 :
                        # hr_atten_browse = self.pool.get('hr.attendance').browse(cr,uid,hr_atten_id).name
                        attendance = datetime.strptime(hr_atten_id[0],"%Y-%m-%d %H:%M:%S")
                        attendance = attendance + timedelta(hours=5,minutes=30)
#                        attendance = attendance.strftime("%d-%m-%Y %H:%M:%S")
                        hr_atten_lst1.append(attendance)
                    hr_atten_lst1.sort()
                    
                    for val in hr_atten_lst1 :
                        attendance = val.strftime("%d-%m-%Y %H:%M:%S")
                        hr_atten_lst.append(attendance)
                    
                    q1 = cr.execute("select shift.shift_name,sline.from_time,sline.working_time,sline.lunch_time from attendance_shift_line as sline left join attendance_shift as shift on (sline.shift_id=shift.id) "
                                    "left join hr_shift_line as hr_sline on (hr_sline.shift_id=shift.id) where hr_sline.employee_id='"+str(emp)+"' and hr_sline.name<='"+str(val_date)+"' order by hr_sline.name desc limit 1 ")
                    t1 = cr.fetchall()
                    if t1:
                        shift = t1[0][0]
                    else:
                        raise osv.except_osv(_('Warning !'), _("Shift is Missing for Employee %s on Date %s" %(emp_browse.sinid,val_date_str)))
		            
                    in_punch = hr_atten_lst[0]
                    out_punch = hr_atten_lst[1]
                    
                    in_punch = datetime.strptime(in_punch,"%d-%m-%Y %H:%M:%S")
                    out_punch = datetime.strptime(out_punch,"%d-%m-%Y %H:%M:%S")
                    total_time_diff = out_punch - in_punch   
                    if len(str(total_time_diff)) > 8:
                        raise osv.except_osv(_('Warning !'), _("More than 15 Hrs found for Employee %s on Date %s" %(emp_browse.sinid,val_date_str)))
                    total_time_diff_lst = str(total_time_diff).split(':')
                    total_time_diff_min = (int(total_time_diff_lst[0])*60) + int(total_time_diff_lst[1])
                                                                
                    in_time = in_punch.strftime('%H:%M')
                    out_time = out_punch.strftime('%H:%M')
                    
                    t11_lst = str(t1[0][1]).split('.')
                    if len(t11_lst[0]) == 1 :
                        t11_hrs = '0' + t11_lst[0]
                    else :
                        t11_hrs = t11_lst[0]
                    t11_min = int((int(t11_lst[1])*60)/100)
                    if len(str(t11_min)) == 1 :
                        t11_min = '0' + str(t11_min)
                    else :
                        t11_min = str(t11_min)

                    shift_in_time_date_str = val_date_str + ' ' + t11_hrs + ':' + t11_min + ':' + '00'
                    shift_in_time_date = datetime.strptime(shift_in_time_date_str,"%Y-%m-%d %H:%M:%S")
                    shift_in_time_date_str = datetime.strftime(shift_in_time_date,"%d-%m-%Y %H:%M:%S")
                    shift_in_time_date = datetime.strptime(shift_in_time_date_str,"%d-%m-%Y %H:%M:%S")
                    
#                    if shift_in_time_date < hr_atten_lst1[0]:
#                        late_time = hr_atten_lst1[0] - shift_in_time_date
#                        late_time = str(late_time)
#                        late_time_lst = late_time.split(':')
#                        late_time_hrs = int(late_time_lst[0])*60
#                        late_time_min = int(late_time_lst[1])
#                        late = late_time_hrs + late_time_min
#                    else :
#                        late = 0
                    
#                    t11 = str(t1[0][1])
#                    t11 = t11.split('.')
#                    t1_min = (int(t11[0])*60) + int((int(t11[1])*60)/100)
                    in_time_min = in_time.split(':')
                    in_time_min = (int(in_time_min[0])*60) + int(in_time_min[1])
#                    
                    
                    out_time_min = out_time.split(':')
                    out_time_min = (int(out_time_min[0])*60) + int(out_time_min[1])

#                    if in_time_min > t1_min :
#                        late = in_time_min - t1_min
#                    else :
#                        late = 0 
                    
                    interval = t1[0][3]
#                    lunch_start = datetime.strptime('13:00',"%H:%M")
#                    lunch_start = lunch_start.strftime('%H:%M')
#                    
#                    lunch_end = datetime.strptime('13:45',"%H:%M")
#                    lunch_end = lunch_end.strftime('%H:%M')
#                                        
#                    if (in_time < lunch_start) and (out_time >= lunch_end) and t1[0][2] > 8 :
#                        interval = 45
#                    elif (in_time < lunch_start) and (out_time < lunch_start) and t1[0][2] > 8 :
#                        interval = 0
#                    elif (in_time < lunch_start) and (out_time < lunch_end) and t1[0][2] > 8 :
#                        interval = out_time_min - (13*60)
#                    elif (in_time >= lunch_end) and t1[0][2] > 8 :
#                        interval = 0
#                    elif (in_time > lunch_start) and (in_time <= lunch_end) and t1[0][2] > 8 :
#                        interval = ((13*60)+45) - in_time_min
                    
#                    if shift == 'GRD B' :
#                        time_diff = working_time_grd_b
#                    else :
                    
                    time_diff = total_time_diff_min - interval

                    if time_diff > 900:
                        raise osv.except_osv(_('Warning !'), _("More than 15 Hrs found for Employee %s on Date %s" %(emp_browse.sinid,val_date_str)))
                    total_hrs1 +=  time_diff
                    
                    working_hrs = float(time_diff)/60
                    working_hrs = str(working_hrs)
                    working_hrs = working_hrs.split('.')
                    working_hrs = working_hrs[0]
                    working_min = time_diff%60
                    working_min = str(working_min)
                    if len(working_min) == 1 :
                        working_min = '0' + working_min
                    
                    working_time = working_hrs + '.' + working_min                
                
                    ws.write(r4,i, in_time, style_header3)
                    ws.write(r5,i, out_time, style_header3)
#                    ws.write(r6,i, late, style_header3)
                    ws.write(r7,i, working_time, style_header3)
                    ws.write(r10,i, shift, style_header3)
            
                else :
                    if doj > val_date_str :
                        ws.write(r4,i, 'N/A', style_header3)
                        ws.write(r5,i, 'N/A', style_header3)
#                        ws.write(r6,i, 'N/A', style_header3)
                        ws.write(r7,i, 'N/A', style_header3)
                        ws.write(r10,i, 'N/A', style_header3)
                    else :
                        ws.write(r4,i, '', style_header3)
                        ws.write(r5,i, '', style_header3)
#                        ws.write(r6,i, '', style_header3)
                        ws.write(r7,i, '', style_header3)
                        ws.write(r10,i, '', style_header3)

                if doj > val_date_str :
                    ws.write(r8,i,'N/A' , style_header3)
                    ws.write(r9,i, 'N/A', style_header3)
                
                else :
                    q2 = cr.execute("select over_time,working from attendance_timing where employee_id='"+str(emp)+"' and name='"+str(val_date)+"'  ")
                    t2 = cr.fetchall()
                    if t2 :
                        ot_hrs = float(t2[0][0])/60
                        ot_hrs = str(ot_hrs)
                        ot_hrs = ot_hrs.split('.')
                        ot_hrs = ot_hrs[0]
                        
                        ot_min = (t2[0][0])%60
                        ot_min = int(ot_min)
                        ot_min = str(ot_min)
                        if len(ot_min) == 1 :
                            ot_min = '0' + ot_min
                        over_time = ot_hrs + '.' + ot_min                
                        
                        status = t2[0][1]
                        if status == 'A' :
                            a_count += 1
                        elif status == 'POW' :
                            wo_count += 1
                        elif status == 'POH' :
                            h_count += 1
                        else :
                            p_count += 1
                        total_ot1 += t2[0][0]
                        
                        ws.write(r8,i,over_time , style_header3)
                        ws.write(r9,i, status, style_header3)
                        
                    if len(t2) == 0 and emp_browse.week != 'Sunday':
                        t3 = []
                        for vall in week_off_lst:
                            if val_date == vall:
                                over_time = ''
                                t3.append(emp_browse.week)
                                status = 'WO'
                                wo_count += 1
                                ws.write(r8,i,over_time , style_header3)
                                ws.write(r9,i, status, style_header3) 
                                
                        if len(t3) == 0:
                            q3 = cr.execute("select week from holiday_list_lines where leave_date='"+str(val_date)+"'  ")
                            t3 = cr.fetchall()
                            if t3 :
                                t3 = t3[0][0]
                                over_time = ''
                                if t3 != 'Sunday' and t3 != emp_browse.week :
                                    status = 'HLD'
                                    h_count += 1
                                    ws.write(r8,i,over_time , style_header3)
                                    ws.write(r9,i, status, style_header3) 
                        
                    elif len(t2) == 0 and emp_browse.week == 'Sunday':
                        q3 = cr.execute("select week from holiday_list_lines where leave_date='"+str(val_date)+"'  ")
                        t3 = cr.fetchall()
                        if t3 :
                            t3 = t3[0][0]
                            over_time = ''
                            if t3 == 'Sunday' :
                                status = 'WO'
                                wo_count += 1
                            else :
                                status = 'HLD'
                                h_count += 1
                            ws.write(r8,i,over_time , style_header3)
                            ws.write(r9,i, status, style_header3) 
                            
                    if len(t2) == 0 and len(t3) == 0 : 
                        q4 = cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp)+"' and state='validate' and type='remove' ")
                        t4 = cr.fetchall()
                        status = ''
                        if t4 :
                            for val1 in t4 :
                                for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                    if leave_date == val_date and val1[2] != 'Factory Work':
                                        over_time = ''
                                        if val1[2] == 'Earned Leaves' : status = 'EL'
                                        elif val1[2] == 'Compensatory Days' : status = 'COM'
                                        elif val1[2][0:4] == 'Sick' : status = 'SL'
                                        elif val1[2][0:4] == 'Casu' : status = 'CL'
                                        l_count += 1
                                        ws.write(r8,i,over_time , style_header3)
                                        ws.write(r9,i, status, style_header3)   
                                    elif leave_date == val_date and val1[2] == 'Factory Work':
                                        over_time = ''
                                        p_count += 1
                                        status = 'FW'
                                        ws.write(r8,i,over_time , style_header3)
                                        ws.write(r9,i, status, style_header3)   
                                            
                        if status == '' :
                            status = 'A'
                            over_time = ''
                            a_count += 1
                            ws.write(r8,i,over_time , style_header3)
                            ws.write(r9,i, status, style_header3)

            total_ot_hrs = float(total_ot1)/60
            total_ot_hrs = str(total_ot_hrs)
            total_ot_hrs = total_ot_hrs.split('.')
            total_ot_hrs = total_ot_hrs[0]
            total_ot_min = (total_ot1)%60
            total_ot_min = int(total_ot_min)
            total_ot_min = str(total_ot_min)
            if len(total_ot_min) == 1 :
                total_ot_min = '0' + total_ot_min
            
            total_ot = total_ot_hrs + '.' + total_ot_min   
            
            total_working_hrs = float(total_hrs1)/60
            total_working_hrs = str(total_working_hrs)
            total_working_hrs = total_working_hrs.split('.')
            total_working_hrs = total_working_hrs[0]
            total_working_min = total_hrs1%60
            total_working_min = str(total_working_min)
            if len(total_working_min) == 1 :
                total_working_min = '0' + total_working_min
            
            total_hrs = total_working_hrs + '.' + total_working_min    

            ws.write(r3,11, 'Present:', style_header2)
            ws.write(r3,12, p_count, style_header2)
            ws.write(r3,13, 'Absent:', style_header2)
            ws.write(r3,14, a_count, style_header2)
            ws.write(r3,15, 'Holiday:', style_header2)
            ws.write(r3,16, h_count, style_header2)  
            ws.write(r3,17, 'Wk Off:', style_header2)
            ws.write(r3,18, wo_count, style_header2)     
            ws.write(r3,19, 'Leave :', style_header2)
            ws.write(r3,20, l_count, style_header2)     
            ws.write(r3,21, 'Hrs Wkd:', style_header2)
            ws.write(r3,22, total_hrs, style_header2)     
            ws.write(r3,23, 'OT:', style_header2)
            ws.write(r3,24, total_ot, style_header2)     
        
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        return self.write(cr, uid, ids, {'export_data':out, 'filename':'Performance Register.xls'}, context=context)
    


#                                 CONTRACTOR PERFORMANCE REGISTER

class wiz_contractor_performance_register(osv.TransientModel):
    _name = 'wiz.contractor.performance.register'

    _columns = {
                'from_date':fields.date('From Date'),
                'till_date':fields.date('Till Date'),
                'partner_id':fields.many2one('res.partner','Contractor'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'export_data':fields.binary('File',readonly=True),
                'filename':fields.char('File Name',size=250,readonly=True),
                'user_id':fields.many2one('res.users','User Id'),
                'month_id':fields.many2one('holiday.list', 'Month'),
                'seq_from': fields.integer('From Seq.'),
                'seq_to': fields.integer('To Seq.'),
                }
    
    _defaults={
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
    
    def performance_register_report(self,cr,uid,ids,context=None):

    #Define the font attributes for header
        fnt = Font()
        fnt.name = 'Arial Black'
        fnt.size=10
        fnt.Style= 'Regular'
        
        content_fnt = Font()
        content_fnt.name ='Arial Black'
        content_fnt.size=10
        content_fnt.Style= 'Regular'
        align_content = Alignment()
        align_content.horz= Alignment.HORZ_CENTER
     
        borders = Borders()
        
        #The text should be centrally aligned
        align = Alignment()
        align.horz = Alignment.HORZ_LEFT
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
        fnt1.name = 'Ubuntu Medium'
        fnt1.size =10
        fnt1.style='Regular'
        
        content_fnt1 = Font()
        content_fnt1.name ='Ubuntu Medium'
        content_fnt1.style='Regular'
        align_content1 = Alignment()
        align_content1.horz= Alignment.HORZ_LEFT
     
        borders1 = Borders()
        borders1.left = 0x00
        borders1.right = 0x00
        borders1.top = 0x03
        borders1.bottom = 0x03
        
        #The text should be centrally aligned
        align1 = Alignment()
        align1.horz = Alignment.HORZ_CENTER
        align1.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern1 = Pattern()

        #apply the above settings to the row(0) header
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
        
    #Define the font attributes for header
        fnt4 = Font()
        fnt4.name = 'Arial'
        fnt4.size ='10'
        fnt4.style='Regular'
        
        content_fnt4 = Font()
        content_fnt4.name ='Arial'
        content_fnt4.style='Regular'
        align_content4 = Alignment()
        align_content4.horz= Alignment.HORZ_LEFT
     
        borders4 = Borders()
        borders4.left = 0x01
        borders4.right = 0x01
        
        #The text should be centrally aligned
        align4 = Alignment()
        align4.horz = Alignment.HORZ_LEFT
        align4.vert = Alignment.VERT_TOP
        
        #We set the backgroundcolour here
        pattern4 = Pattern()

        #apply the above settings to the row(0) header
        style_header4= XFStyle()
        style_header4.font= fnt4
        style_header4.pattern= pattern4
        style_header4.borders = borders4
        style_header4.alignment=align4
                
        wb = Workbook()
        ws = wb.add_sheet('Contractor Performance Register')
#        style_pass = xlwt.easyxf('pattern: pattern solid, Font.name:Arial ,Bold: True, fore_colour black;')
#        ws.row(0).height=500

        ws.col(1).width = 2200
        ws.col(2).width = 2200
        ws.col(3).width = 2200
        ws.col(4).width = 2500
        ws.col(5).width = 2200
        ws.col(6).width = 2200
        ws.col(7).width = 2200
        ws.col(8).width = 2200
        ws.col(9).width = 2200
        ws.col(10).width = 2200
        ws.col(11).width = 2200
        ws.col(12).width = 2200
        ws.col(13).width = 2200
        ws.col(14).width = 2200
        ws.col(15).width = 2200
        ws.col(16).width = 2200
        ws.col(17).width = 2200
        ws.col(18).width = 2200
        ws.col(19).width = 2200
        ws.col(20).width = 2200
        ws.col(21).width = 2200
        ws.col(22).width = 2200
        ws.col(23).width = 2200
        ws.col(24).width = 2200
        ws.col(25).width = 2200
        ws.col(26).width = 2200
        ws.col(27).width = 2200
        ws.col(28).width = 2200
        ws.col(29).width = 2200
        ws.col(30).width = 2200

        this = self.browse(cr,uid,ids)
        if this.seq_from > this.seq_to:
            raise osv.except_osv(_('Warning !'), _("Sequence From cannot be greater than Sequence To !!!"))
        emp_id = this.employee_id.id
        from_date = datetime.strptime(this.from_date,"%Y-%m-%d")
        var1 = from_date
        from_date = from_date.strftime("%d-%m-%Y")
        
        till_date = datetime.strptime(this.till_date,"%Y-%m-%d")
        var2 = till_date
        till_date = till_date.strftime("%d-%m-%Y")
        
        var = var2 - var1
        var = str(var)
        var = var.split(' ')
        var = int(int(var[0])/2) + 1
        if this.employee_id:
            ws.write_merge(1,1,var-3,var+3,'',style_header2)
        elif this.partner_id :
            ws.write_merge(1,1,var-4,var+4, this.partner_id.name,style_header2)
        else :
            ws.write_merge(1,1,var-3,var+3, '  ' ,style_header2)

        ws.write_merge(3,3,var-3,var+3, 'Performance Register from ' + from_date + ' to ' + till_date ,style_header2)

        emp_obj = self.pool.get('hr.employee')
        if this.employee_id:
            list_ids = emp_obj.search(cr, uid, [('id', '=', this.employee_id.id),('active','=',True),('doj','<=',var2),('type','=','Contractor')])
        elif this.partner_id:
            list_ids = emp_obj.search(cr, uid, [('partner_id', '=', this.partner_id.id),('active','=',True),('doj','<=',var2),('type','=','Contractor')])

        if this.seq_from == 0 and this.seq_to == 0 and len(list_ids) > 300:
            raise osv.except_osv(_('Warning !'), _("More than 300 employee cannot be processed !!!"))
        if (this.seq_to - this.seq_from) > 300:
            raise osv.except_osv(_('Warning !'), _("Range cannot be greater than 300 !!!"))
        if this.seq_from != 0 and this.seq_to != 0:
            list_ids = list_ids[int(this.seq_from - 1):this.seq_to]

        r1 = 5
        r2 = 6
        r3 = 8
        r4 = 10
        r5 = 11
#        r6 = 12
        r7 = 13
        r8 = 14
        r9 = 15
        r10 = 16
        i1 = 0
        for emp in list_ids :
            i = 0
            i1 += 1
            print"Contractor Performance Register emp =============================================================>", emp, i1
            p_count = 0
            a_count = 0
            h_count = 0
            wo_count = 0
            l_count = 0
            total_ot = 0
            total_ot1 = 0
            total_hrs = 0
            total_hrs1 = 0

            if i1 >= 1 :
                if (i1-1)%5 == 0  and i1 != 1 :
                    r1 = r1 + 23
                    r2 = r2 + 23
                    r3 = r3 + 23
                    r4 = r4 + 23
                    r5 = r5 + 23
#                    r6 = r6 + 23
                    r7 = r7 + 23
                    r8 = r8 + 23
                    r9 = r9 + 23
                    r10 = r10 + 23 
                    
                    if this.employee_id:
                        ws.write_merge(r1-4,r1-4,var-3,var+3,'',style_header2)
                    elif this.partner_id :
                        ws.write_merge(r1-4,r1-4,var-4,var+4, this.partner_id.name,style_header2)

                    ws.write_merge(r1-2,r1-2,var-3,var+3, 'Performance Register from ' + from_date + ' to ' + till_date, style_header2)
                else :
                    if i1 > 1 :
                        r1 = r1 + 14
                        r2 = r2 + 14
                        r3 = r3 + 14
                        r4 = r4 + 14
                        r5 = r5 + 14
#                        r6 = r6 + 14
                        r7 = r7 + 14
                        r8 = r8 + 14
                        r9 = r9 + 14
                        r10 = r10 + 14


                                    
            ws.write(r4,0, 'In Time', style_header2)
            ws.write(r5,0, 'Out Time', style_header2)
#            ws.write(r6,0, 'Late', style_header2)
            ws.write(r7,0, 'Hrs. Wkd.', style_header2)
            ws.write(r8,0, 'Over Time', style_header2)
            ws.write(r9,0, 'Status', style_header2)
            ws.write(r10,0, 'Shift Att.', style_header2)                
            
            emp_browse = emp_obj.browse(cr, uid, emp)
            doj = emp_browse.doj
            ws.write(r3,0, 'Card No :', style_header2)
            ws.write(r3,1, emp_browse.sinid, style_header2)
            ws.write(r3,3, 'Name :', style_header2)
            ws.write_merge(r3,r3,4,9, emp_browse.name, style_header2)
       
            ws.write(r1,0, '', style_header1)
            ws.write(r2,0, '', style_header1)

            start_dat = datetime.strptime(from_date,'%d-%m-%Y')
            end_dat = datetime.strptime(till_date,'%d-%m-%Y')
            s_date = start_dat.strftime('%Y-%m-%d')
            tm_tuple = datetime.strptime(s_date,'%Y-%m-%d').timetuple()
            month1 = tm_tuple.tm_mon
            year1 = tm_tuple.tm_year
            start1 = tm_tuple.tm_mday
            e_date = end_dat.strftime('%Y-%m-%d')
            tm_tuple1 = datetime.strptime(e_date,'%Y-%m-%d').timetuple()
            end1 = tm_tuple1.tm_mday
            
            before=datetime(year1,month1,start1)
            after=datetime(year1,month1,end1)
            if emp_browse.week.upper()[0:2]=='SU':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.SU,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True) 
            elif emp_browse.week.upper()[0:2]=='MO':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.MO,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='TU':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.TU,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='WE':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.WE,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='TH':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.TH,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='FR':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.FR,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)
            elif emp_browse.week.upper()[0:2]=='SA':
                rr = rrule.rrule(rrule.WEEKLY,byweekday=relativedelta.SA,dtstart=before)
                week_off_lst = rr.between(before,after,inc=True)


            for val_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(from_date,'%d-%m-%Y'),until=datetime.strptime(till_date,'%d-%m-%Y')):
                val_date_str = val_date.strftime('%Y-%m-%d')
                q1 = cr.execute("select sline.from_time from attendance_shift_line as sline left join attendance_shift as shift on (sline.shift_id=shift.id) "
                                "left join hr_shift_line as hr_sline on (hr_sline.shift_id=shift.id) where hr_sline.employee_id='"+str(emp)+"' ")
                t1 = cr.fetchall()
                
                val_from_date_hrs = str(t1[0][0])
                val_from_date_hrs_lst = val_from_date_hrs.split('.')
                val_from_date_hrs_str1 = val_from_date_hrs_lst[0]
                if len(val_from_date_hrs_str1) == 1 :
                    val_from_date_hrs_str1 = '0' + val_from_date_hrs_str1

                val_from_date_hrs_str2 = str(int(int(val_from_date_hrs_lst[1]) * 60)/100)
                if len(val_from_date_hrs_str2) == 1 :
                    val_from_date_hrs_str2 = '0' + val_from_date_hrs_str2
                
                val_from_date_hrs = str(val_from_date_hrs)
                if len(val_from_date_hrs) == 1 :
                    val_from_date_hrs = '0' + val_from_date_hrs
                val_from_date_str = val_date_str + ' ' + val_from_date_hrs_str1 + ':' + val_from_date_hrs_str2 + ':' + '00'
#                val_from_date_str = val_date_str + ' 00:00:00'
                val_from_date_str = datetime.strptime(val_from_date_str,"%Y-%m-%d %H:%M:%S")
                val_from_date_str = val_from_date_str - timedelta(hours=5,minutes=30)
# Here we have to minus 30 minutes from employee start shift .
                val_from_date_str11 = val_from_date_str - timedelta(hours=0,minutes=30)
                val_from_date_str = val_from_date_str11.strftime("%Y-%m-%d %H:%M:%S")
                
#                val_till_date_str = val_date_str + ' 23:59:59'
#                val_till_date_str = datetime.strptime(val_till_date_str,"%Y-%m-%d %H:%M:%S")
                val_till_date_str = val_from_date_str11 + timedelta(hours=22,minutes=0)
                val_till_date_str = val_till_date_str.strftime("%Y-%m-%d %H:%M:%S")


                i += 1
                date = val_date.strftime('%d')
                week_day = val_date.strftime('%a')
                
                ws.write(r1,i, date, style_header1)
                ws.write(r2,i, week_day, style_header1)
                
                hr_atten_search = self.pool.get('hr.attendance').search(cr,uid,[('search_date','>=',val_date_str),('search_date','<=',val_date_str),('employee_id','=',emp)])
                if len(hr_atten_search) == 1:
                    raise osv.except_osv(_('Warning !!!!'),_("Only 1 Punch Found For Employee [ " +(emp_browse.sinid)+" ] " "on Date %s" % (val_date_str)))
                
                if hr_atten_search :
                    hr_atten_lst = []
                    hr_atten_lst1 = []
                    for hr_atten_id in hr_atten_search :
                        hr_atten_browse = self.pool.get('hr.attendance').browse(cr,uid,hr_atten_id).name
                        attendance = datetime.strptime(hr_atten_browse,"%Y-%m-%d %H:%M:%S")
                        attendance = attendance + timedelta(hours=5,minutes=30)
#                        attendance = attendance.strftime("%d-%m-%Y %H:%M:%S")
                        hr_atten_lst1.append(attendance)
                    hr_atten_lst1.sort()
                    
                    for val in hr_atten_lst1 :
                        attendance = val.strftime("%d-%m-%Y %H:%M:%S")
                        hr_atten_lst.append(attendance)
                    
                    q1 = cr.execute("select shift.shift_name,sline.from_time,sline.working_time,sline.lunch_time from attendance_shift_line as sline left join attendance_shift as shift on (sline.shift_id=shift.id) "
                                    "left join hr_shift_line as hr_sline on (hr_sline.shift_id=shift.id) where hr_sline.employee_id='"+str(emp)+"' and hr_sline.name<='"+str(val_date)+"' order by hr_sline.name desc limit 1 ")
                    t1 = cr.fetchall()
                    if t1:
                          shift = t1[0][0]
                    else:
                          raise osv.except_osv(_('Warning !'), _("Shift is Missing for Employee %s on Date %s" %(emp_browse.sinid,val_date_str)))
                    
                    in_punch = hr_atten_lst[0]
                    out_punch = hr_atten_lst[1]
                    
                    in_punch = datetime.strptime(in_punch,"%d-%m-%Y %H:%M:%S")
                    out_punch = datetime.strptime(out_punch,"%d-%m-%Y %H:%M:%S")
                    total_time_diff = out_punch - in_punch   
                    total_time_diff_lst = str(total_time_diff).split(':')
                    total_time_diff_min = (int(total_time_diff_lst[0])*60) + int(total_time_diff_lst[1])
                                                                
                    in_time = in_punch.strftime('%H:%M')
                    out_time = out_punch.strftime('%H:%M')
                    
                    t11_lst = str(t1[0][1]).split('.')
                    if len(t11_lst[0]) == 1 :
                        t11_hrs = '0' + t11_lst[0]
                    else :
                        t11_hrs = t11_lst[0]
                    t11_min = int((int(t11_lst[1])*60)/100)
                    if len(str(t11_min)) == 1 :
                        t11_min = '0' + str(t11_min)
                    else :
                        t11_min = str(t11_min)
                        
                    shift_in_time_date_str = val_date_str + ' ' + t11_hrs + ':' + t11_min + ':' + '00'
                    shift_in_time_date = datetime.strptime(shift_in_time_date_str,"%Y-%m-%d %H:%M:%S")
                    shift_in_time_date_str = datetime.strftime(shift_in_time_date,"%d-%m-%Y %H:%M:%S")
                    shift_in_time_date = datetime.strptime(shift_in_time_date_str,"%d-%m-%Y %H:%M:%S")
                    
#                    if shift_in_time_date < hr_atten_lst1[0]:
#                        late_time = hr_atten_lst1[0] - shift_in_time_date
#                        late_time = str(late_time)
#                        late_time_lst = late_time.split(':')
#                        late_time_hrs = int(late_time_lst[0])*60
#                        late_time_min = int(late_time_lst[1])
#                        late = late_time_hrs + late_time_min
#                    else :
#                        late = 0
                    
#                    t11 = str(t1[0][1])
#                    t11 = t11.split('.')
#                    t1_min = (int(t11[0])*60) + int((int(t11[1])*60)/100)
                    in_time_min = in_time.split(':')
                    in_time_min = (int(in_time_min[0])*60) + int(in_time_min[1])
#                    
                    
                    out_time_min = out_time.split(':')
                    out_time_min = (int(out_time_min[0])*60) + int(out_time_min[1])

#                    if in_time_min > t1_min :
#                        late = in_time_min - t1_min
#                    else :
#                        late = 0 
                    
                    interval = t1[0][3]
#                    lunch_start = datetime.strptime('13:00',"%H:%M")
#                    lunch_start = lunch_start.strftime('%H:%M')
#                    
#                    lunch_end = datetime.strptime('13:45',"%H:%M")
#                    lunch_end = lunch_end.strftime('%H:%M')
#                                        
#                    if (in_time < lunch_start) and (out_time >= lunch_end) and t1[0][2] > 8 :
#                        interval = 45
#                    elif (in_time < lunch_start) and (out_time < lunch_start) and t1[0][2] > 8 :
#                        interval = 0
#                    elif (in_time < lunch_start) and (out_time < lunch_end) and t1[0][2] > 8 :
#                        interval = out_time_min - (13*60)
#                    elif (in_time >= lunch_end) and t1[0][2] > 8 :
#                        interval = 0
#                    elif (in_time > lunch_start) and (in_time <= lunch_end) and t1[0][2] > 8 :
#                        interval = ((13*60)+45) - in_time_min
                    
#                    if shift == 'GRD B' :
#                        time_diff = working_time_grd_b
#                    else :
                    
                    time_diff = total_time_diff_min - interval
                    total_hrs1 +=  time_diff
                    
                    working_hrs = float(time_diff)/60
                    working_hrs = str(working_hrs)
                    working_hrs = working_hrs.split('.')
                    working_hrs = working_hrs[0]
                    working_min = time_diff%60
                    working_min = str(working_min)
                    if len(working_min) == 1 :
                        working_min = '0' + working_min
                    
                    working_time = working_hrs + '.' + working_min                
                
                    ws.write(r4,i, in_time, style_header3)
                    ws.write(r5,i, out_time, style_header3)
#                    ws.write(r6,i, late, style_header3)
                    ws.write(r7,i, working_time, style_header3)
                    ws.write(r10,i, shift, style_header3)
            
                else :
                    if doj > val_date_str :
                        ws.write(r4,i, 'N/A', style_header3)
                        ws.write(r5,i, 'N/A', style_header3)
#                        ws.write(r6,i, 'N/A', style_header3)
                        ws.write(r7,i, 'N/A', style_header3)
                        ws.write(r10,i, 'N/A', style_header3)
                    else :
                        ws.write(r4,i, '', style_header3)
                        ws.write(r5,i, '', style_header3)
#                        ws.write(r6,i, '', style_header3)
                        ws.write(r7,i, '', style_header3)
                        ws.write(r10,i, '', style_header3)

                if doj > val_date_str :
                    ws.write(r8,i,'N/A' , style_header3)
                    ws.write(r9,i, 'N/A', style_header3)
                
                else :
                    q2 = cr.execute("select over_time,working from attendance_timing where employee_id='"+str(emp)+"' and name='"+str(val_date)+"'  ")
                    t2 = cr.fetchall()
                    if t2 :
                        ot_hrs = float(t2[0][0])/60
                        ot_hrs = str(ot_hrs)
                        ot_hrs = ot_hrs.split('.')
                        ot_hrs = ot_hrs[0]
                        
                        ot_min = (t2[0][0])%60
                        ot_min = int(ot_min)
                        ot_min = str(ot_min)
                        if len(ot_min) == 1 :
                            ot_min = '0' + ot_min
                        over_time = ot_hrs + '.' + ot_min                
                        
                        status = t2[0][1]
                        if status == 'A' :
                            a_count += 1
                        elif status == 'POW' :
                            wo_count += 1
                        elif status == 'POH' :
                            h_count += 1
                        else :
                            p_count += 1
                        total_ot1 += t2[0][0]
                        
                        ws.write(r8,i,over_time , style_header3)
                        ws.write(r9,i, status, style_header3)
                        
                    if len(t2) == 0 and emp_browse.week != 'Sunday':
                        t3 = []
                        for vall in week_off_lst:
                            if val_date == vall:
                                over_time = ''
                                t3.append(emp_browse.week)
                                status = 'WO'
                                wo_count += 1
                                ws.write(r8,i,over_time , style_header3)
                                ws.write(r9,i, status, style_header3) 
                                
                        if len(t3) == 0:
                            q3 = cr.execute("select week from holiday_list_lines where leave_date='"+str(val_date)+"'  ")
                            t3 = cr.fetchall()
                            if t3 :
                                t3 = t3[0][0]
                                over_time = ''
                                if t3 != 'Sunday' and t3 != emp_browse.week :
                                    status = 'HLD'
                                    h_count += 1
                                ws.write(r8,i,over_time , style_header3)
                                ws.write(r9,i, status, style_header3) 
                        
                    elif len(t2) == 0 and emp_browse.week == 'Sunday':
                        q3 = cr.execute("select week from holiday_list_lines where leave_date='"+str(val_date)+"'  ")
                        t3 = cr.fetchall()
                        if t3 :
                            t3 = t3[0][0]
                            over_time = ''
                            if t3 == 'Sunday' :
                                status = 'WO'
                                wo_count += 1
                            else :
                                status = 'HLD'
                                h_count += 1
                            ws.write(r8,i,over_time , style_header3)
                            ws.write(r9,i, status, style_header3) 
                            
                    if len(t2) == 0 and len(t3) == 0 : 
                        q4 = cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp)+"' and state='validate' and type='remove' ")
                        t4 = cr.fetchall()
                        status = ''
                        if t4 :
                            for val1 in t4 :
                                for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                                    if leave_date == val_date and val1[2] != 'Factory Work':
                                        over_time = ''
                                        if val1[2] == 'Earned Leaves' : status = 'EL'
                                        elif val1[2] == 'Compensatory Days' : status = 'COM'
                                        elif val1[2][0:4] == 'Sick' : status = 'SL'
                                        elif val1[2][0:4] == 'Casu' : status = 'CL'
                                        l_count += 1
                                        ws.write(r8,i,over_time , style_header3)
                                        ws.write(r9,i, status, style_header3)   
                                    elif leave_date == val_date and val1[2] == 'Factory Work':
                                        over_time = ''
                                        p_count += 1
                                        status = 'FW'
                                        ws.write(r8,i,over_time , style_header3)
                                        ws.write(r9,i, status, style_header3)   
                                            
                        if status == '' :
                            status = 'A'
                            over_time = ''
                            a_count += 1
                            ws.write(r8,i,over_time , style_header3)
                            ws.write(r9,i, status, style_header3)
            
            total_ot_hrs = float(total_ot1)/60
            total_ot_hrs = str(total_ot_hrs)
            total_ot_hrs = total_ot_hrs.split('.')
            total_ot_hrs = total_ot_hrs[0]
            total_ot_min = (total_ot1)%60
            total_ot_min = int(total_ot_min)
            total_ot_min = str(total_ot_min)
            if len(total_ot_min) == 1 :
                total_ot_min = '0' + total_ot_min
            
            total_ot = total_ot_hrs + '.' + total_ot_min   
            
            total_working_hrs = float(total_hrs1)/60
            total_working_hrs = str(total_working_hrs)
            total_working_hrs = total_working_hrs.split('.')
            total_working_hrs = total_working_hrs[0]
            total_working_min = total_hrs1%60
            total_working_min = str(total_working_min)
            if len(total_working_min) == 1 :
                total_working_min = '0' + total_working_min
            
            total_hrs = total_working_hrs + '.' + total_working_min                
            
            ws.write(r3,11, 'Present:', style_header2)
            ws.write(r3,12, p_count, style_header2)
            ws.write(r3,13, 'Absent:', style_header2)
            ws.write(r3,14, a_count, style_header2)
            ws.write(r3,15, 'Holiday:', style_header2)
            ws.write(r3,16, h_count, style_header2)  
            ws.write(r3,17, 'Wk Off:', style_header2)
            ws.write(r3,18, wo_count, style_header2)     
            ws.write(r3,19, 'Leave :', style_header2)
            ws.write(r3,20, l_count, style_header2)     
            ws.write(r3,21, 'Hrs Wkd:', style_header2)
            ws.write(r3,22, total_hrs, style_header2)     
            ws.write(r3,23, 'OT:', style_header2)
            ws.write(r3,24, total_ot, style_header2)     

            
        
        f = cStringIO.StringIO()
        wb.save(f)
        out=base64.encodestring(f.getvalue())
        return self.write(cr, uid, ids, {'export_data':out, 'filename':'Contractor Performance Register.xls'}, context=context)
    
