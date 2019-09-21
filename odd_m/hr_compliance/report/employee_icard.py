import time
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp  import api ,models
from dateutil import rrule

class employee_icard(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_icard, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_employee_icard_designco(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_icard_designco'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_icard_designco'
    _wrapped_report_class = employee_icard
    
    
    
class employee_icard_lohia(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_icard_lohia, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_employee_icard_lohia(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_icard_lohia'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_icard_lohia'
    _wrapped_report_class = employee_icard_lohia    
    
    
    
    

class employee_access_icard(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_access_icard, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  }) 
        
          
class report_employee_access_icard(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_access_icard'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_access_icard'
    _wrapped_report_class = employee_access_icard
    
    
    
    
class employee_access_icard_paint(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_access_icard_paint, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  }) 
        
          
class report_employee_access_icard_paint(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_access_icard_paint'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_access_icard_paint'
    _wrapped_report_class = employee_access_icard_paint  
    
     
    
class employee_access_icard_lacquer(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_access_icard_lacquer, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  }) 
        
          
class report_employee_access_icard_lacquer(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_access_icard_lacquer'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_access_icard_lacquer'
    _wrapped_report_class = employee_access_icard_lacquer    


class designco_employee_icard(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(designco_employee_icard, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_employee_icard_designco_all(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_icard_designco_all'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_icard_designco_all'
    _wrapped_report_class = designco_employee_icard
    
    
    
    
'''
=======================================    Designco Employee  Access  I CARD'S  ===============================================

'''   
 
class green_access_icard_designco(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(green_access_icard_designco, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_green_access_icard_designco(osv.AbstractModel):
    _name = 'report.hr_compliance.report_green_access_icard_designco'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_green_access_icard_designco'
    _wrapped_report_class = green_access_icard_designco
    
    
    
class orange_access_icard_designco(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(orange_access_icard_designco, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_orange_access_icard_designco(osv.AbstractModel):
    _name = 'report.hr_compliance.report_orange_access_icard_designco'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_orange_access_icard_designco'
    _wrapped_report_class = orange_access_icard_designco    
 
 
 
'''
=======================================    Designco Contractor  Access  I CARD'S  ===============================================

'''   
 
class contractor_green_access_icard_designco(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_green_access_icard_designco, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_contractor_green_access_icard_designco(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_green_access_icard_designco'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_green_access_icard_designco'
    _wrapped_report_class = contractor_green_access_icard_designco
    
    
    
class contractor_orange_access_icard_designco(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_orange_access_icard_designco, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_contractor_orange_access_icard_designco(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_orange_access_icard_designco'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_orange_access_icard_designco'
    _wrapped_report_class = contractor_orange_access_icard_designco 
 
 
 
 
 
 
    
    
    
    
    
    
    
    
    
    
    
     
    
# class employee_access_icard_warehouse(report_sxw.rml_parse):
#     
#     def __init__(self, cr, uid, name, context):
#         super(employee_access_icard_warehouse, self).__init__(cr, 1, name, context=context)
#         self.count=0
#         self.localcontext.update({
#                                   }) 
#         
#           
# class report_employee_access_icard_warehouse(osv.AbstractModel):
#     _name = 'report.hr_compliance.report_employee_access_icard_warehouse'
#     _inherit = 'report.abstract_report'
#     _template = 'hr_compliance.report_employee_access_icard_warehouse'
#     _wrapped_report_class = employee_access_icard_warehouse     
#     
    
    
            
        
#                                    ALL CONTRACTOR ICARD REPORT
        
        
class contractor_icard(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_icard, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_contractor_icard_designco(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_icard_designco'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_icard_designco'
    _wrapped_report_class = contractor_icard
    
    
    
class contractor_icard_lohia(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_icard_lohia, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_contractor_icard_lohia(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_icard_lohia'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_icard_lohia'
    _wrapped_report_class = contractor_icard_lohia    
    
    
    
    

class contractor_access_icard_packing(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_access_icard_packing, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  }) 
        
          
class report_contractor_access_icard_packing(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_access_icard_packing'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_access_icard_packing'
    _wrapped_report_class = contractor_access_icard_packing
    
    
    
    
class contractor_access_icard_paint(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_access_icard_paint, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  }) 
        
          
class report_contractor_access_icard_paint(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_access_icard_paint'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_access_icard_paint'
    _wrapped_report_class = contractor_access_icard_paint  
    
     
    
class contractor_access_icard_lacquer(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_access_icard_lacquer, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  }) 
        
          
class report_contractor_access_icard_lacquer(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_access_icard_lacquer'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_access_icard_lacquer'
    _wrapped_report_class = contractor_access_icard_lacquer    
        
        
class designco_contractor_icard_yellow(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(designco_contractor_icard_yellow, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_contractor_icard_designco_all(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_icard_designco_all'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_icard_designco_all'
    _wrapped_report_class = designco_contractor_icard_yellow
    





class neem_trainee_icard_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(neem_trainee_icard_report, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_neem_trainee_icard(osv.AbstractModel):
    _name = 'report.hr_compliance.report_neem_trainee_icard'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_neem_trainee_icard'
    _wrapped_report_class = neem_trainee_icard_report
    
    
'''
=======================================    Designco Neem  Access  I CARD'S  ===============================================

'''   
 
class neem_green_access_icard_designco(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(neem_green_access_icard_designco, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_neem_green_access_icard_designco(osv.AbstractModel):
    _name = 'report.hr_compliance.report_neem_green_access_icard_designco'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_neem_green_access_icard_designco'
    _wrapped_report_class = neem_green_access_icard_designco
    
    
    
class neem_orange_access_icard_designco(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(neem_orange_access_icard_designco, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_father":self.get_father,
                                 
        
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y %H:%M:%S")
         return date1
      
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_father(self,emp_id):
        res={}
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res    
    
                
    
class report_neem_orange_access_icard_designco(osv.AbstractModel):
    _name = 'report.hr_compliance.report_neem_orange_access_icard_designco'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_neem_orange_access_icard_designco'
    _wrapped_report_class = neem_orange_access_icard_designco    
    
    
    
        
