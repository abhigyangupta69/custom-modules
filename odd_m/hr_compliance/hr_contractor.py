from osv import fields, osv
from openerp import addons, netsvc, tools
import os
import re 
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import strftime
import base64, urllib
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import time

class wizard_change_machine(osv.TransientModel):
    _name = 'wizard.change.machine'
    
    _columns = {
                'sinid': fields.char('P Card', size=32),
#                 'machin_no': fields.char('Machin No', size=32),
#                 'type':fields.selection([('Card','Card No'),('Machine','Machine No')],'Change In',required=True)
                }
    
    def default_get(self, cr, uid, fields, context=None):
        if not context:
            context = {}
        ids = context.get('active_ids',[])
        res = super(wizard_change_machine, self).default_get(cr, uid, fields, context=context)
        for line in self.pool.get('hr.contractorp').browse(cr, uid, ids):
            if 'sinid' in fields:
                res.update({'sinid':line.sinid})
        return res        
        
    def add_change(self, cr, uid, ids, context=None):
        cont_obj = self.pool.get('hr.contractorp')
        if not context:
            context = {}
        cont_ids = context.get('active_ids',[])
        each = self.read(cr, uid, ids, ['sinid'])
        contract_ids = cont_obj.search(cr, uid, [('sinid','=',each[0]['sinid'])])
        if contract_ids:
            raise osv.except_osv(_('warning'), _('This card number is already exsist.'))
        cont_obj.write(cr, uid, cont_ids, {'sinid':each[0]['sinid']})            
        return {'type':'ir.actions.act_window_close'}

class wizard_image_contractor(osv.TransientModel):
    _name = 'wizard.image.contractor'
    
    _columns = {
                'image':fields.binary('Image'),
                'image_name':fields.char('Image Name',size=64,required=True,readonly=True),                
                }
    
    def default_get(self, cr, uid, fields, context=None):
        if not context:
            context = {}
        ids = context.get('active_ids',[])
        res = super(wizard_image_contractor, self).default_get(cr, uid, fields, context=context)
        for line in self.pool.get('hr.contractorp').browse(cr, uid, ids):
            if 'image_name' in fields:                
                res.update({'image_name':line.sinid+'.jpg'})
        return res        
        
    def create_image(self, cr, uid, ids, context=None):        
        if not context:
            context = {}
        time_ids = context.get('active_ids',[])
        each = self.read(cr, uid, ids, ['image_name','image'])
        if each[0]['image_name'] and not each[0]['image']:
            raise osv.except_osv(_('UserError'), _('Please select the image..'))
        try:
            if each[0]['image_name'] and each[0]['image']:
                import io, StringIO
                from PIL import Image
                image_stream = io.BytesIO(each[0]['image'].decode('base64'))
                img = Image.open(image_stream)
                img.thumbnail((240, 200), Image.ANTIALIAS)
                img_stream = StringIO.StringIO()
                img.save(img_stream, "JPEG")
                bin = base64.decodestring(img_stream.getvalue().encode('base64'))
                fname = each[0]['image_name']
                filename = str(os.getcwd()+'/Photo/Contractor/'+each[0]['image_name'])
                f = open(filename , 'wb')
                f.write(bin)
                self.pool.get('hr.contractorp').write(cr, uid, time_ids, {'image_url':str(each[0]['image_name'])})
        except:
            #pass
            raise osv.except_osv(_('warning'), _('Unable to add image, please check your network setting.'))               
        return {'type':'ir.actions.act_window_close'}
    
class hr_shift_line(osv.osv):
    _inherit = 'hr.shift.line'
    
    _columns = {
                'contractor_id':fields.many2one('hr.employee','Contractor',select=True),
                }
class hr_contractor_shift_line(osv.osv):
    _name = "hr.contractor.shift.line"
    _columns = {
                'contractor_id':fields.many2one('hr.contractorp','Contractor',select=True),
                'name':fields.date('Date',required=True,select=True),
                'shift_id':fields.many2one('contr.attendance.shift','Shift',required=True,select=True),
                'department_id':fields.related('contractor_id','department_id',relation='con.department',string='Department',type="many2one"),
                'manager_id':fields.related('contractor_id','parent_id',relation='hr.contractorp',string='Reporting Officer',type="many2one"),
                'user_id':fields.many2one('res.users','Created By',readonly=True),
                }

#    
#class contractor_salary(osv.osv):
#    _name = 'contractor.salary'
#    
#    def _calculate_month(self, cr, uid, ids, name, args, context=None):
#        res = {}
#        for each in self.browse(cr, uid, ids):
#            tm_tuple = datetime.strptime(each.increment_date,'%Y-%m-%d').timetuple()
#            month = tm_tuple.tm_mon
#            res[each.id] = month     
#        return res
#    
#    def _calculate_year(self, cr, uid, ids, name, args, context=None):
#        res = {}
#        for each in self.browse(cr, uid, ids):
#            tm_tuple = datetime.strptime(each.increment_date,'%Y-%m-%d').timetuple()
#            year = tm_tuple.tm_year
#            year_id = self.pool.get('holiday.year').search(cr, uid, [('name','=',year)])
#            if year_id:
#                res[each.id] = year_id[0]  
#            else:
#                raise osv.except_osv(_('Invalid action !'), _('Unable to found year specified.!'))
#        return res
#    
#    
#    _columns = {
#                'contractor_id':fields.many2one('hr.contractorp','Employee',required=True,readonly=True, states={'draft': [('readonly', False)]}),
#                'department_id':fields.related('contractor_id','department_id',relation='hr.department',string='Department',type="many2one",readonly=True),
#                'designation_id':fields.related('contractor_id','designation_id',relation='hr.designation',string='Designation',type="many2one",readonly=True),
#                'type':fields.related('contractor_id','type',selection=[('Wood','Wood'),('Metal','Metal'),('Lohia','Lohia')],string='Type',type="selection",readonly=True),
#                'increment_date':fields.date('Increment Date',required=True,readonly=True, states={'draft': [('readonly', False)]}),
#                'old_salary':fields.float('Old Salary',digits=(16,2),required=True,readonly=True, states={'draft': [('readonly', False)]}),
#                'increment_amt':fields.float('Increment Amt.',digits=(16,2),required=True,readonly=True, states={'draft': [('readonly', False)]}),
#                'month':fields.function(_calculate_month,method=True,type='integer',string='Month',store=True),
#                'year_id':fields.function(_calculate_year,relation="holiday.year",method=True,type='many2one',string='Year',store=True),
#                'state':fields.selection([('draft','Draft'),('done','Done')],'State',readonly=True),
#                'type':fields.related('contractor_id','type',selection=[('Wood','Wood'),('Metal','Metal'),('Lohia','Lohia'),('Kashipur','Kashipur'),('Lodhipur','Lodhipur'),('Prabhat Market','Prabhat Market'),('Galshahid','Galshahid'),('Rajan','Rajan ENC'),('LB Unit-III','LB Unit-III')],string='Working AT',type="selection",readonly=True),
#                }
#    _defaults = {
#                 'increment_date':time.strftime(DEFAULT_SERVER_DATE_FORMAT),
#                 'state':'draft',
#                 }
#    
#    _sql_constraints = [('unique_employee_month_year','unique(contractor_id,increment_date)','Employee salary line for this date is already exist.')]
#    
#    def create(self, cr, uid, vals, context=None):
#        res = {}
#        hr_obj = self.pool.get('hr.employee')
#        old = new = 0.0
#        if 'increment_amt' in vals and vals['increment_amt'] and 'contractor_id' in vals and vals['contractor_id']:
#            old = hr_obj.browse(cr, uid, hr_obj.search(cr, uid, [('id','=',vals['contractor_id'])]))
#            if not old:
#                raise osv.except_osv(('Warning'),("Current salary is zero, waiting for updation."))
#            else:
#                old = old[0].salary
#            new = old + vals['increment_amt']
#            if new > 0.0:
#                hr_obj.write(cr, uid, [vals['contractor_id']], {'salary':new})
#        if 'increment_amt' in vals and vals['increment_amt'] > 0.0:
#            vals.update({'state':'done'})
#        
#        res = super(employee_salary, self).create(cr, uid, vals)
#        return res
#    
#    def write(self, cr, uid, ids, vals, context=None):
#        res = {}
#        hr_obj = self.pool.get('hr.contractorp')
#        old = new = 0.0
#        for each in self.browse(cr, uid, ids):
#            emp_id = each.contractor_id and each.contractor_id.id or False
#            old = each.contractor_id and each.contractor_id.salary or 0.0
#        
#        if 'increment_amt' in vals and vals['increment_amt'] and 'contractor_id' in vals and vals['contractor_id']:
#            old = hr_obj.browse(cr, uid, hr_obj.search(cr, uid, [('id','=',vals['contractor_id'])]))
#            if not old:
#                raise osv.except_osv(('Warning'),("Current salary is zero, waiting for updation."))
#            else:
#                old = old[0].salary
#            new = old + vals['increment_amt']
#            if new > 0.0:
#                hr_obj.write(cr, uid, [vals['contractor_id']], {'salary':new})
#        
#        if 'increment_amt' in vals and vals['increment_amt']:
#            new = old + vals['increment_amt']
#            if new > 0.0:
#                hr_obj.write(cr, uid, [emp_id], {'salary':new})
#        
#        if new <= 0.0:
#            raise osv.except_osv(('Warning'),("Unable to process, increment amount is zero."))
#        vals['state'] = 'done'
#        
#        res = super(employee_salary, self).write(cr, uid, ids, vals)
#        return res
#    
#    def onchange_contractor(self, cr, uid, ids, employee, context=None):
#        res = {}
#        old = 0.0
#        if not employee:
#            res['value'] = {'old_salary':0.0}
#            return res
#        old = self.pool.get('hr.contractorp').browse(cr, uid, employee).salary
#        res['value'] = {'old_salary':old}
#        return res

class hr_contractorp(osv.osv):
    _name = "hr.contractorp"
    _description = "Contractor"
    _inherits = {'resource.resource': "resource_id"}
    
    def get_image(self, cr, uid, ids):
        each = self.read(cr, uid, ids, ['image_url'])
        try:
            if each['image_url']:
                (filename, header) = urllib.urlretrieve('file://'+os.getcwd()+'/Photo/Contractor/'+each['image_url'])
                f = open(filename , 'rb')
                img = base64.encodestring(f.read())
                f.close()
            else:
                (filename, header) = urllib.urlretrieve('file://'+os.getcwd()+'/openerp/addons/designcoplugin/images/default.png')
                f = open(filename , 'rb')
                img = base64.encodestring(f.read())
                f.close()            
        except:
            (filename, header) = urllib.urlretrieve('file://'+os.getcwd()+'/openerp/addons/designcoplugin/images/default.png')
            f = open(filename , 'rb')
            img = base64.encodestring(f.read())
            f.close()           
        return img        
    
    def _get_image(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for each in ids:
            img = self.get_image(cr, uid, each)
            res[each] = img
        return res
    
    def contractor_hire(self, cr, uid, ids, context=None):
        part_obj = self.pool.get('res.partner')
        addr_obj = self.pool.get('res.partner.address')
        partner_id = False
        for each in self.browse(cr, uid, ids):
            if each.type_cont == 'contractor':
                partner_ids = part_obj.search(cr, uid, [('pcard','=',each.sinid)])
                if not partner_ids:
                    ID = self.pool.get('ir.sequence').get(cr,uid,'res.partner')
                    partner_id = part_obj.create(cr, uid, {'name':each.name.upper(),'ID':ID,'pcard':each.sinid,'customer':False,
                                                       'supplier':True,'inhouse_supplier':True,'purchase_type':'inho'})
                    self.write(cr, uid, ids, {'partner_id':partner_id})
                    partner_ids = [partner_id]
                if partner_ids:
                    if not partner_id:
                        part_obj.write(cr, uid, partner_ids,{'name':each.name.upper()})
                        add_ids = addr_obj.search(cr, uid, [('partner_id','=',partner_ids[0])])
                        if add_ids:
                            addr_obj.write(cr, uid, add_ids, {'name':each.name.upper(),
                                                  'street':each.street,'phone':each.phone,'mobile':each.mobile })                        
                    else:
                        addr_obj.create(cr, uid, {'partner_id':partner_id,'name':each.name.upper(),
                                                  'street':each.street,'phone':each.phone,'mobile':each.mobile })                    
        return True

    def create(self, cr, uid, vals, context=None):
#         seq1=False
        type_cont=False
        date1=time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        cur_obj=self.pool.get('hr.contractorp')
        if 'type_cont' in vals and vals['type_cont']:
            type_cont=vals['type_cont']            
        if 'type' in vals and vals['type']:
            type = vals['type']
            
        if type_cont and type not in ('Prabhat Market'):            
            if type_cont == 'contractor':
                if type == 'Designco':
                    seq = self.pool.get('ir.sequence').get(cr, uid, 'hr.contractorp')
#                 seq1 = self.pool.get('ir.sequence').get(cr, uid, 'designco.mach')
                    init=int(seq)
                    code=str(init)
                    code = code.strip()
    #                 init1=int(seq1)
    #                 machin=str(init1)
    #                 machin = machin.strip()
                    code=code+'C' + '0' + str(1)
                    vals.update({'sinid':code,})
                elif type == 'Lodhipur':
                    seq = self.pool.get('ir.sequence').get(cr, uid, 'lodhi.contractorp')
    #                 seq1 = self.pool.get('ir.sequence').get(cr, uid, 'designco.mach')
                    init=int(seq)
                    code=str(init)
                    code = code.strip()
    #                 init1=int(seq1)
    #                 machin=str(init1)
    #                 machin = machin.strip()
                    code=code+'A' + '0' + str(1)
                    vals.update({'sinid':code,})
            if type_cont == 'labour':
                if type == 'Designco':
                    if 'parent_id1' in vals and vals['parent_id1']:
                        vals['parent_id1'] = False
                    #seq = self.pool.get('ir.sequence').get(cr, uid, 'hr.contractorp')
                    contractor=False
                    cont_ids=[]
                    if 'parent_id' in vals and vals['parent_id']:
                        contractor=vals['parent_id']
                        if contractor:
                            sinid=cur_obj.browse(cr ,uid ,contractor).sinid
                            if sinid:
                                code=sinid.split('C')[0]
                                cont_ids=cur_obj.search(cr ,uid ,[('sinid','ilike',code +'%')])
                                max=1
                                if cont_ids:
                                    for cont_id in cont_ids:
                                        new_sinid=cur_obj.browse(cr ,uid ,cont_id).sinid
                                        code_new=new_sinid.split('C')[0]
                                        if code == code_new:
                                            code1=new_sinid.split('C')[1]
                                            if int(code1) > max:
                                                max=int(code1)                                
                                code1=int(max)+1
                                code_now=str(code)
                                if code1 in [0,1,2,3,4,5,6,7,8,9]:
                                    code_now=code_now+'C' + '0' + str(code1)
                                else:
                                    code_now=code_now+'C' + str(code1)
                                vals.update({'sinid':code_now})
                elif type == 'Lodhipur':
                    if 'parent_id1' in vals and vals['parent_id1']:
                        vals['parent_id1'] = False
                    #seq = self.pool.get('ir.sequence').get(cr, uid, 'hr.contractorp')
                    contractor=False
                    cont_ids=[]
                    if 'parent_id' in vals and vals['parent_id']:
                        contractor=vals['parent_id']
                        if contractor:
                            sinid=cur_obj.browse(cr ,uid ,contractor).sinid
                            if sinid:
                                code=sinid.split('A')[0]
                                cont_ids=cur_obj.search(cr ,uid ,[('sinid','ilike',code +'%')])
                                max=1
                                if cont_ids:
                                    for cont_id in cont_ids:
                                        new_sinid=cur_obj.browse(cr ,uid ,cont_id).sinid
                                        code_new=new_sinid.split('A')[0]
                                        if code == code_new:
                                            code1=new_sinid.split('A')[1]
                                            if int(code1) > max:
                                                max=int(code1)                                 
                                code1=int(max)+1
                                code_now=str(code)
                                if code1 in [0,1,2,3,4,5,6,7,8,9]:
                                    code_now=code_now+'A' + '0' + str(code1)
                                else:
                                    code_now=code_now+'A' + str(code1)
                                vals.update({'sinid':code_now})
                                
            if type_cont == 'Supplier':
                if type == 'Designco':
                    seq = self.pool.get('ir.sequence').get(cr, uid, 'hr.contractorp.supplier')
                    seq1 = self.pool.get('ir.sequence').get(cr, uid, 'hr.contractorp.supplier.punch')
                    vals.update({'sinid':seq,'machin_no':seq1})
                                                       
#         if type_cont and type == 'Lodhipur':
#             if type_cont == 'contractor':
#                 seq = self.pool.get('ir.sequence').get(cr, uid, 'lodhi.contractorp')
# #                 seq2 = self.pool.get('ir.sequence').get(cr, uid, 'lodhi.mach')
#                 init=int(seq)
#                 code=str(init)
#                 code = code.strip()
# #                 init1=int(seq2)+28450
# #                 machin=str(init1)
# #                 machin = machin.strip()
#                 code=code+'A' + '0' + str(1)
#                 vals.update({'sinid':code})
#             if type_cont == 'labour':
#                 if 'parent_id1' in vals and vals['parent_id1']:
#                     vals['parent_id1'] = False
#                 #seq = self.pool.get('ir.sequence').get(cr, uid, 'hr.contractorp')
#                 contractor=False
#                 cont_ids=[]
#                 if 'parent_id' in vals and vals['parent_id']:
#                     contractor=vals['parent_id']
#                     if contractor:
#                         sinid=cur_obj.browse(cr ,uid ,contractor).sinid
#                         if sinid:
#                             code=sinid.split('A')[0]
#                             cont_ids=cur_obj.search(cr ,uid ,[('sinid','ilike',code +'%')])
#                             max=1
#                             if cont_ids:
#                                 for cont_id in cont_ids:
#                                     new_sinid=cur_obj.browse(cr ,uid ,cont_id).sinid
#                                     code_new=new_sinid.split('A')[0]
#                                     if code == code_new:
#                                         code1=new_sinid.split('A')[1]
#                                         if int(code1) > max:
#                                             max=int(code1)
#                             
#                             code1=int(max)+1
#                             code_now=str(code)
#                             if code1 in [0,1,2,3,4,5,6,7,8,9]:
#                                 code_now=code_now+'A' + '0' + str(code1)
#                             else:
#                                 code_now=code_now+'A' + str(code1)
#                             vals.update({'sinid':code_now})
#                             
# #                 seq1 = self.pool.get('ir.sequence').get(cr, uid, 'designco.mach')
# #                 init1=int(seq1)+28450
# #                 machin=str(init1)
# #                 machin = machin.strip()
# #                 vals.update({'machin_no':machin})   

        if type_cont and type == 'Prabhat Market':
            if type_cont == 'contractor':
                seq = self.pool.get('ir.sequence').get(cr, uid, 'prabhat.contractorp')
#                 seq2 = self.pool.get('ir.sequence').get(cr, uid, 'lodhi.mach')
                init=int(seq)
                code=str(init)
                code = code.strip()
#                 init1=int(seq2)+28450
#                 machin=str(init1)
#                 machin = machin.strip()
                code=code+'P' + '0' + str(1)
                vals.update({'sinid':code})
            if type_cont == 'labour':
                if 'parent_id1' in vals and vals['parent_id1']:
                    vals['parent_id1'] = False
                #seq = self.pool.get('ir.sequence').get(cr, uid, 'hr.contractorp')
                contractor=False
                cont_ids=[]
                if 'parent_id' in vals and vals['parent_id']:
                    contractor=vals['parent_id']
                    if contractor:
                        sinid=cur_obj.browse(cr ,uid ,contractor).sinid
                        if sinid:
                            code=sinid.split('P')[0]
                            cont_ids=cur_obj.search(cr ,uid ,[('sinid','ilike',code +'%')])
                            max=1
                            if cont_ids:
                                for cont_id in cont_ids:
                                    new_sinid=cur_obj.browse(cr ,uid ,cont_id).sinid
                                    code_new=new_sinid.split('P')[0]
                                    if code == code_new:
                                        code1=new_sinid.split('P')[1]
                                        if int(code1) > max:
                                            max=int(code1)                            
                            code1=int(max)+1
                            code_now=str(code)
                            if code1 in [0,1,2,3,4,5,6,7,8,9]:
                                code_now=code_now+'P' + '0' + str(code1)
                            else:
                                code_now=code_now+'P' + str(code1)
                            vals.update({'sinid':code_now})                                     
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].strip()
            vals['name'] = vals['name'].upper()
        if 'fath_name' in vals and vals['fath_name']:
            vals['fath_name'] = vals['fath_name'].strip()
            vals['fath_name'] = vals['fath_name'].upper()
        if 'street' in vals and vals['street']:
            vals['street'] = vals['street'].strip()
            vals['street'] = vals['street'].upper()        
        res = super(hr_contractorp,self).create(cr, uid, vals, context)        
        for val in self.browse(cr,uid,[res]): 
            if val:
                hr_contractor_shift = self.pool.get('hr.contractor.shift.line').create(cr,uid,{'user_id':uid,'shift_id':val.shift_id.id,'department_id':val.department_id.id,'contractor_id':val.id,'name':date1})
                shift_line = self.pool.get('contr.shift.line').create(cr,uid,{'user_id':uid,'shift_id':val.shift_id.id,'contractor_id':val.id,'name':date1,'department_id':val.department_id.id})

#         if res:
#             seq1 = self.pool.get('ir.sequence').get(cr, uid, 'designco.contractorp')
#             w = self.write(cr,uid,[res],{'machin_no':str(seq1)})
        
        self.contractor_hire(cr, uid, [res], context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'sinid' in vals and vals['sinid']:
            vals['sinid'] = vals['sinid'].strip()
        res = super(hr_contractorp, self).write(cr, uid, ids, vals, context)
        self.contractor_hire(cr, uid, ids, context)
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
#    def _empsalary(self, cr, uid, ids, prop, unknow_none, context=None):
#        res={}
#        for val in self.browse(cr,uid,ids,context):
#            pf = 0.0
##            if val.salary==0.0:
##                raise osv.except_osv(('Warning'),("Please Enter Salary"))  
#            if val.daily:  
#                res[val.id]=val.salary
#            if val.monthly:
#                if val.pf:
#                    if val.salary > 6500:
#                        pf = 780
#                    else:
#                         pf = val.salary * 0.12
#                    res[val.id]=val.salary - pf
#                else:
#                    sal=val.salary   
#                    res[val.id]=sal
#        return res    
#       
#    def _calpf(self, cr, uid, ids, prop, unknow_none, context=None):
#        res={} 
#        pf = 0.0
#        for val in self.browse(cr,uid,ids,context):
#            if val.monthly:
#                if val.salary > 6500:
#                    pf = 780
#                else:
#                     pf = val.salary * 0.12
#            res[val.id]=pf  
#        return res
#    
#    def _calcsh(self, cr, uid, ids, prop, unknow_none, context=None):
#        res={}
#        for val in self.browse(cr,uid,ids,context):
#            cs = 0.0
#            if val.monthly:
#                if val.pf:
#                    if val.salary > 6500:
#                        cs = 884.65
#                    else:
#                         cs = val.salary * 0.1361
#                res[val.id]=cs                
#        return res


    def _check_name(self, cr, uid, ids, context=None):
        str="^-?[a-zA-Z. ]+$"
        obj=self.browse(cr, uid, ids)[0]
        name=obj.name
        if name and len(name) >= 20:
            raise osv.except_osv(_('Invalid Name'), _('Name  must contain 20 char only.'))    
        if name and re.match(str,name) == None:
            return False    
        return True
    def _check_father_name(self, cr, uid, ids, context=None):
        str="^-?[a-zA-Z/\. ]+$"
        obj=self.browse(cr, uid, ids)[0]
        name=obj.fath_name 
        if name and len(name)>= 26:
            raise osv.except_osv(_('Invalid Father Name'), _('Father Name  must contain 20 char only.')) 
        if name and re.match(str,name) == None:
            return False    
        return True
    def _check_address(self,cr,uid,ids,context=None):
        str="^-?[a-zA-Z0-9-/\,. ]+$"
        obj=self.browse(cr, uid, ids)[0]
        name=obj.street
        if name and len(name) >= 80:
            raise osv.except_osv(_('Invalid Address'), _('Address  must contain 80 char only.')) 
        if name and re.match(str,name) == None:
            return False
        else:
            return True
    def _check_mobile(self, cr, uid, ids, context=None):
        str="^-?[0-9]+$"
        obj=self.browse(cr, uid, ids)[0]
        ph=obj.mobile
        alt_ph=obj.alt_mobile
        
        if ph and len(ph)!= 10:
            raise osv.except_osv(_('Invalid Number'), _(' Mobile Number must contain 10 digits only.'))
        if ph and re.match(str, ph) == None:
            return False
        if alt_ph and len(alt_ph)!= 10:
            raise osv.except_osv(_('Invalid Number'), _(' Mobile Number must contain 10 digits only.'))
        if alt_ph and re.match(str, alt_ph) == None:
            return False
        return True
    
#     def _check_dob(self,cr,uid,ids,context=None):
#         obj=self.browse(cr, uid, ids)[0]
#         date1=obj.dob_date
#         date2=obj.joining_date
#         if date1 >= date2:
#             raise osv.except_osv(_('Invalid Date'), _('Please enter a valid  Date !'))
#         days=(datetime.strptime(date2,"%Y-%m-%d").date()-datetime.strptime(date1,"%Y-%m-%d").date()).days
# #        years = days/366.0
# #        years = round(years,2) 
#         if days >= 6574:
#             return True
#         else:
#             raise osv.except_osv(_('Invalid Date'), _('Please enter a valid  Date Of Birth (Minimum 18 years) !'))
        
    def _check_machine(self, cr, uid, ids, context=None):
        str="^-?[0-9]+$"
        obj=self.browse(cr, uid, ids)[0]
        name=obj.machin_no
        if name and len(name) < 5:
            raise osv.except_osv(_('Invalid Machine No'), _('Machine No. must contain 5 integers only.'))    
        if name and re.match(str,name) == None:
            return False    
        return True
    
    _columns = {
        'type_cont': fields.selection([('contractor','Contractor'),('labour','Labour'),('Supplier','Supplier')],'Contractor Type', help="Used to select type of contractor", required=True),#required=True
        'country_id': fields.many2one('res.country', 'Nationality'),
        'dob_date': fields.date("Date of Birth",required=False ),
        'joining_date':fields.date('Joining Date',required=True ,readonly=False),#required=True
        'dob_by_date' : fields.boolean('DOB by Date'),
        'years': fields.integer('Years',size=5,store=False),
        'fath_name': fields.char('Father Name', size=64,required=False),
        'sinid': fields.char('P Card', size=32,readonly=False),#required=True
        'machin_no': fields.char('Machin No', size=8),
        'gender': fields.selection([('male', 'Male'),('female', 'Female')], 'Gender',required=True ),#required=True
        'marital': fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status',required=True ),#required=True
#         'department_id':fields.many2one('hr.department', 'Department', ),#required=True
        'department_id':fields.many2one('con.department', 'Department', ),
        'notes': fields.text('Notes'),
        'parent_id': fields.many2one('hr.contractorp', 'Manager'),
        'parent_id1': fields.many2one('hr.employee', 'Manager'),
        'category_ids': fields.many2many('hr.employee.category', 'employee_category_rel1', 'emp_id1', 'category_id1', 'Categories'),
        'child_ids': fields.one2many('hr.contractorp', 'parent_id', 'Subordinates'),
        'resource_id': fields.many2one('resource.resource', 'Resource', ondelete='cascade',required=True),#required=True
        'coach_id': fields.many2one('hr.contractorp', 'Coach'),
        'job_id': fields.many2one('hr.job', 'Job'),
        'image_url':fields.char('Image URL' , size=256, help="Specify complete path to image when, you are importing images \
             from CSV file. example for local system path=file:///home/directoryname/imagedirectoryname/image.jpg",readonly=True),
        'photo':fields.function(_get_image, type="binary", method=True),
        'color': fields.integer('Color Index'),
        'login': fields.related('user_id', 'login', type='char', string='Login', readonly=1),        
        'partner_id': fields.many2one('res.partner', 'Partner Name', ondelete='set null', select=True, help="Keep empty for a private address, not related to partner."),
        'type':fields.selection([('Designco','Designco'),('Kashipur','Kashipur'),('Lodhipur','Lodhipur'),('Prabhat Market','Prabhat Market'),('Galshahid','Galshahid')],'Working AT',required=True),#required=True
        'function': fields.char('Function', size=128),
        'title': fields.many2one('res.partner.title','Title'),
        'street': fields.char('Address', size=128,required=False),
        'phone': fields.char('Phone', size=64),
        'mobile': fields.char('Mobile', size=64,required=False),
        'alt_mobile': fields.char('Alt. Mobile', size=64,required=False),     
        'company_id': fields.many2one('res.company', 'Company',select=1),
        'designation_id':fields.many2one('hr.designation','Designation'),
        'shift_id':fields.many2one('contr.attendance.shift','Shift', required=True),#required=True
        'shift_lines':fields.one2many('hr.shift.line','contractor_id','Master Shift'),
        'cont_shift_line':fields.one2many('hr.contractor.shift.line','contractor_id','Master Shift'),
        'qualification': fields.char('Qualification', size=64),
#        'shift_ids':fields.function(_calculate_current_shift,method=True,relation='attendance.shift',type='many2one',string='Shift'),
#        "daily":fields.boolean("Daily"),
#        "monthly":fields.boolean("Monthly"),
#        "salary":fields.float("Current Salary"),
#        "new_salary":fields.float("Joining Salary"),
#        "pf":fields.boolean("PF"),
#        "payable":fields.function(_empsalary,method=True,type='float',string="Payable",store=True,),
#        "pfsh":fields.function(_calpf,method=True,type='float',string="pf",store=True,),
#        "cashshare":fields.function(_calcsh,method=True,type='float',string="Company Share",store=True,),
        "state1":fields.selection([("draft","Draft"),("confirmed","Confirmed")],"state",readonly=True),
        #'salary_line':fields.one2many('contractor.salary','contractor_id','Salary Lines'),
        'created_by':fields.many2one('res.users','Created By'),  
        'identity': fields.char('Aadhar No.', size=128),      
    }
    
    _sql_constraints=[('unique_sinid','unique(sinid)','P-Card number must be unique !')]
#     _sql_constraints=[('unique_machin_no','unique(machin_no)','Machin No must be unique !')]    
    
    
    _constraints =  [
        (_check_name, 'must contain only character and spaces', [' name ']),
        (_check_address, 'must contain only character ,spaces and number ',['street']),
        (_check_father_name, ' must contain only character and spaces', ['fath_name']),
        (_check_mobile, 'must contain only integer values', ['Mobile  Number ']),
#         (_check_dob,"should be smaller than today's date",["Date Of Birth"]),
        (_check_machine,"must contain only integer values", ['Punch Number']),
         ]

    _defaults = {
        "state1":'draft',
        'type_cont':'contractor',
#         'sinid': '/',
        'dob_by_date' : lambda * a : True ,
        'joining_date' : fields.date.context_today,
        'created_by': lambda obj, cr, uid, context: uid,
        "machin_no":'000'
        #'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'res.partner.address', context=c),
    }
    
    def process_script(self,cr,uid,ids,context=None):
        res={}
        cont=self.pool.get('hr.contractorp').search(cr,uid,[])
        for val in self.pool.get('hr.contractorp').browse(cr,uid,cont):
            self.pool.get('hr.contractor.shift.line').create(cr,uid,{'name':'02.06.2013','contractor_id':val.id,'shift_id':val.shift_id.id})
        return res
    
    def on_change_years(self,cr,uid,ids,year,context=None):
        res={}
        if not( year < 0):
            dob = (datetime.now() + relativedelta(years=-year)).strftime('%Y-%m-%d')            
            if dob:
                res['value'] = {'dob_date':dob}            
        else :
            return res
        return res

    def draft_con(self,cr,uid,ids,context=None):
        for vals in self.browse(cr,uid,ids,context=None):
            if vals.state1=="draft":
                self.write(cr,uid,ids,{"state1":'confirmed'})
        return True  
#    def onchange_daily(self,cr,uid,ids,process):
#        res={}
#        if process:
#            res['value']={ 'monthly':False,}
#        return res
#    
#    def onchange_monthly(self,cr,uid,ids,process):
#        res={}
#        if process:
#            res['value']={ 'daily':False,}
#        return res
    def onchange_company(self, cr, uid, ids, company, context=None):
        address_id = False
        if company:
            company_id = self.pool.get('res.company').browse(cr, uid, company, context=context)
            address = self.pool.get('res.partner').address_get(cr, uid, [company_id.partner_id.id], ['default'])
            address_id = address and address['default'] or False
        return {'value': {'address_id' : address_id}}
    
    def onchange_department_id(self, cr, uid, ids, department_id, context=None):
        value = {'parent_id': False}
        if department_id:
            department = self.pool.get('con.department').browse(cr, uid, department_id)
            value['parent_id'] = department.manager_id.id    
        return {'value': value}
    
    def onchange_parent_id(self, cr, uid, ids, parent_id, context=None):
        value = {'department_id': False}
        if parent_id:
            parent_id = self.pool.get('hr.contractorp').browse(cr, uid, parent_id)
            value['department_id'] = parent_id.department_id.id    
        return {'value': value}
    
    def onchange_type_cont(self, cr, uid, ids, type_cont, context=None):
        value = {'designation_id': False}
        if type_cont == 'contractor':
            value['designation_id'] = 51
        else:
            value['designation_id'] = 11
        return {'value': value}
    
    def onchange_user(self, cr, uid, ids, user_id, context=None):
        work_email = False
        if user_id:
            work_email = self.pool.get('res.users').browse(cr, uid, user_id, context=context).user_email
        return {'value': {'work_email' : work_email}}
    
    def update_manager(self, cr, uid, ids, context=None):
        qry = "select hr.id,substring(hr.sinid,1,position('C' in hr.sinid)), hr.sinid, res.name, "\
        "hr.type_cont from hr_contractorp as hr left join resource_resource as res on "\
        "(hr.resource_id=res.id) where (sinid ilike '%C1' or sinid ilike '%C01')"
        
        cr.execute(qry)
        temp = cr.fetchall()
        print_list = []
        for val in temp:
            code = val[1]
            mg_id = val[0]
            
            qry1 = "select hr.id, hr.sinid,res.name,hr.type_cont from hr_contractorp as hr left join resource_resource "\
            "as res on (hr.resource_id=res.id) where type_cont='labour' and substring(hr.sinid,1,position('C' in hr.sinid)) "\
            " = '"+str(code)+"'"
            
            cr.execute(qry1)
            temp1 = cr.fetchall()
            
            for val1 in temp1:
                self.write(cr, uid, [val1[0]],{'parent_id':mg_id})
#                 record = val1[0],val1[1],val1[2],val[2],val[3],val[4],
#                 print "=======record=========",val1[0],val1[1],val1[2],val[2],val[3],val[4]
#                 print_list.append(list(record))
           
#         import csv     
#         writer = csv.writer(open("/tmp/contractor_lobour.csv", "wb"))
# 
#         for data in print_list:
#             row = []
#             for d in data:
#                 if isinstance(d, basestring):
#                     d = d.replace('\n',' ').replace('\t',' ')
#                     try:
#                         d = d.encode('utf-8')
#                     except:
#                         pass
#                 if d is False: d = None
#                 row.append(d)
#     
#             writer.writerow(row)
    
# class employee_barcode(osv.osv):
#     
#     _inherit = 'employee.barcode'
#     
#     _columns = {
#                 'contractor_id':fields.many2one('hr.contractorp','Contractor Name',readonly=True),
#                 }
    
class con_department(osv.osv):
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','manager_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['manager_id']:
                name = name+' / '+record['manager_id'][1]
            res.append((record['id'], name))
        return res

    _name = "con.department"
    _columns = {
        'name': fields.char('Department Name', size=64, required=True),
        'manager_id': fields.many2one('hr.employee', 'Manager'),
        'company_id': fields.many2one('res.company', 'Company', select=True, required=False),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'con.department', context=c),
                }  
con_department()
