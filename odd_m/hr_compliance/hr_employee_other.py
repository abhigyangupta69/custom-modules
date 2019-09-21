import time
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import base64
import time
import csv
import os

class holiday_year(osv.osv):
    _name="holiday.year"
    
    _columns={
              'name':fields.char("Year")
              }

class qualification_list(osv.osv):
    _name="qualification.list"
    _columns = {
                'name':fields.char('Name',required=True,select=True),
                }

class icard_history(osv.osv):
    _name="icard.history"
    
    _columns={
             'employee_id':fields.many2one('hr.employee','Icard'),
             'date':fields.datetime('Creation Date',readonly=True),
             'card_name':fields.char('Name Of Card',readonly=True),
             'user_id': fields.many2one('res.users', 'Responsible',readonly=True),
               }
    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               }
    
    
    
# class hr_shift_line(osv.osv):
#     _name="hr.shift.line"
#     
#     _columns={
#              'employee_id':fields.many2one('hr.employee','Icard'),
#              'date':fields.datetime('Creation Date'),
#              'card_name':fields.char('Name Of Card'),
#              'user_id': fields.many2one('res.users', 'User By'),
#                }
#     _defaults={
#                'user_id': lambda obj, cr, uid, context: uid,
#                }
# class attendance_shift(osv.osv):
#     _name = 'attendance.shift'
#     
#     _columns = {
#                 'name':fields.char('Name',required=True),
#                 'date':fields.date('Date',required=True),
#                 'user_id':fields.many2one('res.users','Created By',readonly=True),
#                 }
#     _defaults={
#                'user_id': lambda obj, cr, uid, context: uid,
#                }


class attendance_shift(osv.osv):
    _name = 'attendance.shift'  
    _columns = {
                'name':fields.char('Name',required=True,select=True),
                'date':fields.date('Date',required=True),
                'active': fields.boolean('Active', help="By unchecking the active field, you may hide a location without deleting it."),
                'shift_line':fields.one2many('attendance.shift.line','shift_id','Shift line'),
                'user_id':fields.many2one('res.users','Created By',readonly=True),
                'shift_history_id':fields.one2many('attendance.shift.history','history_id','Active Shift History'),
                'shift_name':fields.char('Shift Name',required=True,size=8),
                }
    _defaults={
               'active':True,
               'user_id': lambda obj, cr, uid, context: uid,
               }

    def create(self, cr, uid, vals, context=None):
        act_obj = self.pool.get('attendance.shift.history')
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].strip()
            vals['name'] = vals['name'].upper()
        res = super(attendance_shift,self).create(cr, uid, vals, context)
        if res:
            act_obj.create(cr, uid, {'history_id':res,'name':'Active','date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,})
             
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res={}
        act_obj = self.pool.get('attendance.shift.history')
        if 'active' in vals:
            if vals['active']:
                a= act_obj.create(cr, uid, {'history_id':ids[0],'name':'Active','date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid})
            else:
                a=act_obj.create(cr, uid, {'history_id':ids[0],'name':'In Active','date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid})       
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
            timing = self.pool.get('wiz.attendance').calculate_time(cr, uid, ids, date, each.from_time, each.to_time)
            working = timing.get('working_hour',0.0)
            res[each.id]=working
        return res
    
    _columns = {
                'type':fields.selection([('morning','Morning'),('evening','Evening'),('night','Night')],'Shift',required=True),
                'case':fields.selection([('Labour','Labour'),('Staff','Staff'),('Guard','Guard')],'Cases',),
                'from_time':fields.float('From Time',required=True),
                'to_time':fields.float('To Time',required=True),
                'shift_id':fields.many2one('attendance.shift','Shift',ondaelete="cascade"),
                'working_time':fields.function(_calculate_time,method=True,store=True,string="Working Time",type="float"),
                'user_id':fields.many2one('res.users','Created By',readonly=True),
                'lunch_start_time':fields.float('Lunch Start Time',required=True),
                'lunch_end_time':fields.float('Lunch End Time',required=True),
                'lunch_time':fields.integer('Lunch Time',required=True),
                }

    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               }
    
class attendance_shift_history(osv.osv):
    _name='attendance.shift.history'
    _columns={
              'name':fields.char('Status',size=64),
              'user_id':fields.many2one('res.users','Responsible'),
               'date':fields.datetime('Date'),
               'history_id':fields.many2one('attendance.shift','History')
               }
    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               }
         

class hr_shift_line(osv.osv):
    _name = "hr.shift.line"
    
    def update_shift(self, cr, uid, ids, context=None):
        shift_line = self.browse(cr, uid, ids, context=context) 
        query = """ SELECT DISTINCT ON (emp.id)  emp.id, shift.shift_id as shift FROM  hr_employee as emp JOIN 
                  hr_shift_line as shift ON emp.id = shift.employee_id ORDER BY emp.id,shift.create_date DESC """
        cr.execute(query)
        shift = cr.fetchall()  
        for val in shift:
            a = cr.execute("""update hr_employee set shift_id=%s where id=%s  """, (val[1],val[0]))
        return True

    _columns = {
                'employee_id':fields.many2one('hr.employee','Employee'),
                'name':fields.date('Date'),
                'shift_id':fields.many2one('attendance.shift','Shift'),
                'sinid':fields.related('employee_id','sinid',relation='hr.employee',string='PCard',type="char",readonly=True,store=True),
                'employee_name':fields.related('employee_id','name',relation='hr.employee',string='Employee Name',type="char",readonly=True,store=True),
                'department_id':fields.related('employee_id','department_id',relation='hr.department',string='Department',type="many2one",readonly=True,store=True),
                'company_id':fields.related('employee_id','resource_id','company_id',relation='res.company',string='Company Name',type='many2one',store=True,method=True,readonly=True),
                'type':fields.related('employee_id','type',selection=[('Employee','Employee'),('Contractor','Contractor')],string='Type',type="selection",store=True),
                'job_id':fields.related('employee_id','job_id',relation='hr.job',string='Designation',type="many2one",readonly=True,store=True),
                'active':fields.related('employee_id','resource_id','active',relation='resource.resource',string='Active',type="boolean",store=True),
                'doj':fields.related('employee_id','doj',relation='hr.employee',string='Date of Joining',type="date",store=True),
                'employment_type':fields.related('employee_id','employment_type',selection=[('Employee','Employee'),('Labor','Labor')],string='Employment Type',type="selection",store=True),
                'user_id':fields.many2one('res.users','Created By',readonly=True),
                }
    _defaults={
               'name':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
               'user_id': lambda obj, cr, uid, context: uid,
               }

    def create(self, cr, uid, vals, context=None):
        obj=False
        
#        if 'name' in vals and vals['name']:
#            if datetime.strptime(vals['name'],'%Y-%m-%d') > datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),'%Y-%m-%d'):
#                raise osv.except_osv(_('Warning!'),_("Shift date cannot be greater than today's date."))
            
        if 'name' in vals and vals['name'] and 'employee_id' in vals and vals['employee_id'] :
            obj=self.search(cr,uid,[('name','=',vals['name']),('employee_id','=',vals['employee_id'])])
            if obj:
                raise osv.except_osv(_('Warning!'),_("Record already exists for this date"))            
                
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
            change_emp = self.pool.get('hr.employee').search(cr, uid, [('id','=',vals['employee_id'])])
            emp_id = self.browse(cr,uid,ids[0]).employee_id.id
            shift_id = self.browse(cr,uid,ids[0]).shift_id.id
            last_shift = self.search(cr, uid, [('employee_id','=',emp_id)], limit=2, order='name DESC')
            last_shift_id = self.browse(cr, uid, last_shift[1])
            if shift_date:
                obj=self.search(cr,uid,[('name','=',shift_date),('employee_id','=',vals['employee_id'])])
                if obj:
                    raise osv.except_osv(_('Invalid  Name'), _('shift already exists for this date'))
                else:
                    self.pool.get('hr.employee').write(cr, uid, [change_emp[0]],{'shift_id':shift_id})
                    self.pool.get('hr.employee').write(cr, uid, [emp_id],{'shift_id':last_shift_id.shift_id.id})
        res = super(hr_shift_line,self).write(cr, uid, ids, vals)
        return res    

class verification(osv.osv):
    _name = "verification"
    
    _columns = {
                'employee_id':fields.many2one('hr.employee','Employee'),
                'proof_id':fields.selection([('Passport','Passport'),('Bank_ Account_ No','Bank_Account_No.'),('Voter_ID','Voter_ID'),('Aadhar_Card','Aadhar_Card'),('DL','DL'),('PAN_Card','PAN_Card'),('Other','Other')],"ID",required=True),
                'id_no':fields.char('ID No/ Account No'),
                'name':fields.char('Name on ID '),
                'copy_name':fields.boolean('Copy'),
                 'remark':fields.char('Remark'),
                'verify':fields.boolean('Verify',size=45),
#                 'user_id':fields.many2one('res.users','User',readonly=True ),
                'ifsc_code':fields.many2one('res.bank','IFSC Code' ,invisibe=True),
                'bank_name':fields.char('Bank Name',size=60,invisible=True),
                'bank_address':fields.char('Bank Address',size=100)
                
                }
#     _defaults = {
#                 'user_id': lambda obj, cr, uid, context: uid,
#                  }
#     
    def onchange_copy(self, cr, uid, ids, val1, val, context=None):
        res = {}
        if val1:
            res['value'] = {'name' : val}
       
        return res
    
    
    def onchange_ifsc_code(self, cr, uid, ids,ifsc_code, context=None):
        print " proff id===================",ifsc_code
        res={}
        if ifsc_code:
            bank_browse=self.pool.get('res.bank').browse(cr,uid,ifsc_code)
            if bank_browse :
                bank_name=bank_browse.name
                street_add=bank_browse.street
                city_name=bank_browse.city
                if street_add and city_name :
                    bank_add= street_add + ',' + city_name
                    res['value'] = {'bank_name' : bank_name,'bank_address':bank_add}
                elif  street_add :
                     bank_add= street_add  
                     res['value'] = {'bank_name' : bank_name,'bank_address':bank_add}
                elif city_name:
                     bank_add= city_name 
                     res['value'] = {'bank_name' : bank_name,'bank_address':bank_add}
        return res
    
    
    
    
    

class hr_active_history(osv.osv):
    _name = 'hr.active.history'
    _columns = {
                'name':fields.char('Change To',size=64,readonly=True),
                'date':fields.datetime('Date',readonly=True),
                'user_id':fields.many2one('res.users','Responsible',readonly=True),
                'employee_id':fields.many2one('hr.employee','Employee',readonly=True),
                'previous_id':fields.char('Old Paycode',size=34,readonly=True),
                'current_id':fields.char('New Paycode',size=67,readonly=True),
                'previous_designtation':fields.char('Old Designation',size=34,readonly=True),
                'current_designation':fields.char('New Designation',size=34,readonly=True),
                'previous_dept':fields.char('Previous Department',size=34,readonly=True),
                'current_dept':fields.char('Current Department',size=34,readonly=True),
                }
    
class earn_leave_history(osv.osv):
    _name = 'earn.leave.history'
     
    _columns = {
                'name':fields.date('Date',readonly=True),
                'prev_earn':fields.integer("Previous Earn",readonly=True),
                'curr_earn':fields.integer("Current Earn",readonly=True),
                'user_id':fields.many2one('res.users','User',readonly=True),
                'employee_id':fields.many2one('hr.employee','Employee'),
                }

class employee_salary_category(osv.osv):
    _name="employee.salary.category"
    
    _columns={
               'category':fields.selection([('Skilled','Skilled'),('UnSkilled','UnSkilled'),('Semi_Skilled','Semi_Skilled')],"Category",required=True),
               'date':fields.date('Date',required=True),
               'salary':fields.float('Salary',required=True),
               'bonus_limit':fields.float('Bonus Limit',required=True),
               'user_id':fields.many2one('res.users','User',readonly=True),
               'employee_salary_category_line_id':fields.one2many('employee.salary.category.line','employee_salary_category_id','Employee Category Line'),
               'name':fields.char('Name',size=100),
               }
    
    def create(self, cr, uid, vals, context=None):
        res ={}
        res = super(employee_salary_category,self).create(cr, uid ,vals, context=context)
        employee = self.browse(cr,uid,res)
        self.pool.get('employee.salary.category.line').create(cr, uid,{'date':employee.date,'salary':employee.salary,'user_id':uid,'employee_salary_category_id':employee.id})
        
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = {}
        l=self.browse(cr,uid,ids[0])
        res = super(employee_salary_category,self).write(cr, uid ,ids,vals, context=context)
        for employee in self.browse(cr, uid, ids):
            self.pool.get('employee.salary.category.line').create(cr, uid,{'date':employee.date,'salary':employee.salary,'user_id':uid,'employee_salary_category_id':employee.id})

        return res
    
    _defaults={
                'user_id': lambda obj, cr, uid, context: uid,
                'date':lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                 }
  
    
class employee_salary_category_line(osv.osv):
    _name="employee.salary.category.line"
  
    _columns={
               'employee_salary_category_id':fields.many2one('employee.salary.category','Category'),
               'date':fields.date('Date',readonly=True),
               'salary':fields.float('Salary',readonly=True),
               'user_id':fields.many2one('res.users','User',readonly=True),
               }
    
    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               }
    
class check_aadhaar_duplicacy(osv.osv):
    _name="check.aadhaar.duplicacy"

    _columns = {
                'name':fields.char(string='Aadhaar Number',size=12),
                'check_history_ids':fields.one2many('check.aadhaar.duplicacy.history' ,"aadhaar_id", string="CHECK AADHAAR HISTORY",readonly=True),
                'uan_name':fields.char(string='UAN',size=64),
                'uan_history_line_id':fields.one2many('uan.duplicacy.history.line' ,"uan_id", string="CHECK UAN HISTORY",readonly=True),
                }
    
    
    def check_duplicacy(self, cr, uid, ids, context=None):
        res = self.browse(cr,uid,ids[0])
        aadhaar_history_obj=self.pool.get('check.aadhaar.duplicacy.history')
        if res:
            aadhaar_no=str(res.name)
            if len(aadhaar_no) < 12 :
                 raise osv.except_osv(_('ALERT !'),_("AADHAAR CARD NO LENGHTH SHOULD NOT BE LESS THAN 12 ,Currently Length  %s " % (len(aadhaar_no))))
            if " " in aadhaar_no :
                 raise osv.except_osv(_('Mistake !'),_('Spaces are not allowed in AADHAAR CARD No'))                        
            query="select verf.id,hr.sinid,rr.name,hr.doj,rr.active,comp.name from verification as verf left join hr_employee as hr on verf.employee_id=hr.id left join resource_resource as rr on rr.id=hr.resource_id left join res_company as comp on rr.company_id=comp.id  where verf.proof_id  = 'Aadhar_Card' and verf.id_no  = '"+str(aadhaar_no)+"' "
            cr.execute(query)
            aadhaar_temp=cr.fetchall()
            if aadhaar_temp :
                for val in aadhaar_temp :
                    cr.execute('insert into check_aadhaar_duplicacy_history (name,user_id,aadhaar_no,result,aadhaar_id) values (%s,%s,%s,%s,%s)', (time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),uid,aadhaar_no,'Duplicacy Found',ids[0]))
                    cr.commit()
                    raise osv.except_osv(_('Warning !'),_("AADHAR CARD ALREADY EXIST FOR Card NO %s ,Employee NAME %s , Doj  %s , Company Name %s ,ACTIVE  %s " % (val[1],val[2],val[3],val[5],val[4])))
            else:
                    cr.execute('insert into check_aadhaar_duplicacy_history (name,user_id,aadhaar_no,result,aadhaar_id) values (%s,%s,%s,%s,%s)', (time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),uid,aadhaar_no,'FRESH AADHAAR CARD NUMBER',ids[0]))
                    cr.commit()
                    raise osv.except_osv(_('Congratulation !'),_("THIS AADHAR CARD NO %s,  IS FRESH AND READY TO USE " % (aadhaar_no)))
        return True 

    def check_uan_duplicacy(self, cr, uid, ids, context=None):
        res = self.browse(cr,uid,ids[0])
        aadhaar_history_obj=self.pool.get('uan.duplicacy.history.line')
        if res:
            uan_no=str(res.uan_name)
            query="select hr.sinid,rr.name,hr.doj,rr.active,comp.name from hr_employee as hr left join resource_resource as rr on rr.id=hr.resource_id left join res_company as comp on rr.company_id=comp.id  where hr.uan  = '"+str(uan_no)+"' "
            cr.execute(query)
            uan_temp=cr.fetchall()
            if uan_temp :
                for val in uan_temp :
                    cr.execute('insert into uan_duplicacy_history_line (name,user_id,uan,result,uan_id) values (%s,%s,%s,%s,%s)', (time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),uid,uan_no,'Duplicacy Found',ids[0]))
                    cr.commit()
                    raise osv.except_osv(_('Warning !'),_("UAN ALREADY EXIST FOR Card NO %s ,Employee NAME %s , Doj  %s , Company Name %s ,ACTIVE  %s " % (val[0],val[1],val[2],val[4],val[3])))
            else:
                    cr.execute('insert into uan_duplicacy_history_line (name,user_id,uan,result,uan_id) values (%s,%s,%s,%s,%s)', (time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),uid,uan_no,'FRESH UAN NUMBER',ids[0]))
                    cr.commit()
                    raise osv.except_osv(_('Congratulation !'),_("THIS UAN NO %s,  IS FRESH AND READY TO USE " % (uan_no)))
        return True 
    
class uan_duplicacy_history_line(osv.osv):
    _name="uan.duplicacy.history.line"

    _columns = {
                'name':fields.datetime(string='Check Date'),
                'user_id':fields.many2one('res.users','User'),
                'uan_id':fields.many2one('check.aadhaar.duplicacy','Check UAN ID'),
                'uan':fields.char('UAN',size=256),
                'result':fields.char('RESULT',size=256)
                } 

class check_aadhaar_duplicacy_history(osv.osv):
    _name="check.aadhaar.duplicacy.history"

    _columns = {
                'name':fields.datetime(string='Check Date'),
                'user_id':fields.many2one('res.users','User'),
                'aadhaar_id':fields.many2one('check.aadhaar.duplicacy','Check AADHAAR ID'),
                'aadhaar_no':fields.char('AADHAAR NO',size=256),
                'result':fields.char('RESULT',size=256)
                } 

class import_emp_uan_details(osv.TransientModel):
    _name="import.emp.uan.details"
    
    _columns={
              'file':fields.binary('Upload File'),
              'file_format':fields.text("File's Format",readonly=True),
              'date':fields.date("Uploading Date"),
              }
    
    _defaults={
               }
    
    
    def file_upload(self,cr,uid,ids,context=None):
        res={}
        file=self.browse(cr,uid,ids)[0].file
        string=base64.decodestring(file)
        fp=open("/tmp/uan.csv",'wb')
        fp.write(string)
        fp.close()
        emp_obj=self.pool.get('hr.employee')
        data=csv.reader(open('/tmp/uan.csv'), delimiter=',', quotechar='"')
        obj=self.browse(cr,uid,ids[0])
        for row in data:
            pf_no=''
            if row[0]:
                emp_search = self.pool.get('hr.employee').search(cr,uid,[('sinid','=',row[0]),('active','=',True)])
                if emp_search:
                     emp_browse=emp_obj.browse(cr,uid,emp_search[0]).pf_number
                     if emp_browse :
                         pf_no=str(emp_browse)+str(row[2])
                     emp_obj.write(cr, uid, emp_search,{'uan': row[1],'pf_number': pf_no})
                else:
                    raise osv.except_osv(_('Warning !'), _('This Card No is Either Wrong or InActive  %s'%(row[0])))
                
        os.remove("/tmp/uan.csv")
        return {'type':'ir.actions.act_window_close'}  
    
    
          
       
