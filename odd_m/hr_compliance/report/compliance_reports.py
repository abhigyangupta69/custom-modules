import time
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class form16(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(form16, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
            'get_doj': self.get_doj,
            'get_data':self.get_data
              })
        
    def get_data(self,emp_id):
        res={}
        qry = "select name,relation from family where nom_tick=True and employee_id='"+str(emp_id)+"' "
        self.cr.execute(qry)
        temp = self.cr.fetchall()
        if temp:
            res = temp
        else:
            res = ' '    
        return res   
           
        
    def get_doj(self,doj): 
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
        return date1
           
   
report_sxw.report_sxw('report.form16', 'wiz.employee.compliance', 'addons/hr_compliance/report/form16.rml', parser=form16,header='external')


class formf(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(formf, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  'get_data':self.get_data
              
              })
        
    def get_data(self,family_id,emp_id):
        res={}
        if family_id :
            qry = "select name,address,relation,age,share from family where nom_tick=True and employee_id='"+str(emp_id)+"' order by age"
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            return temp
            if temp:
                res = temp
            else:
                res = ' '    
        return res   
       
report_sxw.report_sxw('report.formf', 'wiz.employee.compliance', 'addons/hr_compliance/report/formf.rml', parser=formf,header='external')



#class service_record(report_sxw.rml_parse):
#
#    def __init__(self, cr, uid, name, context):
#        super(service_record, self).__init__(cr, 1, name, context=context)
#        self.localcontext.update({
#                                 'get_doj':self.get_doj, 
#                                 'get_residing':self.get_residing,
#                                 'get_father':self.get_father,
#                                 "get_wife":self.get_wife,
#                                 "get_account":self.get_account,
#                                 "get_bank":self.get_bank
#        
#                                   })
#        
#    def get_doj(self,doj):  
#         date1 = datetime.strptime(doj,"%Y-%m-%d")
#         date1 = date1.strftime("%d-%m-%Y")
#         return date1  
#     
#    def get_residing(self,resd):
#        if resd==True:
#            resd='Yes'
#        else:
#            resd='No'
#        return resd  
#    
#    def get_father(self,family_id,emp_id):
#        res={}
#        qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
#        self.cr.execute(qry)
#        temp = self.cr.fetchall()
#        if temp:
#            res = temp
#        else:
#            res = ' '    
#        return res
#       
#    
#    def get_wife(self,family_id,emp_id ):
#        res={}
#        qry = "select name from family where relation='Wife' and employee_id='"+str(emp_id)+"'  "
#        self.cr.execute(qry)
#        temp = self.cr.fetchall()
#        if temp:
#            res = temp
#        else:
#            res = ' '  
#        return res
#    
#    def get_account(self,verf_id,emp_id):
#        res={}
#        qry="select id_no,remark  from  verification where proof_id='Bank_ Account_ No' and employee_id='"+str(emp_id)+"' "
#        self.cr.execute(qry)
#        temp = self.cr.fetchall()
#        if temp:
#            res = temp
#        else:
#            res = ' '  
#        return res
#    
#    def get_bank(self,verf_id,emp_id):
#        res={}
#        qry="select remark from  verification where proof_id='Bank_ Account_ No' and employee_id='"+str(emp_id)+"' "
#        self.cr.execute(qry)
#        temp = self.cr.fetchall()
#        if temp:
#            res = temp
#        else:
#            res = ' '  
#        return res
#            
#    
#
#
#report_sxw.report_sxw('report.service.record', 'wiz.employee.compliance', 'addons/hr_compliance/report/service_record.rml', parser=service_record,header='external')


class employee_verification(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(employee_verification, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
            
              })
       
report_sxw.report_sxw('report.employee_verification', 'wiz.employee.compliance', 'addons/hr_compliance/report/employee_verification.rml', parser=employee_verification,header='external')


#                                                  CONTRACTOR VERIFICATION REPORT

class contractor_verification(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(contractor_verification, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
            
              })
       
report_sxw.report_sxw('report.contractor.verification', 'wiz.contractor.compliance', 
                      'addons/hr_compliance/report/contractor_verification.rml', parser=contractor_verification,header='external')

#                                                  CONTRACTOR Formf REPORT

class contractor_formf(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(contractor_formf, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  'get_data':self.get_data
              
              })
        
    def get_data(self,family_id,emp_id):
        res={}
        if family_id :
            qry = "select name,address,relation,age,share from family where nom_tick=True and employee_id='"+str(emp_id)+"' order by age"
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            return temp
            if temp:
                res = temp
            else:
                res = ' '    
        return res   
       
report_sxw.report_sxw('report.contractor.formf', 'wiz.contractor.compliance', 
                      'addons/hr_compliance/report/contractor_formf.rml', parser=contractor_formf,header='external')


#                                                  CONTRACTOR Form16 REPORT

class contractor_form16(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(contractor_form16, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
            'get_doj': self.get_doj,
            'get_data':self.get_data
              })
        
    def get_data(self,emp_id):
        res={}
        qry = "select name,relation from family where nom_tick=True and employee_id='"+str(emp_id)+"' "
        self.cr.execute(qry)
        temp = self.cr.fetchall()
        if temp:
            res = temp
        else:
            res = ' '    
        return res   
           
        
    def get_doj(self,doj): 
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
        return date1
           
   
report_sxw.report_sxw('report.contractor.form16', 'wiz.contractor.compliance',
                       'addons/hr_compliance/report/contractor_form16.rml', parser=contractor_form16,header='external')
