import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import logging
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp
import pymssql
import math
import csv


class holiday_year(osv.osv):
    _name = 'holiday.year'

    _columns = {
                'name':fields.char('Year',required=True,size=4),
                }
    
class holiday_list(osv.osv):
    _name = 'holiday.list'
    
    def _calculate_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr, uid, ids):
            if val.month == '1':
                month = 'January'
            elif val.month == '2':
                month = 'February'
            elif val.month == '3':
                month = 'March'
            elif val.month == '4':
                month = 'April'
            elif val.month == '5':
                month = 'May'
            elif val.month == '6':
                month = 'June'
            elif val.month == '7':
                month = 'July'
            elif val.month == '8':
                month = 'August'
            elif val.month == '9':
                month = 'September'
            elif val.month == '10':
                month = 'October'
            elif val.month == '11':
                month = 'November'
            else:
                month = 'December'
            res[val.id] = month +' '+ str(val.year_id.name)
        return res
    
    def _calculate_days(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr, uid, ids):
            line_ids = []
            for line in val.holiday_lines:
                time1 = datetime.strptime(str(line.leave_date) + ' 01:00:00','%Y-%m-%d %H:%M:%S').timetuple().tm_mon
                time2 = val.month
                if int(time2) != int(time1):
                    raise osv.except_osv(_('Warning !'),_('Specified holiday line date does not belongs to selected month.'))
                line_ids.append(line.id)
            res[val.id] = len(line_ids)
        return res

    
    _columns = {
                'name':fields.function(_calculate_name,method=True,store=True,string='Name',type='char',size=64),
                'date':fields.date('Create Date',readonly=True),
                'month':fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),
                ('8','August'),('9','September'),('10','October'),('11','November'),('12','December'),],'Month',required=True),
                'year_id':fields.many2one('holiday.year','Year',required=True),
                'holiday_lines':fields.one2many('holiday.list.lines','holiday_id','Holiday Lines'),
                'holiday':fields.function(_calculate_days,method=True,store=True,string="Working Days",type="integer"),
                }
    
    _defaults = {
                 'date':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                 }
    
    _sql_constraints = [('unique_month_year','unique(month,year_id)','Month for this Year is already define.')]
    
class holiday_list_lines(osv.osv):
    _name = 'holiday.list.lines'
    
    _columns = {
                'name':fields.char('Description',size=255,required=True),
                'week':fields.selection([('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')],'Week',required=True),
                'holiday_id':fields.many2one('holiday.list','Holiday',ondelete="cascade"),
                'leave_date':fields.date('Holiday Date',required=True),
                }    
    _sql_constraints = [('unique_week_leave','unique(week,leave_date)','Day of this week is already define.')]

 
class hr_holidays(osv.osv):
    _inherit="hr.holidays"
    
    _columns={
              'from_date': fields.date('Start Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, select=True, copy=False),
              'month':fields.many2one('holiday.list','Month',readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, select=True,),
              'work_type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection"),  
              'leave_mode':fields.selection([('Automatic','Automatic'),('Mannual','Mannual')],'Levae Mode',required=True),
             } 
    _defaults = {
         'employee_id': False,
         'leave_mode':'Mannual'
         
        }

    
    def onchange_from(self, cr, uid, ids, emp_id, date):
        result = {'value': {}}
        if date:
            date = str(date) + ' ' + '03:30:00'
            result['value']['date_from'] = date
            
        return result
    
    def onchange_leave_type(self, cr, uid, ids, employee_id, context=None):
        res = {}
        if not employee_id:
            return res
        cr.execute("select month from hr_holidays where type='remove' order by id desc limit 1")
        temp = cr.fetchall()
        for data in temp:
            if data and len(data) > 0 :
                month = data[0]
                res['value'] = {'month':month,}
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        this = self.browse(cr, uid, ids)
        if this.type == 'remove':
            emp_id = this.employee_id.id
            emp_name = this.employee_id.name
            if 'date_from' in vals and vals['date_from'] and 'date_to' in vals and vals['date_to']:
                start  = datetime.strptime(vals['date_from'],'%Y-%m-%d %H:%M:%S')
                start = start.strftime('%Y-%m-%d')
                end  = datetime.strptime(vals['date_to'],'%Y-%m-%d %H:%M:%S')
                end = end.strftime('%Y-%m-%d')
                earned_id = self.pool.get('hr.holidays.status').search(cr, uid, [('name','=','Earned Leaves')])
                while(start <= end):
                    att_rec = self.pool.get('hr.attendance').search(cr, uid, [('search_date','=',start),('employee_id','=',emp_id)])
                    hld_rec = self.pool.get('holiday.list.lines').search(cr, uid, [('leave_date','=',start)])
                    if len(att_rec) == 2:
                        raise osv.except_osv(_('Warning !'),_(" %s is present on this date.You cant not assign leave on this day %s.....!!!!!"%(emp_name, start)))
                    elif len(att_rec) == 1:
                        raise osv.except_osv(_('Warning !'),_(" Please check the HR Attendance for this Employee.....!!!!!"%(emp_id, start)))
                    elif len(hld_rec) > 0 :
                        raise osv.except_osv(_('Warning !'),_(" Leave can not be posted on the Holiday for Employee %s on %s date.."%(emp_id, start)))
                    start = datetime.strptime(start,'%Y-%m-%d')
                    start += timedelta(days=1)
                start = start.strftime('%Y-%m-%d')
        res = super(hr_holidays, self).write(cr, uid, ids, vals, context)
        return res
    
    def create(self, cr, uid, vals, context=None):
        if 'type' in vals and vals['type'] == 'remove':
            emp_id = vals['employee_id']
            emp_name = self.pool.get('hr.employee').browse(cr, uid,emp_id).name
            start  = datetime.strptime(vals['date_from'],'%Y-%m-%d %H:%M:%S')
            start = start.strftime('%Y-%m-%d')
            end  = datetime.strptime(vals['date_to'],'%Y-%m-%d %H:%M:%S')
            end = end.strftime('%Y-%m-%d')
            earned_id = self.pool.get('hr.holidays.status').search(cr, uid, [('name','=','Earned Leaves')])
            if 'month' in vals and vals['month'] and 'from_date' in vals and vals['from_date']:
                rec = self.pool.get('holiday.list').browse(cr, uid, vals['month'])
                from_date = datetime.strptime(vals['from_date'],'%Y-%m-%d')
                month_id = int(rec.month)
                year = int(rec.year_id.name)
                year_val = int(from_date.strftime('%Y'))
                month_val = int(from_date.strftime('%m'))
                if month_id != month_val or year != year_val :
                    raise osv.except_osv(_('Warning !'),_("Month, Start Date and End Date must be of Same Month and Year .....!!!!!")) 
            while(start <= end):
                att_rec = self.pool.get('hr.attendance').search(cr, uid, [('search_date','=',start),('employee_id','=',emp_id)])
                hld_rec = self.pool.get('holiday.list.lines').search(cr, uid, [('leave_date','=',start)])
                if len(att_rec) == 2:
                    raise osv.except_osv(_('Warning !'),_(" %s is present on this date.You cant not assign leave on this day %s.....!!!!!"%(emp_name, start)))
                elif len(att_rec) == 1:
                    raise osv.except_osv(_('Warning !'),_(" Please check the HR Attendance for this Employee.....!!!!!"%(emp_id, start)))
                elif len(hld_rec) > 0 :
                    raise osv.except_osv(_('Warning !'),_(" Leave can not be posted on the Holiday for Employee %s on %s date.."%(emp_name, start)))
                start = datetime.strptime(start,'%Y-%m-%d')
                start += timedelta(days=1)
                start = start.strftime('%Y-%m-%d')
            
            if 'holiday_status_id' in vals and vals['holiday_status_id'] == earned_id[0]:
                if 'month' in vals and vals['month'] :
                    rec = self.pool.get('holiday.list').browse(cr, uid, vals['month'])
                    year = rec.year_id.name
                    month_id = rec.month
                    qry = """ select id from earn_leave_history where extract(month from name) = '"""+str(month_id)+"""' and extract(year from name) = '"""+str(year)+"""' limit 1 """
                    cr.execute(qry)
                    data = cr.fetchall()
                    if len(data) == 0 :
                        raise osv.except_osv(_('Warning !'),_(" Earned Leave can not be posted before computing Earned Leave Button and Compute Punches for....%s"%(rec.name)))
                    earn_val = self.pool.get('hr.employee').browse(cr, uid,emp_id).earn_leave
                    earn_val = earn_val - vals['number_of_days_temp'] 
                    self.pool.get('hr.employee').write(cr, uid,[emp_id],{'earn_leave' : earn_val})  
        res = super(hr_holidays,self).create(cr, uid, vals, context)
        return res