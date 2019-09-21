from openerp.osv import osv, fields
import time
import random
from datetime import datetime, timedelta
from openerp.tools.translate import _
import math

class wiz_update_ot(osv.TransientModel):
    _name = 'wiz.update.ot'

    def _get_company_id(self, cr, uid, context=None):
        comp_id = self.pool.get('res.users').browse(cr, uid, uid,context=None).company_id
        if comp_id:
            return comp_id.id
        return False

    _columns={
              'name':fields.date('Date'),
              'till_date':fields.date('Till Date'),
              'employee_id':fields.many2one('hr.employee',string="Employee"),
              'in_punch':fields.boolean('IN Punch'),
              'department_id':fields.many2one('hr.department',string="Department"),
              'company_id':fields.many2one('res.company',string="Company"),
              'ot_time':fields.char("OT Time",),
              'user_id':fields.many2one('res.users',"User ID"),
              'employment_type':fields.selection([('Employee','Employee'),('Labor','Labor'),('Trainee','Trainee')],'Employment Type'),
              'type':fields.selection([('Employee','Employee'),('Contractor','Contractor')],'Type'),
              }
    
    _defaults={
               'company_id' : _get_company_id,
               'user_id' : lambda obj, cr, uid, context: uid,
               }
    
    def float_time_convert(self,float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return (factor * int(math.floor(val)), int(round((val % 1) * 60)))
    
    
    def calculate_time(self, cr, uid, ids, date, time):
        time2 = '00:00'
        
        val2 = self.float_time_convert(time)
        if val2 and len(str(val2[1])) == 1:
            time2 = str(val2[0]) +':'+'0'+str(val2[1])
        
        if val2 and len(str(val2[1])) == 2:
            time2 = str(val2[0]) +':'+str(val2[1])
        
        date_tuple = datetime.strptime(date,'%Y-%m-%d %H:%M:%S').timetuple()      
        year = date_tuple.tm_year
        mon = date_tuple.tm_mon
        day = date_tuple.tm_mday  
        
        end_time = str(year)+'-'+str(mon)+'-'+str(day)+' '+str(time2)+':00'
        timing = {
                  'end_time':end_time,
                  }
        return timing

    
    def compute_ot(self, cr,uid,ids,context=None):
        hr_obj = self.pool.get("hr.employee")
        att_obj = self.pool.get('hr.attendance')
        shift_obj = self.pool.get('hr.shift.line')
        if ids:0
            rec = self.browse(cr, uid, ids)
            date = datetime.strptime(rec.name,'%Y-%m-%d')
#            if rec.name and rec.ot_time and not rec.in_punch :
            if rec.name and rec.ot_time:    
                ot_time = rec.ot_time
                data = ot_time.split('.')
                if len(data[1]) != 2:
                    raise osv.except_osv(_('Warning !'),_("Please enter the Correct Time Format (0H.MM) .....!!!!"))
                hr = int(data[0])
                min = int(data[1])
                if min > 59:
                    raise osv.except_osv(_('Warning !'),_("Minutes can not be greater than 59...!!!!"))
                temp = (hr*60) + min
                if rec.department_id and rec.company_id and rec.employment_type and not rec.employee_id: 
                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('department_id','=',rec.department_id.id),('company_id','=',rec.company_id.id),('employment_type', '=', rec.employment_type)])
                    if len(emp_ids) > 0:
                        for val in hr_obj.browse(cr, uid, emp_ids) :
                            final_time = 0
          max punch bata rha h   # cr.execute(""" select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '"""+str(val.id)+"""' and search_date =  '"""+str(date)+"""' group by id order by name desc limit 1 """)
                            att_rec = cr.fetchall()
                            if len(att_rec) > 0 :
                          form id      rec_id = att_rec[0][0]
                             last punch    rec_date = att_rec[0][1]
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                      shift ka end punch  timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)
                                        
                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                                final_time = temp + random.randrange(0,5)
                                final_date = final_date + timedelta(hours=0,minutes=final_time)
                                final_date = final_date - timedelta(hours=5,minutes=30)
                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                
                elif rec.employee_id and not rec.department_id and not rec.company_id and not rec.employment_type:
                    for val in rec.employee_id :
                        final_time = 0
                        cr.execute(""" select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '"""+str(val.id)+"""' and search_date  =  '"""+str(date)+"""' group by id order by name desc limit 1 """)
                        att_rec = cr.fetchall()
                        if len(att_rec) > 0 :
                            rec_id = att_rec[0][0]
                            rec_date = att_rec[0][1]
                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                            if prev_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                            elif next_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                            else:
                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                            if shift_data:
                                for line in shift_data.shift_id.shift_line:
                                    timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)

                            final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                            final_time = temp + random.randrange(0,5)
                            final_date = final_date + timedelta(hours=0,minutes=final_time)
                            final_date = final_date - timedelta(hours=5,minutes=30)
                            cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                        else :
                            raise osv.except_osv(_('Warning !'),_("No Employee Attendance record found for this Employee on this date...!!!!"))

                elif rec.department_id and rec.company_id and not rec.employee_id and not rec.employment_type: 
                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('department_id','=',rec.department_id.id),('company_id','=',rec.company_id.id)])
                    if len(emp_ids) > 0:
                        for val in hr_obj.browse(cr, uid, emp_ids) :
                            final_time = 0
                            cr.execute(""" select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '"""+str(val.id)+"""' and search_date =  '"""+str(date)+"""' group by id order by name desc limit 1 """)
                            att_rec = cr.fetchall()
                            if len(att_rec) > 0 :
                                rec_id = att_rec[0][0]
                                rec_date = att_rec[0][1]
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)
                                        
                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                                final_time = temp + random.randrange(0,5)
                                final_date = final_date + timedelta(hours=0,minutes=final_time)
                                final_date = final_date - timedelta(hours=5,minutes=30)
                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))

                elif rec.employment_type and rec.company_id and not rec.employee_id and not rec.department_id: 
                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('employment_type', '=', rec.employment_type),('company_id','=',rec.company_id.id)])
                    if len(emp_ids) > 0:
                        for val in hr_obj.browse(cr, uid, emp_ids) :
                            final_time = 0
                            cr.execute(""" select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '"""+str(val.id)+"""' and search_date =  '"""+str(date)+"""' group by id order by name desc limit 1 """)
                            att_rec = cr.fetchall()
                            if len(att_rec) > 0 :
                                rec_id = att_rec[0][0]
                                rec_date = att_rec[0][1]
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)
                                        
                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')

                                final_time = temp + random.randrange(0,5)
                                final_date = final_date + timedelta(hours=0,minutes=final_time)
                                final_date = final_date - timedelta(hours=5,minutes=30)
                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                
                elif rec.company_id and not rec.employee_id and not rec.department_id and not rec.employment_type:
                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('company_id','=',rec.company_id.id)])
                    if len(emp_ids) > 0:
                        for val in hr_obj.browse(cr, uid, emp_ids) :
                            final_time = 0
                            cr.execute(""" select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '"""+str(val.id)+"""' and search_date =  '"""+str(date)+"""' group by id order by name desc limit 1 """)
                            att_rec = cr.fetchall()
                            if len(att_rec) > 0 :
                                rec_id = att_rec[0][0]
                                rec_date = att_rec[0][1]
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)
                                        
                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                                final_time = temp + random.randrange(0,5)
                                final_date = final_date + timedelta(hours=0,minutes=final_time)
                                final_date = final_date - timedelta(hours=5,minutes=30)
                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                                
#                elif rec.employment_type and not rec.employee_id and not rec.department_id and not rec.company_id:
#                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('employment_type','=',rec.employment_type)])
#                    if len(emp_ids) > 0:
#                        for val in hr_obj.browse(cr, uid, emp_ids) :
#                            final_time = 0
#                            cr.execute(""" select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '"""+str(val.id)+"""' and search_date =  '"""+str(date)+"""' group by id order by name desc limit 1 """)
#                            att_rec = cr.fetchall()
#                            if len(att_rec) > 0 :
#                                rec_id = att_rec[0][0]
#                                rec_date = att_rec[0][1]
#                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
#                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
#                                if prev_shift_ids:
#                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
#                                elif next_shift_ids:
#                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
#                                else:
#                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
#                                if shift_data:
#                                    for line in shift_data.shift_id.shift_line:
#                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)
#
#                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
#                                final_time = temp + random.randrange(0,5)
#                                final_date = final_date + timedelta(hours=0,minutes=final_time)
#                                final_date = final_date - timedelta(hours=5,minutes=30)
#                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                                
                elif rec.department_id and not rec.company_id : 
                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                else :
                    raise osv.except_osv(_('Warning !'),_("Please select at least one selection....!!!"))
                
                
#            elif rec.name and rec.in_punch and not rec.till_date:
#                if rec.employee_id and not rec.department_id and not rec.company_id:
#                    for val in rec.employee_id :
#                        temp = 0
#                        cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
#                        att_rec = cr.fetchall()
#                        if len(att_rec) > 0 :
#                            rec_id = att_rec[0][0]
#                            rec_date = att_rec[0][1]
#                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
#                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
#                            if prev_shift_ids:
#                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
#                            elif next_shift_ids:
#                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
#                            else:
#                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
#                            if shift_data:
#                                for line in shift_data.shift_id.shift_line:
#                                    timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
#                            final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
#                            temp = random.randrange(0,5)
#                            final_date = final_date + timedelta(hours=0,minutes=temp)
#                            final_date = final_date - timedelta(hours=5,minutes=30)
#                            cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
#                        else :
#                            raise osv.except_osv(_('Warning !'),_("No Employee Attendance record found for this Employee on this date...!!!!"))
#                elif rec.department_id and rec.company_id and not rec.employee_id : 
#                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('department_id','=',rec.department_id.id),('company_id','=',rec.company_id.id)])
#                    if len(emp_ids) > 0:
#                        for val in hr_obj.browse(cr, uid, emp_ids) :
#                            temp = 0
#                            cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
#                            att_rec = cr.fetchall()
#                            if len(att_rec) > 0 :
#                                rec_id = att_rec[0][0]
#                                rec_date = att_rec[0][1]
#                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
#                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
#                                if prev_shift_ids:
#                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
#                                elif next_shift_ids:
#                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
#                                else:
#                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
#                                if shift_data:
#                                    for line in shift_data.shift_id.shift_line:
#                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
#                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
#                                temp = random.randrange(0,5)
#                                final_date = final_date + timedelta(hours=0,minutes=temp)
#                                final_date = final_date - timedelta(hours=5,minutes=30)
#                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
#                elif rec.company_id and not rec.employee_id and not rec.department_id:
#                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('company_id','=',rec.company_id.id)])
#                    if len(emp_ids) > 0:
#                        for val in hr_obj.browse(cr, uid, emp_ids) :
#                            temp = 0
#                            cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
#                            att_rec = cr.fetchall()
#                            if len(att_rec) > 0 :
#                                rec_id = att_rec[0][0]
#                                rec_date = att_rec[0][1]
#                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
#                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
#                                if prev_shift_ids:
#                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
#                                elif next_shift_ids:
#                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
#                                else:
#                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
#                                if shift_data:
#                                    for line in shift_data.shift_id.shift_line:
#                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
#                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
#                                temp = random.randrange(0,5)
#                                final_date = final_date + timedelta(hours=0,minutes=temp)
#                                final_date = final_date - timedelta(hours=5,minutes=30)
#                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
#                elif rec.department_id and not rec.company_id : 
#                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
#                else :
#                    raise osv.except_osv(_('Warning !'),_("Please select at least one selection....!!!"))
#            elif rec.name and rec.in_punch and rec.till_date :
#                till_date = datetime.strptime(rec.till_date,'%Y-%m-%d')
#                if rec.employee_id and not rec.department_id and not rec.company_id:
#                    while (date <= till_date):
#                        for val in rec.employee_id :
#                            temp = 0
#                            cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
#                            att_rec = cr.fetchall()
#                            if len(att_rec) > 0 :
#                                rec_id = att_rec[0][0]
#                                rec_date = att_rec[0][1]
#                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
#                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
#                                if prev_shift_ids:
#                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
#                                elif next_shift_ids:
#                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
#                                else:
#                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
#                                if shift_data:
#                                    for line in shift_data.shift_id.shift_line:
#                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
#                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
#                                temp = random.randrange(0,5)
#                                final_date = final_date + timedelta(hours=0,minutes=temp)
#                                final_date = final_date - timedelta(hours=5,minutes=30)
#                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
#                        date += timedelta(days=1)     
#                elif rec.department_id and rec.company_id and not rec.employee_id :
#                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('department_id','=',rec.department_id.id),('company_id','=',rec.company_id.id)])
#                    if len(emp_ids) > 0:
#                        while (date <= till_date):
#                            for val in hr_obj.browse(cr, uid, emp_ids) :
#                                temp = 0
#                                cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
#                                att_rec = cr.fetchall()
#                                if len(att_rec) > 0 :
#                                    rec_id = att_rec[0][0]
#                                    rec_date = att_rec[0][1]
#                                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
#                                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
#                                    if prev_shift_ids:
#                                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
#                                    elif next_shift_ids:
#                                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
#                                    else:
#                                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
#                                    if shift_data:
#                                        for line in shift_data.shift_id.shift_line:
#                                            timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
#                                    final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
#                                    temp = random.randrange(0,5)
#                                    final_date = final_date + timedelta(hours=0,minutes=temp)
#                                    final_date = final_date - timedelta(hours=5,minutes=30)
#                                    cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
#                            date += timedelta(days=1) 
#                elif rec.company_id and not rec.employee_id and not rec.department_id:
#                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('company_id','=',rec.company_id.id)])
#                    if len(emp_ids) > 0:
#                        while (date <= till_date):
#                            for val in hr_obj.browse(cr, uid, emp_ids) :
#                                temp = 0
#                                cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
#                                att_rec = cr.fetchall()
#                                if len(att_rec) > 0 :
#                                    rec_id = att_rec[0][0]
#                                    rec_date = att_rec[0][1]
#                                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
#                                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
#                                    if prev_shift_ids:
#                                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
#                                    elif next_shift_ids:
#                                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
#                                    else:
#                                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
#                                    if shift_data:
#                                        for line in shift_data.shift_id.shift_line:
#                                            timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
#                                    final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
#                                    temp = random.randrange(0,5)
#                                    final_date = final_date + timedelta(hours=0,minutes=temp)
#                                    final_date = final_date - timedelta(hours=5,minutes=30)
#                                    cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
#                            date += timedelta(days=1) 
#                elif rec.department_id and not rec.company_id : 
#                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
#                else :
#                    raise osv.except_osv(_('Warning !'),_("Please select at least one selection....!!!"))
                
            
        return True


    def compute_ab_ot(self, cr, uid, ids, context=None):
        hr_obj = self.pool.get("hr.employee")
        att_obj = self.pool.get('hr.attendance')
        shift_obj = self.pool.get('hr.shift.line')
        if ids:
            rec = self.browse(cr, uid, ids)
            date = datetime.strptime(rec.name, '%Y-%m-%d')
            #            if rec.name and rec.ot_time and not rec.in_punch :
            if rec.name and rec.ot_time:
                ot_time = rec.ot_time
                data = ot_time.split('.')
                if len(data[1]) != 2:
                    raise osv.except_osv(_('Warning !'),
                                         _("Please enter the Correct Time Format (0H.MM) .....!!!!"))
                hr = int(data[0])
                min = int(data[1])
                if min > 59:
                    raise osv.except_osv(_('Warning !'), _("Minutes can not be greater than 59...!!!!"))
                temp = (hr * 60) + min

                if rec.department_id and rec.company_id and rec.employment_type and not rec.employee_id:
                    emp_ids = hr_obj.search(cr, uid,
                                            [('active', '=', True), ('department_id', '=', rec.department_id.id),
                                             ('company_id', '=', rec.company_id.id),
                                             ('employment_type', '=', rec.employment_type)])
                    if len(emp_ids) > 0:
                        for val in hr_obj.browse(cr, uid, emp_ids):
                            final_time = 0
                            cr.execute(
                                """ select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '""" + str(
                                    val.id) + """' and search_date =  '""" + str(
                                    date) + """' group by id order by name desc limit 1 """)
                            att_rec = cr.fetchall()
                            if len(att_rec) > 0:
                                rec_id = att_rec[0][0]
                                rec_date = att_rec[0][1]
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                            ('name', '<=', rec_date)], limit=1,
                                                                  order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                            ('name', '>', rec_date)], limit=1,
                                                                  order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'), _(
                                        "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                            emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)

                                final_date = datetime.strptime(timing['end_time'], '%Y-%m-%d %H:%M:%S')
                                final_time = temp + random.randrange(0, 5)
                                final_date = final_date + timedelta(hours=0, minutes=final_time)
                                final_date = final_date - timedelta(hours=5, minutes=30)
                                cr.execute(' update hr_attendance set name = %s where id = %s ',
                                           (final_date, rec_id))

                elif rec.employee_id and not rec.department_id and not rec.company_id and not rec.employment_type:
                    for val in rec.employee_id:
                        final_time = 0
                        cr.execute(
                            """ select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '""" + str(
                                val.id) + """' and search_date  =  '""" + str(
                                date) + """' group by id order by name desc limit 1 """)
                        att_rec = cr.fetchall()
                        if len(att_rec) > 0:
                            rec_id = att_rec[0][0]
                            rec_date = att_rec[0][1]
                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                        ('name', '<=', rec_date)], limit=1,
                                                              order='name DESC')
                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                        ('name', '>', rec_date)], limit=1,
                                                              order='name ASC')
                            if prev_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                            elif next_shift_ids:
                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                            else:
                                raise osv.except_osv(_('Warning !'), _(
                                    "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                        emp.sinid)))
                            if shift_data:
                                for line in shift_data.shift_id.shift_line:
                                    timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)

                            final_date = datetime.strptime(timing['end_time'], '%Y-%m-%d %H:%M:%S')
                            final_time = temp + random.randrange(0, 5)
                            final_date = final_date + timedelta(hours=0, minutes=final_time)
                            final_date = final_date - timedelta(hours=5, minutes=30)
                            cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date, rec_id))
                        else:
                            raise osv.except_osv(_('Warning !'), _(
                                "No Employee Attendance record found for this Employee on this date...!!!!"))

                elif rec.department_id and rec.company_id and not rec.employee_id and not rec.employment_type:
                    emp_ids = hr_obj.search(cr, uid,
                                            [('active', '=', True), ('department_id', '=', rec.department_id.id),
                                             ('company_id', '=', rec.company_id.id)])
                    if len(emp_ids) > 0:
                        for val in hr_obj.browse(cr, uid, emp_ids):
                            final_time = 0
                            cr.execute(
                                """ select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '""" + str(
                                    val.id) + """' and search_date =  '""" + str(
                                    date) + """' group by id order by name desc limit 1 """)
                            att_rec = cr.fetchall()
                            if len(att_rec) > 0:
                                rec_id = att_rec[0][0]
                                rec_date = att_rec[0][1]
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                            ('name', '<=', rec_date)], limit=1,
                                                                  order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                            ('name', '>', rec_date)], limit=1,
                                                                  order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'), _(
                                        "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                            emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)

                                final_date = datetime.strptime(timing['end_time'], '%Y-%m-%d %H:%M:%S')
                                final_time = temp + random.randrange(0, 5)
                                final_date = final_date + timedelta(hours=0, minutes=final_time)
                                final_date = final_date - timedelta(hours=5, minutes=30)
                                cr.execute(' update hr_attendance set name = %s where id = %s ',
                                           (final_date, rec_id))

                elif rec.employment_type and rec.company_id and not rec.employee_id and not rec.department_id:
                    emp_ids = hr_obj.search(cr, uid,
                                            [('active', '=', True), ('employment_type', '=', rec.employment_type),
                                             ('company_id', '=', rec.company_id.id)])
                    if len(emp_ids) > 0:
                        for val in hr_obj.browse(cr, uid, emp_ids):
                            final_time = 0
                            cr.execute(
                                """ select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '""" + str(
                                    val.id) + """' and search_date =  '""" + str(
                                    date) + """' group by id order by name desc limit 1 """)
                            att_rec = cr.fetchall()
                            if len(att_rec) > 0:
                                rec_id = att_rec[0][0]
                                rec_date = att_rec[0][1]
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                            ('name', '<=', rec_date)], limit=1,
                                                                  order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                            ('name', '>', rec_date)], limit=1,
                                                                  order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'), _(
                                        "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                            emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)

                                final_date = datetime.strptime(timing['end_time'], '%Y-%m-%d %H:%M:%S')
                                final_time = temp + random.randrange(0, 5)
                                final_date = final_date + timedelta(hours=0, minutes=final_time)
                                final_date = final_date - timedelta(hours=5, minutes=30)
                                cr.execute(' update hr_attendance set name = %s where id = %s ',
                                           (final_date, rec_id))

                elif rec.company_id and not rec.employee_id and not rec.department_id and not rec.employment_type:
                    emp_ids = hr_obj.search(cr, uid,
                                            [('active', '=', True), ('company_id', '=', rec.company_id.id)])
                    if len(emp_ids) > 0:
                        for val in hr_obj.browse(cr, uid, emp_ids):
                            final_time = 0
                            cr.execute(
                                """ select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '""" + str(
                                    val.id) + """' and search_date =  '""" + str(
                                    date) + """' group by id order by name desc limit 1 """)
                            att_rec = cr.fetchall()
                            if len(att_rec) > 0:
                                rec_id = att_rec[0][0]
                                rec_date = att_rec[0][1]
                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                            ('name', '<=', rec_date)], limit=1,
                                                                  order='name DESC')
                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),
                                                                            ('name', '>', rec_date)], limit=1,
                                                                  order='name ASC')
                                if prev_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                elif next_shift_ids:
                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                else:
                                    raise osv.except_osv(_('Warning !'), _(
                                        "Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (
                                            emp.sinid)))
                                if shift_data:
                                    for line in shift_data.shift_id.shift_line:
                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)

                                final_date = datetime.strptime(timing['end_time'], '%Y-%m-%d %H:%M:%S')
                                final_time = temp + random.randrange(0, 5)
                                final_date = final_date + timedelta(hours=0, minutes=final_time)
                                final_date = final_date - timedelta(hours=5, minutes=30)
                                cr.execute(' update hr_attendance set name = %s where id = %s ',
                                           (final_date, rec_id))

                                #                elif rec.employment_type and not rec.employee_id and not rec.department_id and not rec.company_id:
                                #                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('employment_type','=',rec.employment_type)])
                                #                    if len(emp_ids) > 0:
                                #                        for val in hr_obj.browse(cr, uid, emp_ids) :
                                #                            final_time = 0
                                #                            cr.execute(""" select id,max(name + interval '5 hours 30 minute') from hr_attendance where employee_id = '"""+str(val.id)+"""' and search_date =  '"""+str(date)+"""' group by id order by name desc limit 1 """)
                                #                            att_rec = cr.fetchall()
                                #                            if len(att_rec) > 0 :
                                #                                rec_id = att_rec[0][0]
                                #                                rec_date = att_rec[0][1]
                                #                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                                #                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                                #                                if prev_shift_ids:
                                #                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                                #                                elif next_shift_ids:
                                #                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                                #                                else:
                                #                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                                #                                if shift_data:
                                #                                    for line in shift_data.shift_id.shift_line:
                                #                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.to_time)
                                #
                                #                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                                #                                final_time = temp + random.randrange(0,5)
                                #                                final_date = final_date + timedelta(hours=0,minutes=final_time)
                                #                                final_date = final_date - timedelta(hours=5,minutes=30)
                                #                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))

                elif rec.department_id and not rec.company_id:
                    raise osv.except_osv(_('Warning !'), _("Please select Department along with Company"))
                else:
                    raise osv.except_osv(_('Warning !'), _("Please select at least one selection....!!!"))


                    #            elif rec.name and rec.in_punch and not rec.till_date:
                    #                if rec.employee_id and not rec.department_id and not rec.company_id:
                    #                    for val in rec.employee_id :
                    #                        temp = 0
                    #                        cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
                    #                        att_rec = cr.fetchall()
                    #                        if len(att_rec) > 0 :
                    #                            rec_id = att_rec[0][0]
                    #                            rec_date = att_rec[0][1]
                    #                            prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                    #                            next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                    #                            if prev_shift_ids:
                    #                                shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    #                            elif next_shift_ids:
                    #                                shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    #                            else:
                    #                                raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    #                            if shift_data:
                    #                                for line in shift_data.shift_id.shift_line:
                    #                                    timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
                    #                            final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                    #                            temp = random.randrange(0,5)
                    #                            final_date = final_date + timedelta(hours=0,minutes=temp)
                    #                            final_date = final_date - timedelta(hours=5,minutes=30)
                    #                            cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                    #                        else :
                    #                            raise osv.except_osv(_('Warning !'),_("No Employee Attendance record found for this Employee on this date...!!!!"))
                    #                elif rec.department_id and rec.company_id and not rec.employee_id :
                    #                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('department_id','=',rec.department_id.id),('company_id','=',rec.company_id.id)])
                    #                    if len(emp_ids) > 0:
                    #                        for val in hr_obj.browse(cr, uid, emp_ids) :
                    #                            temp = 0
                    #                            cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
                    #                            att_rec = cr.fetchall()
                    #                            if len(att_rec) > 0 :
                    #                                rec_id = att_rec[0][0]
                    #                                rec_date = att_rec[0][1]
                    #                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                    #                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                    #                                if prev_shift_ids:
                    #                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    #                                elif next_shift_ids:
                    #                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    #                                else:
                    #                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    #                                if shift_data:
                    #                                    for line in shift_data.shift_id.shift_line:
                    #                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
                    #                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                    #                                temp = random.randrange(0,5)
                    #                                final_date = final_date + timedelta(hours=0,minutes=temp)
                    #                                final_date = final_date - timedelta(hours=5,minutes=30)
                    #                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                    #                elif rec.company_id and not rec.employee_id and not rec.department_id:
                    #                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('company_id','=',rec.company_id.id)])
                    #                    if len(emp_ids) > 0:
                    #                        for val in hr_obj.browse(cr, uid, emp_ids) :
                    #                            temp = 0
                    #                            cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
                    #                            att_rec = cr.fetchall()
                    #                            if len(att_rec) > 0 :
                    #                                rec_id = att_rec[0][0]
                    #                                rec_date = att_rec[0][1]
                    #                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                    #                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                    #                                if prev_shift_ids:
                    #                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    #                                elif next_shift_ids:
                    #                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    #                                else:
                    #                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    #                                if shift_data:
                    #                                    for line in shift_data.shift_id.shift_line:
                    #                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
                    #                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                    #                                temp = random.randrange(0,5)
                    #                                final_date = final_date + timedelta(hours=0,minutes=temp)
                    #                                final_date = final_date - timedelta(hours=5,minutes=30)
                    #                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                    #                elif rec.department_id and not rec.company_id :
                    #                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                    #                else :
                    #                    raise osv.except_osv(_('Warning !'),_("Please select at least one selection....!!!"))
                    #            elif rec.name and rec.in_punch and rec.till_date :
                    #                till_date = datetime.strptime(rec.till_date,'%Y-%m-%d')
                    #                if rec.employee_id and not rec.department_id and not rec.company_id:
                    #                    while (date <= till_date):
                    #                        for val in rec.employee_id :
                    #                            temp = 0
                    #                            cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
                    #                            att_rec = cr.fetchall()
                    #                            if len(att_rec) > 0 :
                    #                                rec_id = att_rec[0][0]
                    #                                rec_date = att_rec[0][1]
                    #                                prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                    #                                next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                    #                                if prev_shift_ids:
                    #                                    shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    #                                elif next_shift_ids:
                    #                                    shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    #                                else:
                    #                                    raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    #                                if shift_data:
                    #                                    for line in shift_data.shift_id.shift_line:
                    #                                        timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
                    #                                final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                    #                                temp = random.randrange(0,5)
                    #                                final_date = final_date + timedelta(hours=0,minutes=temp)
                    #                                final_date = final_date - timedelta(hours=5,minutes=30)
                    #                                cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                    #                        date += timedelta(days=1)
                    #                elif rec.department_id and rec.company_id and not rec.employee_id :
                    #                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('department_id','=',rec.department_id.id),('company_id','=',rec.company_id.id)])
                    #                    if len(emp_ids) > 0:
                    #                        while (date <= till_date):
                    #                            for val in hr_obj.browse(cr, uid, emp_ids) :
                    #                                temp = 0
                    #                                cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
                    #                                att_rec = cr.fetchall()
                    #                                if len(att_rec) > 0 :
                    #                                    rec_id = att_rec[0][0]
                    #                                    rec_date = att_rec[0][1]
                    #                                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                    #                                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                    #                                    if prev_shift_ids:
                    #                                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    #                                    elif next_shift_ids:
                    #                                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    #                                    else:
                    #                                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    #                                    if shift_data:
                    #                                        for line in shift_data.shift_id.shift_line:
                    #                                            timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
                    #                                    final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                    #                                    temp = random.randrange(0,5)
                    #                                    final_date = final_date + timedelta(hours=0,minutes=temp)
                    #                                    final_date = final_date - timedelta(hours=5,minutes=30)
                    #                                    cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                    #                            date += timedelta(days=1)
                    #                elif rec.company_id and not rec.employee_id and not rec.department_id:
                    #                    emp_ids = hr_obj.search(cr, uid, [('active','=',True),('company_id','=',rec.company_id.id)])
                    #                    if len(emp_ids) > 0:
                    #                        while (date <= till_date):
                    #                            for val in hr_obj.browse(cr, uid, emp_ids) :
                    #                                temp = 0
                    #                                cr.execute(""" select id,min(name) from hr_attendance where employee_id = '"""+str(val.id)+"""' and cast(name as date) =  '"""+str(date)+"""' group by id order by name asc limit 1 """)
                    #                                att_rec = cr.fetchall()
                    #                                if len(att_rec) > 0 :
                    #                                    rec_id = att_rec[0][0]
                    #                                    rec_date = att_rec[0][1]
                    #                                    prev_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '<=',rec_date)], limit=1, order='name DESC')
                    #                                    next_shift_ids = shift_obj.search(cr, uid, [('employee_id', '=', val.id),('name', '>',rec_date)], limit=1, order='name ASC')
                    #                                    if prev_shift_ids:
                    #                                        shift_data = shift_obj.browse(cr, uid, prev_shift_ids)[0]
                    #                                    elif next_shift_ids:
                    #                                        shift_data = shift_obj.browse(cr, uid, next_shift_ids)[0]
                    #                                    else:
                    #                                        raise osv.except_osv(_('Warning !'),_("Shift is missing for employee %s, shift date must be less or equal to synchronize date." % (emp.sinid)))
                    #                                    if shift_data:
                    #                                        for line in shift_data.shift_id.shift_line:
                    #                                            timing = self.calculate_time(cr, uid, ids, rec_date, line.from_time)
                    #                                    final_date = datetime.strptime(timing['end_time'],'%Y-%m-%d %H:%M:%S')
                    #                                    temp = random.randrange(0,5)
                    #                                    final_date = final_date + timedelta(hours=0,minutes=temp)
                    #                                    final_date = final_date - timedelta(hours=5,minutes=30)
                    #                                    cr.execute(' update hr_attendance set name = %s where id = %s ', (final_date,rec_id))
                    #                            date += timedelta(days=1)
                    #                elif rec.department_id and not rec.company_id :
                    #                    raise osv.except_osv(_('Warning !'),_("Please select Department along with Company"))
                    #                else :
                    #                    raise osv.except_osv(_('Warning !'),_("Please select at least one selection....!!!"))

        return True
