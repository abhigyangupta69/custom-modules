import time
import re
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import psycopg2


class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _order = 'sinid'
    
#     def _get_user_id(self, cr, uid, context=None):
#         usr_obj = self.pool.get('res.users')
#         comp_id = usr_obj.browse(cr, uid, uid,context=None).company_id.id
#         rec_id = usr_obj.search(cr, uid,[('company_id','=',comp_id),('login','ilike','hr')])
#         if len(rec_id) > 0 :
#             return rec_id[0]
#         return False
        
    
    _columns = {
                'father_name':fields.char("Father Name"),
                'category_ids': fields.many2many('hr.employee.category', 'employee_category_rel', 'emp_id', 'category_id', 'Designation'),
                'sinid':fields.char("Employee Code"),
                'paycode':fields.char("Punch Code"),
                'joining_salary':fields.float("Joining Salary"),
                'current_salary':fields.float("Basic+DA"),
                'age':fields.integer("Age"),
                'category':fields.selection([('Skilled','Skilled'),('UnSkilled','UnSkilled'),('Semi_Skilled','Semi_Skilled')],"Category"),
                'religion':fields.selection([('Hindu','Hindu'),('Muslim','Muslim'),('Sikh','Sikh'),('Isai','Isai'),('Other','Other')],"Religion"),
                'employee_nominee_ids':fields.one2many('employee.nominee','employee_id',"Nominee Information"),
                'permanent_add':fields.char("Permanent Address"),
                'local_add':fields.char("Local Address"),
                'education_id':fields.one2many('qualification','employee_id',"Qualification"),
                'experience_id':fields.one2many('experience','employee_id',string = 'Experience'),
                'reference_id':fields.one2many('reference','employee_id',string="Reference"),
                'verf_id':fields.one2many('verification','employee_id',string="Verification"),
                'family_id':fields.one2many('family','employee_id',string="Family"),
                'increment_id':fields.one2many('increment','employee_id',string="Increment"),
                'icard_history':fields.one2many('icard.history','employee_id',string="Icard",readonly=True),
                'shift_lines':fields.one2many('hr.shift.line','employee_id',string="Icard"),
                'promotion_id':fields.one2many('promotion','employee_id',string="Promotion"),
                'mark':fields.text("Identification Mark"),
                'doa':fields.date("Date of App."),
                'doc':fields.date("Date of Ref. Check"),
                'doj':fields.date("Date of Joining"),
                'weight':fields.char("Weight (in kg)"),
                'height':fields.char("Height (in cm)"),
                'blood':fields.char("Blood Group"),
                'app_review':fields.many2one("hr.employee","App Reviewed By"),
                'ref_check1':fields.many2one("hr.employee","Ref.Check Conducted By"),
                'gap' : fields.char("Reason for Gap"),
                'copy_add' : fields.boolean("Copy Address"),
                'uan' : fields.char("UAN"),
                'pf_number' : fields.char("PF Number"),
                'esi_number' : fields.char("ESI Number"),
                'job_id': fields.many2one('hr.job', 'Job Title'),
                'ot_tick':fields.boolean("OT Tick"),
                'earn_leave':fields.integer("Earned Leaves",readonly=True),
                'earn_date':fields.date("Earn Date",readonly=True),
                'epf_tick':fields.boolean("EPF Tick"),
                'esi_tick':fields.boolean("ESI Tick"),
                'week':fields.selection([('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')],'Week',required=True),
                'comp_user_id':fields.many2one('res.users',string="Compliance User"),
                'admin_user_id':fields.many2one('res.users',string="Admin User"),
                'history_act_ids':fields.one2many('hr.active.history','employee_id','Active History',readonly=True),
                'mobile_phone': fields.char('Mobile No.', readonly=False),
                'department_id': fields.many2one('hr.department', 'Department'),
                'history_earn_ids':fields.one2many('earn.leave.history','employee_id','Active History',readonly=True),
                'earn_open':fields.integer('Open Earned Leave',readonly=True),
                'holiday_status_ids':fields.one2many("employee.leave.allocation", "employee_id", string="Leave Allocation",required=True),
                'comp_transfer_ids':fields.one2many('company.transfer.history' ,"employee_id",string="Company Transfer",required=True),
                'tick_history_ids':fields.one2many('hr.tick.history' ,"employee_id", string="HR TICK HISTORY",readonly=True),
                'leaving_reason':fields.selection([('Death','Death'),('Retire','Retire'),('Resigned','Resigned')],"Reason For Leaving"),
                'epf_start_date':fields.date('EPF Start Date',required=True,),
                'state':fields.selection([('Draft','Draft'),('Done','Done')],'State'),
                'epf_end_date':fields.date('EPF Exit Date',required=True,),
                'employee_type':fields.selection([('Staff','Staff'),('Worker','Worker')],'Employee Type'),
                'employment_type':fields.selection([('Employee','Employee'),('Labor','Labor'),('Trainee','Trainee')],'Employment Type'),
                'hra':fields.float("HRA"),
                'conveyance':fields.float("Conveyance"),
                'medical':fields.float("Medical"),
                'special_allowance':fields.float("Special Allowance"),
                'total_salary':fields.float("Current Salary"),
                'other_salary':fields.float("Other"),
                'type':fields.selection([('Employee','Employee'),('Contractor','Contractor')],'Type'),
                'partner_id':fields.many2one("res.partner","Contractor"),
                'app_review_cont':fields.many2one("res.partner","App Reviewed By"),
                'ref_check1_cont':fields.many2one("hr.employee","Ref.Check Conducted By"),
                'app_review_by':fields.char("App Reviewed By",size=2056),
                'ref_check_by':fields.char("Ref.Check Conducted By",size=2056),
                'app_review_contractor':fields.char("App Reviewed Contractor",size=4112),
                'uan_tick':fields.boolean("UAN Tick"),
                'shift_id':fields.many2one('attendance.shift','Shift'),
                }
    _defaults={
#                'user_id': lambda obj, cr, uid, context: uid,
               'country_id':105,'category_ids':[(4, 16,0)],
               'week':'Sunday',
               'admin_user_id': 1,
               'state':'Draft'
#                'epf_start_date':_get_epf_date
#                'comp_user_id': _get_user_id,
               }
    
    _sql_constraints=[
                      ('emp_uniq_sinid', 'unique(sinid)', 'Employee Code must be Unique...!!!'),
                       ('emp_uniq_paycode', 'unique(paycode)', 'Employee Pay Code must be Unique...!!!'),
                      ]

    
    def create_duplicate_employee(self, cr, uid, ids, context=None):
        res = self.browse(cr,uid,ids[0])
        paycode = res.paycode
        old_paycode = 'DUP' + paycode[3:8]
        self.write(cr, uid, ids, {'paycode':old_paycode })
        print " ======pay code =========",paycode,old_paycode
        emp_id = self.copy(cr, uid, ids[0], default={'sinid':'',
                                                     'paycode':paycode,
                                                     'company_id':'',
                                                     'user_id':'',
                                                     'comp_user_id':'',
                                                     'doj':False,
                                                     'earn_leave':0,
                                                     'joining_salary':0,
                                                     'current_salary':0,
                                                     'earn_open':0,
                                                     'doa':False,
                                                     'doc':False,
                                                     'app_review_by':'',
                                                     'ref_check_by':'',
                                                     'epf_start_date':False,
                                                     'earn_date':False,
                                                     'remaining_leaves':0,
                                                     'increment_id':False,
                                                     'promotion_id':False,
                                                     'reference_id':False,
                                                     'comp_transfer_ids':False,
                                                     'history_earn_ids':False,
                                                     'tick_history_ids':False,
                                                     'icard_history':False,
                                                     'shift_lines':False,
                                                     'holiday_status_ids':False,
                                                     'app_review_contractor':'',}, context=context)                                     
        
        if res.family_id :
            for val1 in res.family_id :
                self.pool.get('family').copy(cr, uid, val1.id, default={'employee_id':emp_id, 'user_id':uid})
        if res.education_id :
            for val2 in res.education_id :
                self.pool.get('qualification').copy(cr, uid, val2.id, default={'employee_id':emp_id, 'user_id':uid})   
        if res.experience_id :
            for val3 in res.experience_id :
                self.pool.get('experience').copy(cr, uid, val3.id, default={'employee_id':emp_id, 'user_id':uid})
        if res.verf_id :
            for val4 in res.verf_id :
                self.pool.get('verification').copy(cr, uid, val4.id, default={'employee_id':emp_id})
        
        model_str=''
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr', 'view_employee_form')
        view_id = view_ref and view_ref[1] or False,
        return {
                'type': 'ir.actions.act_window',
                'name': model_str,
                'res_model': 'hr.employee',
                'res_id': emp_id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id[0],
                'target': 'current',
                'nodestroy': True,
               }
    
    def roger(self,cr,uid,ids,context=None):
        if ids:
            qry = " select sinid, ear_open from earn_data"
            cr.execute(qry)
            data=cr.fetchall()
            print "dataaaaaaaaaaaaaaaa",data,
            for val in data:
                value = val[0].strip(' ')
                hr_id = self.search(cr, uid, [('sinid','=',value)])
                self.write(cr, uid, hr_id,{'earn_leave': val[1],'earn_open': val[1]})
        return True
    
    def roger1(self,cr,uid,ids,context=None):
        emp_id = self.search(cr, uid, [('active','=',True)])
        count = 0
        for val in emp_id :
            value=0
            hol_ids = self.pool.get('hr.holidays').search(cr, uid, [('holiday_type','=','employee'),('month','=',6),('employee_id','=',val),('type','=','remove'),('state','=','validate'),('holiday_status_id','=',5)])
            if hol_ids:
                for vals in self.pool.get('hr.holidays').browse(cr, uid,hol_ids):
                    value = value + vals.number_of_days_temp
                earn = self.browse(cr,uid,val).earn_leave - value
                count = count +1
                self.write(cr, uid, [val], {'earn_leave':earn })
                print "vals.number_of_days_temp,value,earn",vals.number_of_days_temp,value,earn
        print "countttttttttttttttttttttttttt",count
        return True
    
    
    
    
    def onchange_epf_tick(self,cr,uid,ids,epf_tick,doj,context):
        res={}
        if epf_tick == True :
            query="select leave_date from holiday_list_lines"
            cr.execute(query)
            temp=cr.fetchall()
            return {'value': {'epf_start_date':doj,}}
            raise osv.except_osv(_('Alert'), _('Please Check The EPF Date !!!!')) 
            
            
 
            
    
    def onchange_doa(self,cr,uid,ids,doa,context=None):
        if doa:
            query="select leave_date from holiday_list_lines"
            cr.execute(query)
            temp=cr.fetchall()
            for val in temp:
                if doa==val[0]:
                     raise osv.except_osv(_('Invalid Date'), _('This Date contains a holiday !!!!'))
        return True
    
    def onchange_doc(self,cr,uid,ids,doc,context=None):
        if doc:
            query="select leave_date from holiday_list_lines"
            cr.execute(query)
            temp=cr.fetchall()
            for val in temp:
                if doc==val[0]:
                     raise osv.except_osv(_('Invalid Date'), _('This Date contains a holiday !!!!'))
        return True
    
#    def onchange_doj(self,cr,uid,ids,doj,context=None): 
#        res = {}
#        r = []
#        if doj:
#            r.append({'name': doj,'shift_id':1,})
#            res['value'] = {'shift_lines' : r}      
#            return res
#        return res
   
  
    def onchange_company(self, cr, uid, ids, company,context=None):
        pf_num = False
        if company:
            company_id = self.pool.get('res.company').browse(cr, uid, company, context=context)
            reg_code = company_id.regional_code
            offce_code = company_id.office_code
            estab_id = company_id.estab_id
            if reg_code and offce_code and estab_id : 
                pf_num = reg_code + offce_code + estab_id + '/'
                
            rec_id = self.pool.get('res.users').search(cr, uid,[('company_id','=',company),('id','!=',1)])
            rec_hr_id = self.pool.get('res.users').search(cr, uid,[('company_id','=',company),('login','like','hr-')])
            if rec_hr_id:
                for val in rec_id : 
                    if val ==  rec_hr_id[0] : 
                       comp_user_id = val
                       user_id = rec_id[1]
                       break
                    else : 
                       comp_user_id = rec_id[1]
                       user_id = rec_id[0]
                       break 
                return {'value': {'pf_number':pf_num,'comp_user_id':comp_user_id,'user_id':user_id}}
        
        
    def copy_address(self,cr,uid,ids,permanent_add,context=None):
        res = {}
        if permanent_add :
                res['value'] =  {'local_add' : permanent_add}
        return res
    
    
    
    def onchange_birthday(self,cr ,uid,ids,birthday,doj,context=None):
        res={}
        r = []
        if doj:
            date1=birthday
            date2= doj
            if date1:
                if date1 >= date2:
                    raise osv.except_osv(_('Invalid Date'), _('Please enter a valid  Date !'))
                days=(datetime.strptime(date2,"%Y-%m-%d").date()-datetime.strptime(date1,"%Y-%m-%d").date()).days
                if days >= 6574:
                     dob = datetime.strptime(birthday, "%Y-%m-%d")
                     doj=datetime.strptime(date2, "%Y-%m-%d")   
                     rdelta = relativedelta(doj, dob)
                     age_calc= rdelta.years
                     r.append({'name': doj,'shift_id':1,}) 
                     res['value'] = {'age' : age_calc,'shift_lines' : r,'shift_id':1}
                     return res   
                else:
                    raise osv.except_osv(_('Invalid Date'), _('Please enter a valid  Date Of Birth (Minimum 18 years) !'))
        return res
    
    def name_get(self, cr, user, ids, context=None):
        
        if context is None:
            context = {}
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name','')
            code = d.get('sinid',False)
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)

        result = []
        for emp in self.browse(cr, user, ids, context=context):
            mydict = {
                      'id': emp.id,
                      'name': emp.name,
                      'sinid': emp.sinid,
                      }
            result.append(_name_get(mydict))
        return result
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('sinid','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('name','=',name)]+ args, limit=limit, context=context)
                
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('sinid',operator,name)], limit=limit, context=context))
                if len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit-len(ids)), context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('sinid','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
    def create(self, cr, uid, vals, context=None):
        act_obj = self.pool.get('hr.active.history')
        str1="^-?[a-z0-9A-Z0-9]+([a-z0-9-])+$"
        if 'sinid' in vals and vals['sinid']:
            vals['sinid'] = vals['sinid'].strip()
            vals['sinid'] = vals['sinid'].replace(' ','')
            if re.match(str1,vals['sinid']) == None:
                raise osv.except_osv(_('Warning!'),_('Only alphanumeric and - sign is allowed in permanent card number.'))
            if len(vals['sinid'].split('-')) > 2:
                raise osv.except_osv(_('Warning!'),_('Only single - sign is allowed in permanent card number.'))
            vals['sinid'] = vals['sinid'].upper()
            if len(vals['sinid']) < 4:
                raise osv.except_osv(_('Warning!'),_('Add zero in front to have appropriate P-Card NO.'))
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].upper()
        if 'permanent_add' in vals and vals['permanent_add']:
            vals['permanent_add'] = vals['permanent_add'].upper()
        if 'father_name' in vals and vals['father_name']:
            vals['father_name'] = vals['father_name'].strip()
            vals['father_name'] = vals['father_name'].upper()
        if 'doj' in vals and vals['doj']:
            vals['doj'] = datetime.strptime(vals['doj'],'%Y-%m-%d')
            earn_date = vals['doj'] + timedelta(days=240)
            earn_date = earn_date.strftime("%Y-%m-%d")
            vals['earn_date'] = earn_date
        if 'paycode' in vals and vals['paycode']:
            code_len = len(vals['paycode'])
            if code_len and code_len  > 8:
                 raise osv.except_osv(_('Warning!'),_('Paycode number is greater than eight digit !!!!'))
#                 vals['paycode'] = '0000000' + vals['paycode']
#             elif code_len and code_len == 2:
#                 vals['paycode'] = '000000' + vals['paycode']
#             elif code_len and code_len == 3:
#                 vals['paycode'] = '00000' + vals['paycode']
#             elif code_len and code_len == 4:
#                 vals['paycode'] = '0000' + vals['paycode']
#             elif code_len and code_len == 5:
#                 vals['paycode'] = '000' + vals['paycode']
#             elif code_len and code_len == 6:
#                 vals['paycode'] = '00' + vals['paycode']
#             elif code_len and code_len == 7:
#                 vals['paycode'] = '0' + vals['paycode']

        if 'current_salary' in vals and vals['current_salary'] and 'other_salary' in vals and vals['other_salary']:
            vals['joining_salary'] = vals['current_salary'] + vals['other_salary']
            vals['total_salary'] = vals['current_salary'] + vals['other_salary']

#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical']:
#            vals['joining_salary'] = vals['current_salary'] + vals['hra'] + vals['conveyance'] + vals['medical']
#            vals['total_salary'] = vals['current_salary'] + vals['hra'] + vals['conveyance'] + vals['medical']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance'] and 'special_allowance' in vals and vals['special_allowance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['hra'] + vals['conveyance'] + vals['special_allowance']
#            vals['total_salary'] = vals['current_salary'] + vals['hra'] + vals['conveyance'] + vals['special_allowance']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra']  and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['hra'] + vals['medical'] + vals['special_allowance']
#            vals['total_salary'] = vals['current_salary'] + vals['hra'] + vals['medical'] + vals['special_allowance']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['conveyance'] + vals['medical'] + vals['special_allowance']
#            vals['total_salary'] = vals['current_salary'] + vals['conveyance'] + vals['medical'] + vals['special_allowance']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['hra'] + vals['conveyance']
#            vals['total_salary'] = vals['current_salary'] + vals['hra'] + vals['conveyance']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'medical' in vals and vals['medical']:
#            vals['joining_salary'] = vals['current_salary'] + vals['hra'] + vals['medical']
#            vals['total_salary'] = vals['current_salary'] + vals['hra'] + vals['medical']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'special_allowance' in vals and vals['special_allowance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['hra'] + vals['special_allowance']
#            vals['total_salary'] = vals['current_salary'] + vals['hra'] + vals['special_allowance']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['medical'] + vals['special_allowance']
#            vals['total_salary'] = vals['current_salary'] + vals['medical'] + vals['special_allowance']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'conveyance' in vals and vals['conveyance'] and 'special_allowance' in vals and vals['special_allowance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['conveyance'] + vals['special_allowance']
#            vals['total_salary'] = vals['current_salary'] + vals['conveyance'] + vals['special_allowance']
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical']:
#            vals['joining_salary'] = vals['current_salary'] + vals['conveyance'] + vals['medical']
#            vals['total_salary'] = vals['current_salary'] + vals['conveyance'] + vals['medical']
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra']:
#            vals['joining_salary'] = vals['current_salary'] + vals['hra']
#            vals['total_salary'] = vals['current_salary'] + vals['hra']
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'conveyance' in vals and vals['conveyance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['conveyance']
#            vals['total_salary'] = vals['current_salary'] + vals['conveyance']
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'medical' in vals and vals['medical']:
#            vals['joining_salary'] = vals['current_salary'] + vals['medical']
#            vals['total_salary'] = vals['current_salary'] + vals['medical']
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'special_allowance' in vals and vals['special_allowance']:
#            vals['joining_salary'] = vals['current_salary'] + vals['special_allowance']
#            vals['total_salary'] = vals['current_salary'] + vals['special_allowance']
            
        elif 'current_salary' in vals and vals['current_salary']:
            vals['joining_salary'] = vals['current_salary']
            vals['total_salary'] = vals['current_salary']
                
        if 'company_id' in vals and vals['company_id'] and 'department_id' in vals and vals['department_id'] and 'job_id' in vals and vals['job_id']:
            vals.update({'state':'Done'})

        res = super(hr_employee,self).create(cr, uid, vals, context)
        return res
    
    
    def write(self, cr, uid, ids, vals, context=None):
        emp_browse=self.browse(cr,uid,ids[0])
        act_obj = self.pool.get('hr.active.history')
        hr_tick_obj=self.pool.get('hr.tick.history')
        old_paycode = new_paycode = 0
        old_job = new_job = 0
        salary = 0
        str1="^-?[a-z0-9A-Z0-9]+([a-z0-9-])+$"
        if 'sinid' in vals and vals['sinid']:
            vals['sinid'] = vals['sinid'].strip()
            vals['sinid'] = vals['sinid'].replace(' ','')
            if re.match(str1,vals['sinid']) == None:
                raise osv.except_osv(_('Warning!'),_('Only alphanumeric and - sign is allowed in permanent card number.'))
            if len(vals['sinid'].split('-')) > 2:
                raise osv.except_osv(_('Warning!'),_('Only single - sign is allowed in permanent card number.'))
            vals['sinid'] = vals['sinid'].upper()
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].upper()
            
        if 'doj' in vals and vals['doj']:
            this = self.browse(cr, uid, ids)
            if this.history_earn_ids or this.earn_leave == 30:
                raise osv.except_osv(_('Contact to Admin!'),_('DOJ for this Employee can not be Changed due to Earn Leave History or 30 Earned Leaves due...!!'))
            vals['doj'] = datetime.strptime(vals['doj'],'%Y-%m-%d')
            earn_date = vals['doj'] + timedelta(days=240)
            earn_date = earn_date.strftime("%Y-%m-%d")
            vals['earn_date'] = earn_date
            
        if 'father_name' in vals and vals['father_name']:
            vals['father_name'] = vals['father_name'].strip()
            vals['father_name'] = vals['father_name'].upper()
        if 'paycode' in vals and vals['paycode']:
            code_len = len(vals['paycode'])
            if code_len and code_len > 8:
                  raise osv.except_osv(_('Warning!'),_('Paycode number is greater than eight digit !!!!'))
#                 vals['paycode'] = '0000000' + vals['paycode']
#             elif code_len and code_len == 2:
#                 vals['paycode'] = '000000' + vals['paycode']
#             elif code_len and code_len == 3:
#                 vals['paycode'] = '00000' + vals['paycode']
#             elif code_len and code_len == 4:
#                 vals['paycode'] = '0000' + vals['paycode']
#             elif code_len and code_len == 5:
#                 vals['paycode'] = '000' + vals['paycode']
#             elif code_len and code_len == 6:
#                 vals['paycode'] = '00' + vals['paycode']
#             elif code_len and code_len == 7:
#                 vals['paycode'] = '0' + vals['paycode']
        if 'active' in vals:
            if vals['active']:
                act_obj.create(cr, uid, {'name':'Active','date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'previous_id':'X','current_id':'X','previous_designtation':'X','current_designation':'X','previous_dept':'X','current_dept':'X'})
                vals.update({'epf_end_date':False}) 
            else:
                act_obj.create(cr, uid, {'name':'In Active','date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'previous_id':'X','current_id':'X','previous_designtation':'X','current_designation':'X','previous_dept':'X','current_dept':'X'})
        if 'type' in vals and vals['type']:
            act_obj.create(cr, uid, {'name':vals['type'],'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'previous_id':'X','current_id':'X','previous_designtation':'X','current_designation':'X','previous_dept':'X','current_dept':'X'})
       
        if 'paycode' in vals and vals['paycode']:
            new_paycode = vals['paycode']
            for a in self.browse(cr, uid, ids):
                old_paycode = a.paycode
            if new_paycode and new_paycode <> old_paycode:
                b=act_obj.create(cr, uid, {'previous_id':str(old_paycode),'current_id':str(new_paycode),'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'previous_designtation':'X','current_designation':'X','name':'X','previous_dept':'X','current_dept':'X'})
        if 'department_id' in vals and vals['department_id']:
            new_dept=vals['department_id']
            this = self.browse(cr,uid,ids)
            old_dept=this[0].department_id.name
            cr.execute("select name from  hr_department where id = '"+str(new_dept)+"' ")
            dept_temp=cr.fetchall()
            if new_dept and new_dept <> old_dept:
                act_obj.create(cr, uid, {'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'previous_id':'X','current_id':'X','name':'X','previous_dept':old_dept,'current_dept':dept_temp[0][0],'previous_designtation':'X','current_designation':'X'})  
        if 'job_id' in vals and vals['job_id']:
            this = self.browse(cr,uid,ids)
            old_job = this[0].job_id.name
            new_job = vals['job_id']
            cr.execute("select name from  hr_job where id = '"+str(new_job)+"' ")
            temp=cr.fetchall()
            if new_job and new_job <> old_job:
                b=act_obj.create(cr, uid, {'previous_designtation':old_job,'current_designation':temp[0][0],'date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'previous_id':'X','current_id':'X','name':'X','previous_dept':'X','current_dept':'X'})  
        
        if 'ot_tick' in vals:
            if vals['ot_tick']:
                hr_tick_obj.create(cr, uid, {'ot_tick_rec':'TICK','create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'epf_tick_rec':'X','esi_tick_rec':'X'})
            else:
                hr_tick_obj.create(cr, uid, {'ot_tick_rec':'UN TICK','create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'epf_tick_rec':'X','esi_tick_rec':'X'})
        
        if 'epf_tick' in vals:
            if vals['epf_tick']:
                hr_tick_obj.create(cr, uid, {'ot_tick_rec':'X','create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'epf_tick_rec':'TICK','esi_tick_rec':'X'})
            else:
                hr_tick_obj.create(cr, uid, {'ot_tick_rec':'X','create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'epf_tick_rec':'UNTICK','esi_tick_rec':'X'})        

        if 'esi_tick' in vals:
            if vals['esi_tick']:
                hr_tick_obj.create(cr, uid, {'ot_tick_rec':'X','create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'epf_tick_rec':'X','esi_tick_rec':'TICK'})
            else:
                hr_tick_obj.create(cr, uid, {'ot_tick_rec':'X','create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),'user_id':uid,'employee_id':ids[0],'epf_tick_rec':'X','esi_tick_rec':'UNTICK'})        

#        if 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['current_salary'] + vals['hra'] + vals['conveyance'] + vals['medical'] + vals['special_allowance']
#            vals.update({'total_salary':salary})
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical']:
#            salary = vals['current_salary'] + vals['hra'] + vals['conveyance'] + vals['medical']
#            vals.update({'total_salary':salary})
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['current_salary'] + vals['hra'] + vals['conveyance'] + vals['special_allowance']
#            vals.update({'total_salary':salary})
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra']  and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['current_salary'] + vals['hra'] + vals['medical'] + vals['special_allowance']
#            vals.update({'total_salary':salary})
#
#        elif 'current_salary' in vals and vals['current_salary'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['current_salary'] + vals['conveyance'] + vals['medical'] + vals['special_allowance']
#            vals.update({'total_salary':salary})
#            
#        elif 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['hra'] + vals['conveyance'] + vals['medical'] + vals['special_allowance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance']:
#            salary = vals['current_salary'] + vals['hra'] + vals['conveyance']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'medical' in vals and vals['medical']:
#            salary = vals['current_salary'] + vals['hra'] + vals['medical']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['current_salary'] + vals['hra'] + vals['special_allowance']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical']:
#            salary = vals['current_salary'] + vals['conveyance'] + vals['medical']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'conveyance' in vals and vals['conveyance'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['current_salary'] + vals['conveyance'] + vals['special_allowance']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['current_salary'] + vals['medical'] + vals['special_allowance']
#            vals.update({'total_salary':salary})
#
#        elif 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical']:
#            salary = vals['hra'] + vals['conveyance'] + vals['medical'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#
#        elif 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['hra'] + vals['conveyance'] + vals['special_allowance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#
#        elif 'hra' in vals and vals['hra'] and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['hra'] + vals['medical'] + vals['special_allowance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#
#        elif 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['conveyance'] + vals['medical'] + vals['special_allowance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#
#        elif 'hra' in vals and vals['hra'] and 'conveyance' in vals and vals['conveyance']:
#            salary = vals['hra'] + vals['conveyance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#            
#        elif 'hra' in vals and vals['hra'] and 'medical' in vals and vals['medical']:
#            salary = vals['hra'] + vals['medical'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#
#        elif 'hra' in vals and vals['hra'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['hra'] + vals['special_allowance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#
#        elif 'conveyance' in vals and vals['conveyance'] and 'medical' in vals and vals['medical']:
#            salary = vals['conveyance'] + vals['medical'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#
#        elif 'conveyance' in vals and vals['conveyance'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['conveyance'] + vals['special_allowance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#
#        elif 'medical' in vals and vals['medical'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['medical'] + vals['special_allowance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'hra' in vals and vals['hra']:
#            salary = vals['current_salary'] + vals['hra']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'conveyance' in vals and vals['conveyance']:
#            salary = vals['current_salary'] + vals['conveyance']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'medical' in vals and vals['medical']:
#            salary = vals['current_salary'] + vals['medical']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary'] and 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['current_salary'] + vals['special_allowance']
#            vals.update({'total_salary':salary})
#            
#        elif 'current_salary' in vals and vals['current_salary']:
#            salary = vals['current_salary']
#            vals.update({'total_salary':salary})
#            
#        elif 'hra' in vals and vals['hra']:
#            salary = vals['hra'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#            
#        elif 'conveyance' in vals and vals['conveyance']:
#            salary = vals['conveyance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#            
#        elif  'medical' in vals and vals['medical']:
#            salary = vals['medical'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
#            
#        elif 'special_allowance' in vals and vals['special_allowance']:
#            salary = vals['special_allowance'] + emp_browse.current_salary
#            vals.update({'total_salary':salary})
            
        res = super(hr_employee, self).write(cr, uid, ids, vals, context)
        
        emp_browse = self.browse(cr, uid, ids[0])
        if emp_browse.company_id and emp_browse.department_id and emp_browse.job_id :
            cr.execute("update hr_employee set state='Done' where id='"+str(ids[0])+"'  ")        
        return res
        
    def update_category(self,cr,uid,ids,context=None):
        count = 0
        for val in self.search(cr,uid,[]):
            self.write(cr,uid,[val],{'category_ids':[(6,0,[16])]})
            count = count+1
        return True
    
    def update_ssnid(self,cr,uid,ids,context=None):
        for val in self.search(cr,uid,[('active','=',True)]):
            pay = self.browse(cr, uid, val).paycode
            if len(pay) == 8:
                continue
            elif len(pay) == 7:
                roger = '0' + str(pay)
            elif len(pay) == 6:
                roger = '00' + str(pay)
            elif len(pay) == 5:
                roger = '000' + str(pay)
            elif len(pay) == 4:
                roger = '0000' + str(pay)
            elif len(pay) == 3:
                roger = '00000' + str(pay)
            elif len(pay) == 2:
                roger = '000000' + str(pay)
            elif len(pay) == 1:
                roger = '0000000' + str(pay)
            print "roger",roger,
            self.write(cr, uid, [val],{'paycode':roger})
        return True
            
    def onchange_job_id(self,cr,uid,ids,job_id,context=None):
        res = {}
        if job_id:
            job = self.pool.get('hr.job').browse(cr, uid,job_id,context=context)
            sal_categ = self.pool.get('employee.salary.category').search(cr, uid, [('category','=',job.category)])
            if sal_categ:
                sal_category =  self.pool.get('employee.salary.category').browse(cr, uid,sal_categ)
                res['value'] =  {'category':job.category,'current_salary':sal_category.salary,'employee_type':job.employee_type}
        return res
            

class res_company(osv.osv):
    _inherit = "res.company"
    _columns={
              'regional_code' : fields.char("PF Regional Code"),
              'office_code' : fields.char("PF Office Code"),
              'estab_id' : fields.char("PF Establishment ID"),
              'extension_id' : fields.char("Extension ID."),
              'iec':fields.char('IEC',size=20),
              'tin_no':fields.char('TIN NO',SIZE=40)
              }

class employee_nominee(osv.osv):
    _name = "employee.nominee"
    
    _columns = {
                'name':fields.char("Nominee's Name"),
                'nominee_father':fields.char("Nominee's Father/Husband Name"),
                'relation':fields.char("Relation",required=True),
                'age':fields.integer("Age"),
                'share':fields.float("Share",required=True),
                'employee_id':fields.many2one('hr.employee',"Employee Name"),
                }

class qualification(osv.osv):
    _name="qualification"
    _columns = {
                'name':fields.many2one('qualification.list','Qualification',required=True,select=True),
                'college' :fields.char('College Name',required=True,select=True),
                'employee_id':fields.many2one('hr.employee','Qualification',select=True),
                'year11':fields.many2one('emp.year','Year',required=True),
                'grade':fields.char('Grade'),
                'user_id':fields.many2one('res.users','User',readonly=True),
                }
    _defaults = {
                'user_id': lambda obj, cr, uid, context: uid,
                 }
    
class experience(osv.osv):
    _name="experience"
    
    def _calculate_noy(self, cr, uid, ids, fieldsname, args, context=None):            
        res = {}
        for each in self.browse(cr, uid, ids):
# #             year1 = int(each.year11.name)
# #             year2 = int(each.year12.name)
# #             if year1 and year2:
                noy = 0
                res[each.id] =  noy
        return res
    
    _columns = {
                'name' :fields.char('Company Name',required=True,),
                'address' :fields.char('Company Address',required=True,select=True),
                'employee_id':fields.many2one('hr.employee','Experience',select=True),
                'year11':fields.many2one('emp.year','From Year',required=True),
                'year12':fields.many2one('emp.year','To Year',required=True),
                'desg':fields.char('Designation'),
                'leaving_salary':fields.float("Leaving Salary"),
                'noy':fields.function(_calculate_noy,'No.of Years',invisible=True),
                'user_id':fields.many2one('res.users','User',readonly=True),
                'reporting_officer':fields.many2one('hr.employee','Reporting Officer',select=True),
                'reporting_employee':fields.char('Reporting Officer',size=1024),
                'contact_no':fields.char('Contact No.',size=64),
                }
    _defaults = {
                'user_id': lambda obj, cr, uid, context: uid,
                 }
    
class family(osv.osv):
    _name="family"
    _columns = {
                'name' :fields.char('Name',),
                'age' :fields.integer('Age',),
                'relation':fields.selection([('Father','Father'),('Mother','Mother'),('Wife','Wife'),('Husband','Husband'),('Son','Son'),('Daughter','Daughter'),('Other','Other'),('Brother','Brother'),('Sister','Sister')],"Relation",required=True),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'reside':fields.boolean('Residing'),
                "nom_tick":fields.boolean('Nominee Tick'),
                'nominee_father':fields.char("Nominee's Father/Husband Name"),
                'address':fields.char("Nominee's Address"),
                'share':fields.float("Share"),
                'user_id': fields.many2one('res.users', 'Responsible',readonly=True),
                }
    
    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               } 

class reference(osv.osv):
    _name = "reference"
    _columns = {
                'name' :fields.char('Name'),
                'occupation' :fields.char('Occupation'),
                'address' :fields.char('Address'),
                'contact':fields.char('Contact No.'),
                'ref_date':fields.date('Date'),
                'employee_id':fields.many2one('hr.employee',"Employee"),
                'user_id':fields.many2one('res.users','User',readonly=True),
                }
    _defaults = {
                'user_id': lambda obj, cr, uid, context: uid,
                 }

class increment(osv.osv):
    _name = "increment"

    def _calculate_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.inc_date,'%Y-%m-%d').timetuple()
            month = tm_tuple.tm_mon
            res[each.id] = month     
        return res
    
    def _calculate_year(self, cr, uid, ids, name, args, context=None):
        res = {}
        for each in self.browse(cr, uid, ids):
            tm_tuple = datetime.strptime(each.inc_date,'%Y-%m-%d').timetuple()
            year = tm_tuple.tm_year
            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
            if year_id:
                res[each.id] = year_id[0]  
            else:
                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
        return res

    
    _columns = {
                'increment_id':fields.many2one('annual.salary.increment','Increment'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'inc_date':fields.date('Increment Date',required=True),
                'amount' :fields.float('Amount',required=True),
                'old_salary':fields.float('Old Salary',digits=(16,2)),
                'month':fields.function(_calculate_month,method=True,type='integer',string='Month',store=True),
                'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
                'user_id': fields.many2one('res.users', 'Responsible',readonly=True),
                'create_date':fields.datetime('Create Date',readonly=True),
                'salary_category':fields.selection([('Basic+DA','Basic+DA'),('Other','Other'),('HRA','HRA'),('Conveyance','Conveyance'),('Medical','Medical'),('Special Allowance','Special Allowance')],"Category"),
                }
    
    _defaults={
               'create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
               'user_id': lambda obj, cr, uid, context: uid,
               'inc_date':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
               } 

    _sql_constraints = [('unique_employee_month_year','unique(employee_id,inc_date)','Employee salary line for this date is already exist.')]

    def create(self, cr, uid, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
#        old = new = curr = hra = conveyance = medical = allowance = total_salary = new1 =  0.0
        old = new = curr = total_salary = new1 =  other = 0.0
        if 'amount' in vals and vals['amount'] and 'employee_id' in vals and vals['employee_id']:
            emp_obj = hr_obj.browse(cr, uid, hr_obj.search(cr, uid, [('id','=',vals['employee_id'])]))
            if not emp_obj[0].current_salary:
                raise osv.except_osv(('Warning'),("Current salary is zero, waiting for updation."))
            else:
                curr = emp_obj[0].joining_salary
                total_salary = emp_obj[0].total_salary
                
            if emp_obj[0].current_salary > 0.0:
                old = emp_obj[0].current_salary
            else:
                old = 0.0

            if emp_obj[0].other_salary > 0.0:
                other = emp_obj[0].other_salary
            else:
                other = 0.0
                
#            if emp_obj[0].hra > 0.0:
#                hra = emp_obj[0].hra
#            else:
#                hra = 0.0
                
#            if emp_obj[0].conveyance > 0.0:        
#                conveyance = emp_obj[0].conveyance
#            else:
#                conveyance = 0.0
                
#            if emp_obj[0].medical > 0.0:        
#                medical = emp_obj[0].medical
#            else:
#                medical = 0.0
                
#            if emp_obj[0].special_allowance > 0.0:        
#                allowance = emp_obj[0].special_allowance
#            else:
#                allowance = 0.0
                    
            if 'salary_category' in vals and vals['salary_category'] == 'Basic+DA':
                new = old + vals['amount']
                new1 = total_salary + vals['amount']
                hr_obj.write(cr, uid, [vals['employee_id']], {'current_salary':new,'total_salary':new1})

            elif 'salary_category' in vals and vals['salary_category'] == 'Other':
                new = other + vals['amount']
                new1 = total_salary + vals['amount']
                hr_obj.write(cr, uid, [vals['employee_id']], {'other_salary':new,'total_salary':new1})
                
#            elif 'salary_category' in vals and vals['salary_category'] == 'HRA':
#                new = hra + vals['amount']
#                new1 = total_salary + vals['amount']
#                hr_obj.write(cr, uid, [vals['employee_id']], {'hra':new,'total_salary':new1})
                
#            elif 'salary_category' in vals and vals['salary_category'] == 'Conveyance':
#                new = conveyance + vals['amount']
#                new1 = total_salary + vals['amount']
#                hr_obj.write(cr, uid, [vals['employee_id']], {'conveyance':new,'total_salary':new1})
                
#            elif 'salary_category' in vals and vals['salary_category'] == 'Medical':
#                new = medical + vals['amount']
#                new1 = total_salary + vals['amount']
#                hr_obj.write(cr, uid, [vals['employee_id']], {'medical':new,'total_salary':new1})
                
#            elif 'salary_category' in vals and vals['salary_category'] == 'Special Allowance':
#                new = allowance + vals['amount']
#                new1 = total_salary + vals['amount']
#                hr_obj.write(cr, uid, [vals['employee_id']], {'special_allowance':new,'total_salary':new1})
            else:
                new = old + vals['amount']
                new1 = total_salary + vals['amount']    
                hr_obj.write(cr, uid, [vals['employee_id']], {'current_salary':new,'total_salary':new1})
#            if new <> 0.0 and curr > 0.0:
#                hr_obj.write(cr, uid, [vals['employee_id']], {'current_salary':new})
#            elif new <> 0.0 and curr == 0.0:
#                hr_obj.write(cr, uid, [vals['employee_id']], {'current_salary':new})
        res = super(increment, self).create(cr, uid, vals)
        return res



    def write(self, cr, uid, ids, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        old = new = 0.0
        for each in self.browse(cr, uid, ids):
            emp_id = each.employee_id and each.employee_id.id or False
            old = each.employee_id and each.employee_id.current_salary or 0.0
        
        if 'amount' in vals and vals['amount'] and 'employee_id' in vals and vals['employee_id']:
            old = hr_obj.browse(cr, uid, hr_obj.search(cr, uid, [('id','=',vals['employee_id'])]))
            if not old[0].current_salary:
                raise osv.except_osv(('Warning'),("Current salary is zero, waiting for updation."))
            else:
                old = old[0].current_salary
            new = old + vals['amount']
            if new <> 0.0:
                hr_obj.write(cr, uid, [vals['employee_id']], {'current_salary':new})
        
        if 'amount' in vals and vals['amount']:
            new = old + vals['amount']
            if new <> 0.0:
                hr_obj.write(cr, uid, [emp_id], {'current_salary':new})
        
        res = super(increment, self).write(cr, uid, ids, vals)
        return res
       
class promotion(osv.osv):
    _name = "promotion"
    _columns = {
                'pro_date':fields.date('Promotion Date',required=True),
                'desgn_id' :fields.many2one('hr.job','Designation',required=True),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'user_id': fields.many2one('res.users', 'Responsible',readonly=True),
                 'create_date':fields.datetime('Create Date',readonly=True),
                }
    _defaults={
               'create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
               'user_id': lambda obj, cr, uid, context: uid,
               } 
    
    def create(self, cr, uid,vals,context=None):
        res={}
        hr_obj = self.pool.get('hr.employee')
        job_id = self.pool.get('hr.job')
        job = job_id.browse(cr,uid,vals['desgn_id'])
        if 'desgn_id' in vals and vals['desgn_id'] and 'employee_id' in vals and vals['employee_id']:
            emp_browse = hr_obj.browse(cr, uid, hr_obj.search(cr, uid, [('id','=',vals['employee_id'])]))
            promote_desig=vals['desgn_id']
            if  promote_desig :
                if not emp_browse[0].job_id.id:
                    raise osv.except_osv(('Warning'),("Current Job title  is not define for Employee.Please enter Job title first"))
                else:
                    wr_obj= hr_obj.write(cr, uid, [vals['employee_id']], {'job_id':promote_desig,'category':job.category})
            else:
                 raise osv.except_osv(('Warning'),("Please Select the  Designation !!! "))
        res = super(promotion,self).create(cr, uid, vals)     
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        promote_browse=self.browse(cr,uid,ids)
        hr_obj = self.pool.get('hr.employee')
        if vals:
            if 'desgn_id' in vals and vals['desgn_id'] :
                emp_id=promote_browse.employee_id.id
                desig_update=vals['desgn_id']
                hr_obj.write(cr, uid, [emp_id], {'job_id':desig_update})
            res = super(promotion, self).write(cr, uid, ids, vals, context)
        return res   
    
    
    
    
    
    

class emp_year(osv.osv):
    _name="emp.year"
    _columns = {
                'name':fields.char("Year"),
                }
    
class hr_department(osv.osv):
    _inherit = "hr.department"
    _defaults = {
        'company_id': False
    }
    
class hr_job (osv.osv):
    _inherit = "hr.job"
    _columns={
              'category':fields.selection([('Skilled','Skilled'),('UnSkilled','UnSkilled'),('Semi_Skilled','Semi_Skilled')],"Category"),
              'employee_type':fields.selection([('Staff','Staff'),('Worker','Worker')],'Employee Type'),
              }
    _defaults = {
        'company_id': False
    }
    
class employee_leave_allocation(osv.osv):  
    _name="employee.leave.allocation" 
    _columns={
              'leave_days':fields.integer('Leave Days',required=True),
              'employee_id':fields.many2one('hr.employee','Employee'),
              'holiday_status_id':fields.many2one("hr.holidays.status", "Leave Type", required=True),
              'user_id': fields.many2one('res.users', 'Responsible',readonly=True),
               'create_date':fields.datetime('Create Date',readonly=True),
              }
    _defaults={
               'create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
               'user_id': lambda obj, cr, uid, context: uid,
               } 
    
    def create(self, cr, uid, vals, context=None):
        print "in create===================",vals   
        hol_obj = self.pool.get('hr.holidays')
        res={}
        employee_id=vals['employee_id']    

        hr_obj = self.pool.get('hr.employee').browse(cr,uid,employee_id)
        leave_obj = self.pool.get('hr.holidays.status')
        status_id=vals['holiday_status_id']
        leave_desc = leave_obj.browse(cr,uid,status_id)
        leave_desc_name=leave_desc.name                         
        leave_days=vals['leave_days']
        dept_id=hr_obj.department_id.id
        print "values record========================",hr_obj,leave_obj,status_id,leave_desc,leave_desc_name,dept_id,leave_days 
        res = super(employee_leave_allocation,self).create(cr, uid, vals)
        print "res=============",res  
        if res:
               create_id=self.pool.get('hr.holidays').create(cr, uid,{'holiday_status_id':status_id,'employee_id':employee_id,'user_id':uid,'number_of_days_temp':leave_days,'type':'add','holiday_type':'employee','state':'validate','department_id':dept_id,'name':leave_desc_name})  
               print "create_id==================",create_id   
               button=hol_obj.holidays_validate(cr, uid, create_id, context=None)
               print "button==============",button
        return res

    def write(self, cr, uid, ids, vals, context=None):
        leve_browse= self.browse(cr,uid,ids)
        emp_id=leve_browse.employee_id.id
        hol_id=leve_browse.holiday_status_id.id
        res={}
        leave_obj = self.pool.get('hr.holidays')
        wr_id=leave_obj.browse(cr, uid, leave_obj.search(cr, uid, [('employee_id','=',emp_id),('holiday_status_id','=',hol_id)]))
        res = super(employee_leave_allocation, self).write(cr, uid, ids, vals, context)
        if 'leave_days' in vals:
            if vals['leave_days']:
                wr_obj=leave_obj.write(cr, uid,wr_id.id,{'number_of_days_temp':vals['leave_days']})
        return res 
    
    
class company_transfer_history(osv.osv): 
    _name="company.transfer.history"
    
    def _get_company_id(self,cr,uid,context):
        if context == {}:
            return {}
        if  'params' in context:
            emp_id=0
        if 'employee_id' in context :
            emp_id=context['employee_id']
        if emp_id > 0 :
            emp_browse=self.pool.get('hr.employee').browse(cr,uid,emp_id).resource_id.id
            if  emp_browse :
                resource_browse=self.pool.get('resource.resource').browse(cr,uid,emp_browse).company_id.id
                if resource_browse:
                    comp_browse=self.pool.get('res.company').browse(cr,uid,resource_browse).id
                    return resource_browse
                return True
            
        
    def _get_department_id(self,cr,uid,context):
        if context == {} :
            return {}
        if  'params' in context:
            emp_id=0
        if 'employee_id' in context :
            emp_id=context['employee_id']
        if  emp_id > 0 :
            emp_browse=self.pool.get('hr.employee').browse(cr,uid,emp_id).department_id.id
            if  emp_browse :
                return emp_browse
            return True

    _columns={
              'create_date':fields.datetime('Create Date',readonly=True),
               'employee_id':fields.many2one('hr.employee','Employee',invisible=True),
               'transfer_date':fields.date('Transfer Date',required=True),
               'old_company_id':fields.many2one('res.company','Old Company',readonly=True),
               'new_company_id':fields.many2one('res.company','New Company',required=True),
               'user_id': fields.many2one('res.users', 'Responsible',readonly=True),
               'new_department_id': fields.many2one('hr.department', 'New Department',required=True),
               'old_department_id':fields.many2one('hr.department', ' Old Department',readonly=True),
               }
    _defaults={
               'old_company_id' : _get_company_id,
                'old_department_id':_get_department_id,
               'create_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
               'user_id': lambda obj, cr, uid, context: uid,
               }
    
    def create(self, cr, uid, vals, context):
        if 'employee_id' in vals and vals['employee_id'] :
             employee_id=vals['employee_id']
             dept_browse=self.pool.get('hr.employee').browse(cr,uid,employee_id).department_id.id
             comp_browse=self.pool.get('hr.employee').browse(cr,uid,employee_id).company_id.id
             old_comp_name=self.pool.get('hr.employee').browse(cr,uid,employee_id).company_id.name
             old_comp_name_first=old_comp_name[0]
             vals.update({'old_company_id':comp_browse})
             vals.update({'old_department_id':dept_browse})
        hr_obj = self.pool.get('hr.employee')
        if 'new_company_id'   in vals and 'new_department_id'   in vals:
            company_update=vals['new_company_id']
            dept_update=vals['new_department_id']
            new_comp_name = self.pool.get('res.company').browse(cr, uid, company_update, context=context).name
            new_comp_name_first=new_comp_name[0]
            if old_comp_name_first==new_comp_name_first :
                if  str(old_comp_name_first)=='L' and str(new_comp_name) =='Lohia Developer India Pvt Ltd' :
                     raise osv.except_osv(('Warning'),("You Can not Transfer Lohia Unit  to Lohia Developer Unit"))
                elif str(old_comp_name)=='Lohia Developer India Pvt Ltd' and str(new_comp_name_first) =='L' :
                    raise osv.except_osv(('Warning'),("You Can not Transfer Lohia Developer Unit  to Lohia Unit"))
                else:
                    rec_id = self.pool.get('res.users').search(cr, uid,[('company_id','=',company_update),('id','!=',1)])
                    rec_hr_id = self.pool.get('res.users').search(cr, uid,[('company_id','=',company_update),('login','like','hr-')])
                    for val in rec_id : 
                        if val ==  rec_hr_id[0] : 
                           comp_user_id = val
                           user_id = rec_id[1]
                           break
                        else : 
                           comp_user_id = rec_id[1]
                           user_id = rec_id[0]
                           break
                    wr_obj= hr_obj.write(cr, uid, [employee_id], {'old_department_id':dept_browse,'old_company_id':comp_browse,'company_id':company_update,'department_id':dept_update,'user_id':user_id,'comp_user_id':comp_user_id})
                    res = super(company_transfer_history,self).create(cr, uid, vals,context)
                    if res :
                         return res
            else:
                 raise osv.except_osv(('Warning'),("You Can not Transfer Designco to Lohia Unit or Lohia to Designco Unit")) 
    
    def write(self, cr, uid, ids, vals, context):
        res={}
        comp_hist_browse=self.browse(cr,uid,ids)
        hr_obj = self.pool.get('hr.employee')
        emp_id=comp_hist_browse.employee_id.id
        if 'new_company_id' in vals  and  'new_department_id'   in vals :
            new_comp_id=vals['new_company_id']
            new_dept_id=vals['new_department_id']
            company_id = self.pool.get('res.company').browse(cr, uid, new_comp_id, context=context)
            rec_id = self.pool.get('res.users').search(cr, uid,[('company_id','=',new_comp_id),('id','!=',1)])
            rec_hr_id = self.pool.get('res.users').search(cr, uid,[('company_id','=',new_comp_id),('login','like','hr-')])
            for val in rec_id : 
                if val ==  rec_hr_id[0] : 
                   comp_user_id = val
                   user_id = rec_id[1]
                   break
                else :
                   comp_user_id = rec_id[1]
                   user_id = rec_id[0]
                   break
            hr_obj.write(cr, uid, [emp_id], {'company_id':new_comp_id,'department_id':new_dept_id,'user_id':user_id,'comp_user_id':comp_user_id})
        if  'new_company_id'  in vals  and 'new_department_id' not in vals:
             new_comp_id=vals['new_company_id']
             company_id = self.pool.get('res.company').browse(cr, uid, new_comp_id, context=context)
             rec_id = self.pool.get('res.users').search(cr, uid,[('company_id','=',new_comp_id),('id','!=',1)])
             rec_hr_id = self.pool.get('res.users').search(cr, uid,[('company_id','=',new_comp_id),('login','like','hr-')])
             for val in rec_id : 
                if val ==  rec_hr_id[0] : 
                   comp_user_id = val
                   user_id = rec_id[1]
                   break
                else : 
                   comp_user_id = rec_id[1]
                   user_id = rec_id[0]
                   break
             hr_obj.write(cr, uid, [emp_id], {'company_id':new_comp_id,'user_id':user_id,'comp_user_id':comp_user_id})
        if  'new_department_id' in  vals and 'new_company_id' not   in vals :
            new_dept_id=vals['new_department_id']
            hr_obj.write(cr, uid, [emp_id], {'department_id':new_dept_id})
        res = super(company_transfer_history, self).write(cr, uid, ids, vals, context)        
        return res            
            
            
            
class hr_tick_history(osv.osv): 
    _name="hr.tick.history" 
    
    _columns={
               'create_date':fields.datetime('Create Date',readonly=True),
               'employee_id':fields.many2one('hr.employee','Employee',invisible=True),
               'ot_tick_rec':fields.char('OT TICK',size=64,readonly=True),
               'epf_tick_rec':fields.char('EPF TICK',size=64,readonly=True),
               'esi_tick_rec':fields.char('ESI TICK',size=64,readonly=True),
               'user_id': fields.many2one('res.users', 'Responsible',readonly=True),
               }  
    
    _defaults={
               'user_id': lambda obj, cr, uid, context: uid,
               }     
    

class res_bank(osv.osv): 
    _inherit = 'res.bank'  
    
    def name_get(self, cr, uid, ids, context=None):
           result = []
           for bank in self.browse(cr, uid, ids, context):
               result.append((bank.id, (bank.bic and (bank.bic) or '')))
           return result 
       
    def name_search(self, cr, user, name, args=None, operator='ilike',
                    context=None, limit=80):
        """Search by bank code in addition to the standard search"""
        # Get the standard results
        results = super(res_bank, self).name_search(cr, user,
             name, args=args ,operator=operator, context=context, limit=limit)
        # Get additional results using the RIB code
        ids = self.search(cr, user, [('bic', operator, name)],
                              limit=limit, context=context)
        
        # Merge the results
        results = list(set(results + self.name_get(cr, user, ids, context)))
        return results       

class annual_salary_increment(osv.osv):
    _name="annual.salary.increment"

    _columns = {
                'name':fields.date('Date'),
                'category':fields.selection([('Skilled','Skilled'),('UnSkilled','UnSkilled'),('Semi_Skilled','Semi_Skilled')],"Category"),
                'company_id':fields.many2one('res.company','Company'),
                'employee_id':fields.many2one('hr.employee','Employee'),
                'state':fields.selection([('draft','Draft'),('done','Done')],'State',readonly=True),
                'monthly_amount':fields.float('Monthly Minimum Amount'),
                'monthly_amount_limit':fields.float('Monthly  Limit Amount'),
                'employee_ids':fields.many2many('hr.employee','emp_increment_rel','emp_id','increment_id','Employees'),
                'increment_line':fields.one2many('increment','increment_id','Increment Line'),
                'company_ids':fields.many2many('res.company','company_increment_rel','comp_id','sal_id','Company'),
                }
    _defaults = {
                'name':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'state':'draft',
                }

    def get_employees(self, cr, uid, ids, context=None):
        emp_obj = self.pool.get('hr.employee')
        for val in self.browse(cr, uid ,ids):
            emp_ids = []
            if val.category and val.monthly_amount_limit:
                emp_ids = emp_obj.search(cr, uid, [('category','=',val.category),('current_salary','<',val.monthly_amount_limit),('active','=',True)])
            
            elif val.company_id and val.monthly_amount_limit:
                emp_ids = emp_obj.search(cr, uid, [('company_id','=',val.company_id.id),('current_salary','<',val.monthly_amount_limit),('active','=',True)])
            
            elif val.employee_id and val.monthly_amount_limit:
                emp_ids = emp_obj.search(cr, uid, [('id','=',val.employee_id.id),('current_salary','<',val.monthly_amount_limit),('active','=',True)]) 

            elif val.category :
                emp_ids = emp_obj.search(cr, uid, [('category','=',val.category),('active','=',True)])
            
            elif val.company_id:
                emp_ids = emp_obj.search(cr, uid, [('company_id','=',val.company_id.id),('active','=',True)])
            
            elif val.employee_id:
                emp_ids = emp_obj.search(cr, uid, [('id','=',val.employee_id.id),('active','=',True)]) 
                   
            wr_obj=self.write(cr, uid, ids, {'employee_ids':[(6,0,emp_ids)]})
        return True

    def create_increment(self, cr, uid, ids, context=None):
        increment_obj = self.pool.get('increment')
        for val in self.browse(cr, uid, ids):
            for line in val.employee_ids:
                if val.monthly_amount != 0.00 and not val.monthly_amount_limit :
                    increment_obj.create(cr,uid,{
                                                 'increment_id':val.id,
                                                 'employee_id':line.id,
                                                 'amount':val.monthly_amount,
                                                 'old_salary':line.current_salary,
                                                 'salary_category':'Basic+DA',
                        })
                elif val.monthly_amount != 0.00 and val.monthly_amount_limit:
                    if val.monthly_amount_limit :
                        inc_salary=val.monthly_amount - line.current_salary
                        increment_obj.create(cr,uid,{
                                                    'increment_id':val.id,
                                                    'employee_id':line.id,
                                                    'amount':inc_salary,
                                                    'old_salary':line.current_salary,
                                                    'salary_category':'Basic+DA',
                            })
                else:
                    raise osv.except_osv(('Warning'),("Please Enter Monthly Amount"))
        return True 

    def company_done(self, cr, uid, ids, context=None):
        for val in self.browse(cr, uid, ids):
            if val.company_id:
                write_obj=self.write(cr, uid,ids,{'company_ids':[(4,val.company_id.id)],'company_id':False,'monthly_amount':0.0,})
        return True


class wiz_update_employee_master(osv.TransientModel):
    _name = 'wiz.update.employee.master'
    
    
    _columns = {
                'sinid' : fields.char("Employee Code"),
                }
    
    
    def server_connect(self,ids):
        server='172.20.99.141'
        port='5432'
        user='openerp'
        password='admin'
        database='LOHIA_INDUSTRIAL_ESTATE'            
        try:
            connection = psycopg2.connect(host=server, port=port, user=user, password=password, dbname=database)
            return connection
        except:
            raise osv.except_osv(_('Warning !'),_("Unable to connect to server, please check the parameters and network connections."))   
        
        
    def update_employee_master(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users').browse(cr,uid,uid)
        hr_obj = self.pool.get('hr.employee')
        val =  self.browse(cr, uid, ids)
        conn = self.server_connect(val)
        cursor = conn.cursor()
        religion = ''
        fath_list = []
        adhar_list = []
        print "======================== [[ Connection ESTABLISH ]]  ==================="

        query = "select hr.sinid,rr.name,hr.joining_date,hr.ssnid,hr.marital,hr.gender,hr.birthday,hr.personal_mobile,hr.home_address,hr.blood_group,hr.religion,hr.approval_2,hr.fath_name,hr.adhaar,hr.account_number,hr.id from hr_employee as hr left join resource_resource as rr on hr.resource_id = rr.id  where sinid='"+str(val.sinid)+"' "   
        cursor.execute(query)
        result = cursor.fetchall()
        if result:  
            for value in result:
                if value[10] == 'hindu':
                    religion = 'Hindu'
                elif value[10] == 'muslim':
                    religion = 'Muslim'
                elif value[10] == 'sikh':
                    religion = 'Sikh'
                elif value[10] == 'isai':
                    religion = 'Isai'
                elif value[10] == 'other':
                    religion = 'Other'
                
                date1=value[6]
                date2= value[2]
                days=(datetime.strptime(date2,"%Y-%m-%d").date()-datetime.strptime(date1,"%Y-%m-%d").date()).days
                if days >= 6574:
                     dob = datetime.strptime(date1, "%Y-%m-%d")
                     doj=datetime.strptime(date2, "%Y-%m-%d")   
                     rdelta = relativedelta(doj, dob)
                     age_calc= rdelta.years 
                
                if value[13] and value[13] != None:
                    adhar_list.append([0,False,{'proof_id':'Aadhar_Card' ,'id_no':value[13],'verify':True}])
                else:
                     adhar_list.append([0,False,{'proof_id':'Aadhar_Card','id_no':''}])    

                if value[14] and value[14] != None:
                    adhar_list.append([0,False,{'proof_id':'Bank_ Account_ No' ,'id_no':value[14],'verify':True}])
                else:
                     adhar_list.append([0,False,{'proof_id':'Bank_ Account_ No','id_no':''}])    

                if value[12] and value[12] != None:
                    fath_list.append([0,False,{'name':value[12],'relation':'Father','age':'','reside':False,'nom_tick':False,'nominee_father':'','share':''}])
                else:
                     fath_list.append([0,False,{'name':'','relation':'Father','age':'','reside':False,'nom_tick':False,'nominee_father':'','share':''}])    

                query_family = "select name,relation,age,reside,nom_tick,nominee_father,share from family_information where employee_id='"+str(value[15])+"' "   
                cursor.execute(query_family)
                result_family = cursor.fetchall()
                if result_family:
                    for val in result_family:
                        fath_list.append([0,False,{'name':val[0],'relation':val[1],'age':val[2],'reside':val[3],'nom_tick':val[4],'nominee_father':val[5],'share':val[6]}])
                    
                emp_id = hr_obj.search(cr, uid, [('sinid','=',value[0]),('active','=',True)])
                if emp_id:
                    raise osv.except_osv(_('Warning !'),_("Employee Already Exists For This Card No."))
                else:    
                    create_obj=hr_obj.create(cr,uid,{'sinid':value[0],'name':value[1],'doj':value[2],'paycode':value[3],'marital':value[4],'gender':value[5],'birthday':value[6],'mobile_phone':value[7],'permanent_add':value[8],'copy_add':True,'local_add':value[8],'type':'Employee','age':age_calc,'active':True,'blood':value[9],'religion':religion,'ref_check_by':user_obj.name,'app_review_by':value[11],'family_id':fath_list,'verf_id':adhar_list})
                    print "==============================EMPLOYEE==MASTER==CREATED ============================="
        
        return True



    def update_contractor_master(self, cr, uid, ids, context=None):
        print ("------- In Update Contractor Master --------")
        user_obj = self.pool.get('res.users').browse(cr,uid,uid)
        hr_obj = self.pool.get('hr.employee')
        val =  self.browse(cr, uid, ids)
        conn = self.server_connect(val)
        cursor = conn.cursor()
        religion = ''
        fath_list = []
        adhar_list = []
        exp_list=[]
        
        print "======================== [[ Connection ESTABLISH ]]  ==================="
        
        query = "select hr.sinid,rr.name,hr.joining_date,hr.marital,hr.gender,hr.dob_date,hr.mobile,hr.street,hr.fath_name,hr.identity,hr.account_number,hr.religion,hr.blood_group,hr.id from hr_contractorp as hr left join resource_resource as rr on hr.resource_id = rr.id  where sinid='"+str(val.sinid)+"' "   
        cursor.execute(query)
        result = cursor.fetchall()
        if result:  
            for value in result:
                
                date1=value[5]
                date2= value[2]
                days=(datetime.strptime(date2,"%Y-%m-%d").date() - datetime.strptime(date1,"%Y-%m-%d").date()).days
                if days >= 6574:
                     dob = datetime.strptime(date1, "%Y-%m-%d")
                     doj=datetime.strptime(date2, "%Y-%m-%d")   
                     rdelta = relativedelta(doj, dob)
                     age_calc= rdelta.years 
                     
                if value[9] and value[9] != None:
                    adhar_list.append([0,False,{'proof_id':'Aadhar_Card' ,'id_no':value[9],'verify':True}])
                else:
                     adhar_list.append([0,False,{'proof_id':'Aadhar_Card','id_no':''}])    

                if value[10] and value[10] != None:
                    adhar_list.append([0,False,{'proof_id':'Bank_ Account_ No' ,'id_no':value[10],'verify':True}])
                else:
                     adhar_list.append([0,False,{'proof_id':'Bank_ Account_ No','id_no':''}])           
                if value[8] and value[8] != None:
                    fath_list.append([0,False,{'name':value[8],'relation':'Father','age':'','reside':False,'nom_tick':False,'nominee_father':'','share':''}])
                else:
                    fath_list.append([0,False,{'name':'','relation':'Father','age':'','reside':False,'nom_tick':False,'nominee_father':'','share':''}])    

                query_family = "select name,relation,age,reside,nom_tick,nominee_father,share from contractor_family_information where contractor_id='"+str(value[13])+"' "   
                cursor.execute(query_family)
                result_family = cursor.fetchall()
                if result_family:
                    for val in result_family:
                        fath_list.append([0,False,{'name':val[0],'relation':val[1],'age':val[2],'reside':val[3],'nom_tick':val[4],'nominee_father':val[5],'share':val[6]}])

                query_experience = "select name,address,year11,year12,desg,leaving_salary,reporting_employee,contact_no from contractor_experience where contractor_id='"+str(value[13])+"' "   
                cursor.execute(query_experience)
                result_experience = cursor.fetchall()
                if result_experience:
                    for val in result_experience:
                        exp_list.append([0,False,{'name':val[0],'address':val[1],'year11':val[2],'year12':val[3],'desg':val[4],'leaving_salary':val[5],'reporting_employee':val[6],'contact_no':val[7]}])
                
                emp_id = hr_obj.search(cr, uid, [('sinid','=',value[0]),('active','=',True)])
                if emp_id:
                    raise osv.except_osv(_('Warning !'),_("Contractor Already Exists For This Card No."))
                else:    
                    create_obj=hr_obj.create(cr,uid,{'sinid':value[0],'name':value[1],'doj':value[2],'paycode':value[0],'marital':value[3],'gender':value[4],'birthday':value[5],'mobile_phone':value[6],'permanent_add':value[7],'copy_add':True,'local_add':value[7],'religion':value[11],'blood':value[12],'type':'Contractor','age':age_calc,'active':True,'employee_type':'Worker','employment_type':'Labor','ref_check_by':user_obj.name,'family_id':fath_list,'verf_id':adhar_list,'experience_id':exp_list})
                    print "==============================CONTRACTOR==MASTER==CREATED ============================="
        
        return True
