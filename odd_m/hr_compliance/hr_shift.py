import logging
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp
import pymssql
import math
import re 
import base64, urllib
import os
import csv
class attendance_shift(osv.osv):
    _name = 'attendance.shift'
    
    _columns = {
                'name':fields.char('Name',size=64,required=True,select=True),
                'date':fields.date('Date',required=True),
                'shift_line':fields.one2many('attendance.shift.line','shift_id','Shift line'),
                'user_id':fields.many2one('res.users','Created By',readonly=True),
                }
    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               }
    
    def create(self, cr, uid, vals, context=None):
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].strip()
            vals['name'] = vals['name'].upper()
        res = super(attendance_shift,self).create(cr, uid, vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = {}
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].strip()
            vals['name'] = vals['name'].upper()
        res = super(attendance_shift, self).write(cr, uid, ids, vals, context)
        return res


class attendance_shift_line(osv.osv):
    _name = 'attendance.shift.line'
    
    def _calculate_time(self, cr, uid, ids, name, arg, context=None):
        res = {}
        working = 0.0
        for each in self.browse(cr, uid, ids):
            date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            timing = self.calculate_time(cr, uid, ids, date, each.from_time, each.to_time)
            working = timing.get('working_hour',0.0)
            res[each.id]=working
        return res
    
    def float_time_convert(self,float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return (factor * int(math.floor(val)), int(round((val % 1) * 60)))

    def calculate_time(self, cr, uid, ids, date, start, end):
        time1 = time2 = '00:00'
        
        val1 = self.float_time_convert(start)
        if val1 and len(str(val1[1])) == 1:
            time1 = str(val1[0]) +':'+'0'+str(val1[1])
        
        if val1 and len(str(val1[1])) == 2:
            time1 = str(val1[0]) +':'+str(val1[1])
        
        start_hr = val1[0]
        start_time = str(date) +' '+ str(time1) + ':00'
        
        val2 = self.float_time_convert(end)
        if val2 and len(str(val2[1])) == 1:
            time2 = str(val2[0]) +':'+'0'+str(val2[1])
        
        if val2 and len(str(val2[1])) == 2:
            time2 = str(val2[0]) +':'+str(val2[1])
        
        end_hr = val2[0]
        
        start_time1 = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S').timetuple()
        year = start_time1.tm_year
        mon = start_time1.tm_mon
        day = start_time1.tm_mday
        hour = start_time1.tm_hour
        min  = start_time1.tm_min
        sec = start_time1.tm_sec
        hour1 = hour
        mon1 = mon
        day1 = day
        year1 = year
            
#===========================================================================
        if int(start_hr) > int(end_hr):
            day2 = day + 1
            if mon in [1,3,5,7,8,10,12]:
                if day >= 31:
                    day2 = 1
                    mon2 = mon + 1
                    year2 = year
                    if mon2 > 12:
                        year2 = year + 1
                        mon2 = 1
                else:
                    mon2 = mon
                    year2 = year
                
            elif mon in [4,6,9,11]:
                if day >= 30:
                    day2 = 1
                    mon2 = mon + 1
                    year2 = year
                else:
                    mon2 = mon
                    year2 = year
            elif mon == 2:
                if year % 4 == 0:
                    if day >= 29:
                        day2 = 1
                        mon2 = mon + 1
                        year2 = year
                    else:
                        mon2 = mon
                        year2 = year
                else:
                    if day >= 28:
                        day2 = 1
                        mon2 = mon + 1
                        year2 = year
                    else:
                        mon2 = mon
                        year2 = year
            time2_split = time2.split(':')
            hour2 = int(end_hr)
            min2 = int(time2_split[1])
        else:
            time2_split = time2.split(':')
            hour2 = int(end_hr)
            min2 = int(time2_split[1])
            mon2 = mon
            day2 = day
            year2 = year            
#        =========================================================================
        
        
        if (hour + 22) > 24:
            hour = abs(24 - (hour + 22))
            day = day + 1
                                    
            if mon in [1,3,5,7,8,10,12]:
                if day > 31:
                    day = 1
                    mon = mon + 1
                if mon > 12:
                    year = year + 1
                    mon = 1
            elif mon in [4,6,9,11]:
                if day > 30:
                    day = 1
                    mon = mon + 1
            elif mon == 2:
                if year % 4 == 0:
                    if day > 29:
                        day = 1
                        mon = mon + 1
                else:
                    if day > 28:
                        day = 1
                        mon = mon + 1
        else:
            hour = hour + 22
            
        if len(str(mon1)) < 2:
            mon1 = '0'+str(mon1)
        if len(str(day1)) < 2:
            day1 = '0'+str(day1)
        if len(str(mon2)) < 2:
            mon2 = '0'+str(mon2)
        if len(str(day2)) < 2:
            day2 = '0'+str(day2)
        if len(str(mon)) < 2:
            mon = '0'+str(mon)
        if len(str(day)) < 2:
            day = '0'+str(day)

                
        start_time = str(year1) +'-'+str(mon1)+'-'+str(day1) +' '+ str(hour1)+':'+str(min)+':'+str(sec)
        end_time = str(year2) +'-'+str(mon2)+'-'+str(day2) +' '+ str(hour2)+':'+str(min2)+':'+str('00')
        final_time = str(year) +'-'+str(mon)+'-'+str(day) +' '+ str(hour)+':'+str(min)+':'+str(sec)
        working_time = (datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
        working_hour = working_time.total_seconds()/3600
        timing = {'start_time':start_time,
                  'end_time':end_time,
                  'final_time':final_time,
                  'working_hour':working_hour,
                  }
        
        return timing
    
    _columns = {
                'type':fields.selection([('morning','Morning'),('evening','Evening'),('night','Night')],'Shift',required=True),
                'case':fields.selection([('worker','Worker'),('Staff','Staff'),('office_staff','OFFICE STAFF')],'Cases',),
                'from_time':fields.float('From Time',required=True),
                'to_time':fields.float('To Time',required=True),
                'shift_id':fields.many2one('attendance.shift','Shift',ondaelete="cascade"),
                'working_time':fields.function(_calculate_time,method=True,store=True,string="Working Time",type="float"),
                'user_id':fields.many2one('res.users','Created By',readonly=True),
                }

    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               }
    

class hr_shift_line(osv.osv):
    _name = 'hr.shift.line'
    _order = 'name'
    

    def _calculate_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            res[each.id] = month     
        return res
     
    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.name,'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                res[each.id] = year_id[0]  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res
    
    _columns = {
                'employee_id':fields.many2one('hr.employee','Employee',select=True),
                'name':fields.date('Date',required=True,select=True),
                'shift_id':fields.many2one('attendance.shift','Shift',select=True),
#                 'department_id':fields.related('employee_id','department_id',relation='hr.department',string='Department',type="many2one"),
                'department_id':fields.many2one('hr.department','Department',select=True,store=True),
                'manager_id':fields.related('employee_id','parent_id',relation='hr.employee',string='Reporting Officer',type="many2one"),
                'user_id':fields.many2one('res.users','Created By',readonly=True),
                'month':fields.function(_calculate_month,method=True,type='integer',string='Month',store=True),
                'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
                }
    _defaults={
               'name':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
               'user_id': lambda obj, cr, uid, context: uid,
               }
    
    def create(self, cr, uid, vals, context=None):
        obj=False
         
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].strip()
            vals['name'] = vals['name'].upper()

        if 'name' in vals and vals['name']:
            if datetime.strptime(vals['name'],'%Y-%m-%d') > datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),'%Y-%m-%d'):
                raise osv.except_osv(_('Warning!'),_("Shift date cannot be greater than today's date."))
             
        if 'name' in vals and vals['name'] and 'employee_id' in vals and vals['employee_id'] :
            obj=self.search(cr,uid,[('name','=',vals['name']),('employee_id','=',vals['employee_id'])])
            if obj:
                raise osv.except_osv(_('Warning!'),_("Record already exists for this date"))
        
        if 'employee_id'in vals and vals['employee_id']:
            emp_id=self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'],context=None)
            vals['department_id'] = emp_id.department_id.id
                 
        if 'employee_id' in vals and vals['employee_id'] and 'shift_id' in vals and vals['shift_id'] :    
            last_shift_line_ids = self.search(cr, uid, [('employee_id','=',vals['employee_id'])], limit=1, order='name DESC')
            if last_shift_line_ids:
                if self.browse(cr,uid,last_shift_line_ids[0]).shift_id.id == vals['shift_id']:
                        raise osv.except_osv(_('Warning!'),_("shift already exists "))
        res = super(hr_shift_line,self).create(cr, uid, vals)
        if 'name' in vals and vals['name'] and 'employee_id' in vals and vals['employee_id']:
            last_shift_ids = self.search(cr, uid, [('employee_id','=',vals['employee_id'])], limit=1, order='name DESC')
            if last_shift_ids and res:
                if res == last_shift_ids[0]:
                    self.pool.get('hr.employee').write(cr, uid, [vals['employee_id']],{'shift_id':vals['shift_id']})
        return  res

    
    def write(self,cr,uid,ids,vals,context=None):
        obj=False
        if 'shift_id' in vals and vals['shift_id'] :
            emp_id = self.browse(cr,uid,ids[0]).employee_id.id
            if emp_id :
                last_shift_line_ids = self.search(cr, uid, [('shift_id','=',vals['shift_id']),('employee_id','=',emp_id)], limit=1, order='name DESC')
                if last_shift_line_ids:
                    if self.browse(cr,uid,last_shift_line_ids[0]).shift_id.id == vals['shift_id']:
                            raise osv.except_osv(_('Warning!'),_("shift already exists "))
                self.pool.get('hr.employee').write(cr, uid, [emp_id],{'shift_id':vals['shift_id']})
         
        elif 'name' in vals and vals['name'] and 'employee_id' in vals and vals['employee_id'] :
            obj=self.search(cr,uid,[('name','=',vals['name']),('employee_id','=',vals['employee_id'])])
            if obj:
                raise osv.except_osv(_('Warning!'),_("Record already exists for this date"))
        elif 'name' in vals and vals['name']:
            emp_id = self.browse(cr,uid,ids[0]).employee_id.id
            if emp_id:
                obj=self.search(cr,uid,[('name','=',vals['name']),('employee_id','=',emp_id)])
                if obj:
                    raise osv.except_osv(_('Invalid  Name'), _('shift already exists for this date'))
        elif 'employee_id' in vals and vals['employee_id']:
            shift_date = self.browse(cr,uid,ids[0]).name
            if shift_date:
                obj=self.search(cr,uid,[('name','=',shift_date),('employee_id','=',vals['employee_id'])])
                if obj:
                    raise osv.except_osv(_('Invalid  Name'), _('shift already exists for this date'))    
                   
        res = super(hr_shift_line,self).write(cr, uid, ids, vals)
        return res


              