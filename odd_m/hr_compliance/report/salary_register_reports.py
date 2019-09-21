import time
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp  import api ,models
import time
import calendar
import math
from openerp.tools.translate import _
import psycopg2


# [[===============================[[    SALARY REGISTER  REPORT  ]]===============================================]]

class salary_register(report_sxw.rml_parse):
    
    def server_connect(self):
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
    
    def __init__(self, cr, uid, name, context):
        super(salary_register, self).__init__(cr, 1, name, context=context)
        
        self.count=0
        self.basic_total=0.0
        self.basic1_total=0.0
        self.total_ot_amount=0.0
        self.gross_pay_total=0.0
        self.deduction_total=0.0
        self.total_deduction=0.0
        self.amount_paid_total=0.0
        self.pf_total=0.0
        self.esi_total=0.0
        self.tds_total=0.0
        self.sal_advance=0.0
        self.loan_advance=0.0
        self.vpf_total=0.0
        
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_data":self.get_data,
                                  "get_basic1_total":self.get_basic1_total,
                                  "get_basic_total":self.get_basic_total,
                                  "get_ot_total":self.get_ot_total,
                                  "get_gross_pay":self.get_gross_pay,
                                  "get_total_deduction":self.get_total_deduction,
                                  "get_pf_total":self.get_pf_total,
                                  "get_esi_total":self.get_esi_total,
                                  "get_tds_total":self.get_tds_total,
                                  "get_amount_paid_total":self.get_amount_paid_total,
                                  "get_father":self.get_father,
                                  "get_sal_advance":self.get_sal_advance,
                                  "get_loan_advance":self.get_loan_advance,
                                  "get_vpf_total":self.get_vpf_total,
                                  "get_account_no":self.get_account_no
                                  })            
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
 
   
    def get_account_no(self,emp_sinid):
        res={}
        conn = self.server_connect()
        cursor = conn.cursor()

        if emp_sinid:
             emp_query = "select account_number from hr_employee where sinid='"+str(emp_sinid)+"' "   
             cursor.execute(emp_query)
             result = cursor.fetchall() 
             if   result :
                 res= result[0][0]
             else:
                 res=''    
        return res
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y")
         return date1


    def get_sequence(self):
        self.count=self.count+1
        return self.count
     
    def get_data(self,month,company,department,employee):
        list_ids = []
        l = []
        emp_obj = self.pool.get('hr.employee')
        if department and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        
        
#        if len(list_ids) == 0 :   
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        
        if len(list_ids) == 1 :
            qry =   "select hr.sinid,res.name,hr.id,desg.name,hd.name,hr.esi_number,hr.uan,spl.work_day,spl.week_leave,spl.holiday_leave,sum(spl.sick_leave + spl.casual_leave + spl.compensatory_leave + spl.earned_leave),"\
                    " spl.days,spl.basic,sum(spl.overtime_amount+spl.sun_overtime_amount),spl.total_amount,spl.esi,spl.epf,spl.tds,spl.kharcha,spl.loan, "\
                    " sum(spl.esi+spl.epf+spl.tds+spl.kharcha+spl.loan+spl.vpf),rp.street,rc.name,spl.days_amount,spl.grand_total,spl.month_days,spl.total_over_time "\
                    " ,spl.other_salary,spl.other_salary_amount,spl.factory_work,spl.vpf from salary_payment_line as spl " \
                    "  left join hr_employee as hr on spl.employee_id=hr.id left join resource_resource as res on (hr.resource_id=res.id) left join  hr_job as desg on (hr.job_id=desg.id) "\
                    "   left join hr_department as hd on (hr.department_id=hd.id) left join res_company as rc on (res.company_id=rc.id) left join res_partner as rp on (rc.partner_id=rp.id) where spl.month='"+str(month.month)+"'"\
                    "  and spl.year_id='"+str(month.year_id.id)+"' and spl.employee_id = '"+str(list_ids[0])+"' "\
                    " group by hr.sinid,res.name,hr.father_name,desg.name,hd.name,hr.esi_number,hr.uan,spl.days,spl.week_leave,spl.holiday_leave,spl.work_day,hr.id ," \
                    " spl.month_days,spl.basic,spl.overtime_amount,spl.esi,spl.epf,spl.tds,spl.month_days,spl.kharcha,spl.loan,rp.street,rc.name,spl.days_amount,spl.grand_total,spl.total_amount,spl.total_over_time,spl.other_salary,spl.other_salary_amount,spl.factory_work,spl.vpf order by hr.sinid "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            
        else:
            qry =   "select hr.sinid,res.name,hr.id,desg.name,hd.name,hr.esi_number,hr.uan,spl.work_day,spl.week_leave,spl.holiday_leave,sum(spl.sick_leave + spl.casual_leave + spl.compensatory_leave + spl.earned_leave),"\
                    " spl.days,spl.basic,sum(spl.overtime_amount+spl.sun_overtime_amount),spl.total_amount,spl.esi,spl.epf,spl.tds,spl.kharcha,spl.loan, "\
                    " sum(spl.esi+spl.epf+spl.tds+spl.kharcha+spl.loan+spl.vpf),rp.street,rc.name,spl.days_amount,spl.grand_total,spl.month_days,spl.total_over_time"\
                    " ,spl.other_salary,spl.other_salary_amount,spl.factory_work,spl.vpf from salary_payment_line as spl " \
                    "  left join hr_employee as hr on spl.employee_id=hr.id left join resource_resource as res on (hr.resource_id=res.id) left join  hr_job as desg on (hr.job_id=desg.id) "\
                    "   left join hr_department as hd on (hr.department_id=hd.id) left join res_company as rc on (res.company_id=rc.id) left join res_partner as rp on (rc.partner_id=rp.id) where spl.month='"+str(month.month)+"'"\
                    "  and spl.year_id='"+str(month.year_id.id)+"' and spl.employee_id in "+str(tuple(list_ids))+" "\
                    " group by hr.sinid,res.name,hr.father_name,desg.name,hd.name,hr.esi_number,hr.uan,spl.days,spl.week_leave,spl.holiday_leave,spl.work_day,hr.id ," \
                    " spl.month_days,spl.basic,spl.overtime_amount,spl.esi,spl.epf,spl.tds,spl.month_days,spl.kharcha,spl.loan,rp.street,spl.total_over_time,rc.name,spl.days_amount,spl.grand_total,spl.total_amount,spl.other_salary,spl.other_salary_amount,spl.factory_work,spl.vpf order by hr.sinid "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
        if temp :
            for val in  temp :       
                 self.basic_total+=val[12]+val[27] 
                 self.basic1_total+=val[23]+val[28]
                 if val[13]:
                     self.total_ot_amount += val[13]
                 if val[14]:
                     self.gross_pay_total+=val[14]
                 if val[20]:
                     self.total_deduction+=val[20]
                 if val[24]:
                     self.amount_paid_total+=val[24]
                 if val[16]:    
                     self.pf_total+=val[16]
                 if val[15]:    
                     self.esi_total+=val[15]
                 if val[17]:    
                     self.tds_total+=val[17]
                 if val[18]:    
                     self.sal_advance+=val[18]
                 if val[19]:    
                     self.loan_advance+=val[19] 
                 if val[30]:     
                     self.vpf_total+=val[30]
                                
            self.get_basic_total()
            self.get_basic1_total()
            self.get_ot_total()
            self.get_gross_pay()
            self.get_total_deduction()
            self.get_amount_paid_total()
            self.get_pf_total()
            self.get_esi_total()
            self.get_tds_total()
            self.get_sal_advance()
            self.get_loan_advance()
            self.get_vpf_total()            
            return temp
        
    def get_pf_total(self):
        return self.pf_total 
    
    def get_esi_total(self):
        return self.esi_total 
    
    def get_tds_total(self):
        return self.tds_total        
        
    def get_basic_total(self):
        return self.basic_total 
    
    def get_ot_total(self):
        return self.total_ot_amount
    
    def get_gross_pay(self):
        return self.gross_pay_total
    
    def get_total_deduction(self):
        return self.total_deduction
    
    def get_amount_paid_total(self):
        return self.amount_paid_total 
     
    def get_basic1_total(self):
        return self.basic1_total     

    def get_sal_advance(self):
        return self.sal_advance        

    def get_loan_advance(self):
        return self.loan_advance        

    def get_vpf_total(self):
        return self.vpf_total        

class report_salary_register(osv.AbstractModel):
    _name = 'report.hr_compliance.report_salary_register'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_salary_register'
    _wrapped_report_class = salary_register
    
    
 # [[===============================[[    SALARY SLIP REPORT  ]]===============================================]]
  
     
class salary_slip(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
      
        super(salary_slip, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_time":self.get_time,
                                  "get_data":self.get_data
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y")
         return date1
  
     
    def get_data(self,month,company,department,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if department and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        
#        if len(list_ids) == 0 :
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        
        if len(list_ids) == 1 :
           qry = "select res.name,desg.name,hr.sinid,hd.name,hr.uan,hr.esi_number,spl.work_day,spl.days,spl.week_leave,spl.holiday_leave,sum(spl.casual_leave + spl.sick_leave + spl.compensatory_leave + spl.earned_leave),spl.total_over_time,"\
                    " spl.basic,spl.days_amount,sum(spl.overtime_amount+spl.sun_overtime_amount),sum(spl.days_amount+spl.overtime_amount+spl.sun_overtime_amount+spl.other_salary_amount),spl.esi,spl.epf,spl.loan,spl.kharcha,spl.tds,sum(spl.esi+spl.epf+spl.loan+spl.kharcha+spl.tds+spl.vpf),spl.grand_total,rc.name,rp.street,rp.city,rp.zip,spl.other_salary,spl.other_salary_amount,spl.factory_work,spl.vpf from salary_payment_line as spl " \
                    "  left join hr_employee as hr on spl.employee_id=hr.id left join resource_resource as res on (hr.resource_id=res.id) left join  hr_job as desg on (hr.job_id=desg.id) "\
                    "   left join hr_department as hd on (hr.department_id=hd.id) left join res_company as rc on (res.company_id=rc.id) left join res_partner as rp on (rc.partner_id=rp.id) "\
                     "  where spl.month='"+str(month.month)+"' and spl.year_id='"+str(month.year_id.id)+"'  and spl.employee_id = '"+str(list_ids[0])+"'  "\
                      " group by res.name,desg.name,hr.sinid,hd.name,hr.uan,hr.esi_number,spl.days,spl.week_leave,spl.casual_leave,spl.holiday_leave,spl.sick_leave,spl.compensatory_leave,spl.earned_leave,rc.name,rp.street,rp.city,rp.zip,"\
                      "spl.basic,spl.days_amount,spl.esi,spl.epf,spl.loan,spl.kharcha,spl.tds,spl.grand_total,spl.work_day,spl.total_over_time,spl.other_salary,spl.other_salary_amount,spl.factory_work,spl.vpf order by hr.sinid " 
           self.cr.execute(qry)
           temp = self.cr.fetchall()
           
        else :     
              qry = "select res.name,desg.name,hr.sinid,hd.name,hr.uan,hr.esi_number,spl.work_day,spl.days,spl.week_leave,spl.holiday_leave,sum(spl.casual_leave + spl.sick_leave + spl.compensatory_leave + spl.earned_leave),spl.total_over_time,"\
                    " spl.basic,spl.days_amount,sum(spl.overtime_amount+spl.sun_overtime_amount),sum(spl.days_amount+spl.overtime_amount+spl.sun_overtime_amount+spl.other_salary_amount),spl.esi,spl.epf,spl.loan,spl.kharcha,spl.tds,sum(spl.esi+spl.epf+spl.loan+spl.kharcha+spl.tds+spl.vpf),spl.grand_total,rc.name,rp.street,rp.city,rp.zip,spl.other_salary,spl.other_salary_amount,spl.factory_work,spl.vpf from salary_payment_line as spl " \
                    "  left join hr_employee as hr on spl.employee_id=hr.id left join resource_resource as res on (hr.resource_id=res.id) left join  hr_job as desg on (hr.job_id=desg.id) "\
                    "   left join hr_department as hd on (hr.department_id=hd.id) left join res_company as rc on (res.company_id=rc.id) left join res_partner as rp on (rc.partner_id=rp.id) "\
                    "  where spl.month='"+str(month.month)+"' and spl.year_id='"+str(month.year_id.id)+"'  and spl.employee_id in "+str(tuple(list_ids))+"  "\
                    " group by res.name,desg.name,hr.sinid,hd.name,hr.uan,hr.esi_number,spl.days,spl.week_leave,spl.casual_leave,spl.holiday_leave,spl.sick_leave,spl.compensatory_leave,spl.earned_leave,rc.name,rp.street,rp.city,rp.zip,"\
                    "spl.basic,spl.days_amount,spl.esi,spl.epf,spl.loan,spl.kharcha,spl.tds,spl.grand_total,spl.work_day,spl.total_over_time,spl.other_salary,spl.other_salary_amount,spl.factory_work,spl.vpf order by hr.sinid " 
              self.cr.execute(qry)
              temp = self.cr.fetchall()
                            
        return temp
   
class report_salary_slip(osv.AbstractModel):
    _name = 'report.hr_compliance.report_salary_slip'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_salary_slip'
    _wrapped_report_class = salary_slip
      
  
  # [[===============================[[    ESI CONTRIBUTION REPORT  ]]===============================================]]
   
class esi_contribution(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(esi_contribution, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.esi=0.0
        self.gross=0.0
        self.emp_cont=0.0
        self.total_cont=0.0
        
        
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_data":self.get_data ,
                                  "get_gross":self.get_gross,
                                  "get_esi":self.get_esi,   
                                  "get_emplopyer_cont":self.get_emplopyer_cont ,
                                  "get_total_cont":self.get_total_cont          
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y")
         return date1
      
    def get_sequence(self):
        self.count=self.count+1
        return self.count  
      
    def get_data(self,month,company,department,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if department and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('esi_tick','=',True),('type','=','Employee')])
        elif department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('esi_tick','=',True),('type','=','Employee')])
        elif employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('company_id','=',company.id),('active','=',True),('esi_tick','=',True),('type','=','Employee')])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id),('active','=',True),('esi_tick','=',True),('type','=','Employee')])
#        if len(list_ids) == 0 :
#            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))
#        print"======list_ids=====",list_ids
        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,hr.esi_number,spl.employee_name,hd.name,spl.total_amount,spl.esi,spl.days from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.esi <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,hr.esi_number,spl.employee_name,hd.name,spl.total_amount,spl.esi,spl.days from salary_payment_line as spl  "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.esi <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 
#        if not temp :
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        for val in temp :
            if val[4]:
                self.gross = self.gross + val[4]
            if val[5]:
                self.esi=self.esi+val[5] 
        return temp
    
    
    def get_gross(self) :
        return self.gross
    
    def get_esi(self) :
        return self.esi
    
    def get_emplopyer_cont(self):
        self.emp_cont= (math.ceil((4.75*self.gross)/100 )) 
        return self.emp_cont
    
    def get_total_cont(self):
        self.total_cont=self.emp_cont+self.esi
        return  self.total_cont
         
    
class report_esi_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_esi_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_esi_contribution'
    _wrapped_report_class = esi_contribution
    
    
 # [[===============================[[    PF CONTRIBUTION REPORT  ]]===============================================]]    
    
    
class pf_contribution(report_sxw.rml_parse):
    
    seq = 0
    epf_wages = 0
    epf = 0
    eps = 0
    diff = 0
    def __init__(self, cr, uid, name, context):
        super(pf_contribution, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  "get_epf_wages":self.get_epf_wages,
                                  "get_epf":self.get_epf,
                                  "get_eps":self.get_eps,
                                  "get_diff":self.get_diff,
                                  })
        
    def get_sequence(self):
        self.seq = self.seq + 1
        return self.seq
        
        
    def get_data(self,month,company,department,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if department and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id),('active','=',True),('type','=','Employee')])
#        if len(list_ids) == 0 :
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
         
        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,hr.pf_number,spl.employee_name,spl.gross,spl.epf,spl.epf1,spl.epf2 from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.epf <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,hr.pf_number,spl.employee_name,spl.gross,spl.epf,spl.epf1,spl.epf2 from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.epf <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 
#        if not temp :
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        for val in temp :
            if val[3]:
                self.epf_wages = self.epf_wages + val[3]
            if val[4]:    
                self.epf = self.epf + val[4]
            if val[5]:    
                self.eps = self.eps + val[5]
            if val[6]:    
                self.diff = self.diff + val[6]
        return temp
    
    def get_epf_wages(self) :
        return round(self.epf_wages,0)
    
    def get_epf(self) :
        return round(self.epf,0)

    def get_eps(self) :
        return round(self.eps,0)

    def get_diff(self) :
        return round(self.diff,0)
    
    
class report_pf_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_pf_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_pf_contribution_temp_id'
    _wrapped_report_class = pf_contribution
    
    
# [[===============================[[    TDS CONTRIBUTION REPORT  ]]===============================================]]     





class tds_contribution(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(tds_contribution, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.tds=0.0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  "get_tds":self.get_tds
                    
                                  })   
        
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_data(self,month,company,department,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if department and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id),('active','=',True),('type','=','Employee')])
#        if len(list_ids) == 0 :
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,desg.name,spl.tds from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id)  left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.tds <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,desg.name,spl.tds from salary_payment_line as spl  "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"'and spl.tds <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 
#        if not temp :
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        
        for val in temp :
            if val[4]:
                  self.tds = self.tds + val[4]
        return temp 
    
    def get_tds(self):   
        return self.tds         
                      
        
class report_tds_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_tds_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_tds_contribution'
    _wrapped_report_class = tds_contribution
            
  
  # [[===============================[[ -->   LOAN CONTRIBUTION REPORT <-- ]]===============================================]]  
  
  
class loan_contribution(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(loan_contribution, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.curr_loan=0.0
        self.loan_emi=0.0
        self.localcontext.update({
                                 "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  "get_curr_loan":self.get_curr_loan,
                                  "get_loan_emi":self.get_loan_emi
                    
                                  })   
        
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_data(self,month,company,department,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if department and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id),('active','=',True),('type','=','Employee')])
#        if len(list_ids) == 0 :
#            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))
        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,desg.name,spl.current_loan,spl.loan from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id)  left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.loan <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,desg.name,spl.current_loan,spl.loan  from salary_payment_line as spl  "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.loan <>0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 
#        if not temp :
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        
        for val in temp :
            if val[4]:
                  self.curr_loan = self.curr_loan + val[4]
            if val[5]: 
                 self.loan_emi =  self.loan_emi + val[5]           
        return temp
    
    def get_curr_loan(self):   
        return  self.curr_loan   
          
    def get_loan_emi(self):   
        return self.loan_emi        
        
class report_loan_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_loan_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_loan_contribution'
    _wrapped_report_class = loan_contribution    
    
    
    
# [[ ===========================================[[ ADVANCE REPORT ]]========================================== ]]     
        
class advance_contribution(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(advance_contribution, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.kharcha=0.0
        self.localcontext.update({
                                 "get_sequence":self.get_sequence,
                                 "get_data":self.get_data,
                                 "get_kharcha":self.get_kharcha
                                  })   
        
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    
    def get_data(self,month,company,department,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if department and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif department :
            list_ids = emp_obj.search(self.cr, 1, [('department_id', '=', department.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        elif employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('company_id','=',company.id),('active','=',True),('type','=','Employee')])
        else:
            list_ids = emp_obj.search(self.cr, 1, [('company_id','=',company.id),('active','=',True),('type','=','Employee')])
#        if len(list_ids) == 0 :
#            raise osv.except_osv(('Warning !'),("Record Not Found !!!"))
        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,spl.kharcha,desg.name from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id)  left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.kharcha <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,spl.kharcha,desg.name from salary_payment_line as spl  "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.kharcha <>0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 
#        if not temp :
#            raise osv.except_osv(_('Warning !'),_("Record Not Found !!!"))
        
        for val in temp :
            if val[3]:
                  self.kharcha = self.kharcha + val[3]
        return temp 
    
    def get_kharcha(self):   
        return self.kharcha    
        
class report_advance_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_advance_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_advance_contribution'
    _wrapped_report_class = advance_contribution                   
        
            
        
        
        
                                                    
                                                                    
#                                             CONTRACTOR SALARY REPORT       
 
 
 # [[===============================[[  CONTRACTOR  SALARY REGISTER  REPORT  ]]===============================================]]

class contractor_salary_register(report_sxw.rml_parse):
    
    def server_connect(self):
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
    
    def __init__(self, cr, uid, name, context):
        super(contractor_salary_register, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.basic_total=0.0
        self.basic1_total=0.0
        self.total_ot_amount=0.0
        self.gross_pay_total=0.0
        self.deduction_total=0.0
        self.total_deduction=0.0
        self.amount_paid_total=0.0
        self.pf_total=0.0
        self.esi_total=0.0
        self.tds_total=0.0
        self.sal_advance=0.0
        self.loan_advance=0.0
        
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_data":self.get_data,
                                  "get_basic1_total":self.get_basic1_total,
                                  "get_basic_total":self.get_basic_total,
                                  "get_ot_total":self.get_ot_total,
                                  "get_gross_pay":self.get_gross_pay,
                                  "get_total_deduction":self.get_total_deduction,
                                  "get_pf_total":self.get_pf_total,
                                  "get_esi_total":self.get_esi_total,
                                  "get_tds_total":self.get_tds_total,
                                  "get_amount_paid_total":self.get_amount_paid_total,
                                  "get_father":self.get_father,
                                  "get_sal_advance":self.get_sal_advance,
                                  "get_loan_advance":self.get_loan_advance,
                                   "get_account_no":self.get_account_no
                                  })
        
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
    
    def get_account_no(self,emp_sinid):
        res={}
        conn = self.server_connect()
        cursor = conn.cursor()
        if emp_sinid:
             emp_query = "select account_number from hr_contractorp where sinid='"+str(emp_sinid)+"' "   
             cursor.execute(emp_query)
             result = cursor.fetchall() 
             if   result :
                 res= result[0][0]
             else:
                 res=''    
        return res  
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y")
         return date1
      
    def get_sequence(self):
        self.count=self.count+1
        return self.count
     
    def get_data(self,month,partner,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if partner and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])
        elif partner :
            list_ids = emp_obj.search(self.cr, 1, [('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])
        
        if len(list_ids) == 1 :
            qry =   "select hr.sinid,res.name,hr.id,desg.name,hd.name,hr.esi_number,hr.uan,spl.work_day,spl.week_leave,spl.holiday_leave,sum(spl.sick_leave + spl.casual_leave + spl.compensatory_leave + spl.earned_leave),"\
                    " spl.days,spl.basic,sum(spl.overtime_amount+spl.sun_overtime_amount),spl.total_amount,spl.esi,spl.epf,spl.tds,spl.kharcha,spl.loan, "\
                    " sum(spl.esi+spl.epf+spl.tds+spl.kharcha+spl.loan),rp.street,rp.name,spl.days_amount,spl.grand_total,spl.month_days,spl.total_over_time "\
                    " ,spl.other_salary,spl.other_salary_amount,spl.factory_work from salary_payment_line as spl " \
                    "  left join hr_employee as hr on spl.employee_id=hr.id left join resource_resource as res on (hr.resource_id=res.id) left join  hr_job as desg on (hr.job_id=desg.id) "\
                    "   left join hr_department as hd on (hr.department_id=hd.id) left join res_partner as rp on (hr.partner_id=rp.id) where spl.month='"+str(month.month)+"'"\
                    "  and spl.year_id='"+str(month.year_id.id)+"' and spl.employee_id = '"+str(list_ids[0])+"' "\
                    " group by hr.sinid,res.name,hr.father_name,desg.name,hd.name,hr.esi_number,hr.uan,spl.days,spl.week_leave,spl.holiday_leave,spl.work_day,hr.id ," \
                    " spl.month_days,spl.basic,spl.overtime_amount,spl.esi,spl.epf,spl.tds,spl.month_days,spl.kharcha,spl.loan,rp.street,rp.name,spl.days_amount,spl.grand_total,spl.total_amount,spl.total_over_time,spl.other_salary,spl.other_salary_amount,spl.factory_work order by hr.sinid "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
        else:
            qry =   "select hr.sinid,res.name,hr.id,desg.name,hd.name,hr.esi_number,hr.uan,spl.work_day,spl.week_leave,spl.holiday_leave,sum(spl.sick_leave + spl.casual_leave + spl.compensatory_leave + spl.earned_leave),"\
                    " spl.days,spl.basic,sum(spl.overtime_amount+spl.sun_overtime_amount),spl.total_amount,spl.esi,spl.epf,spl.tds,spl.kharcha,spl.loan, "\
                    " sum(spl.esi+spl.epf+spl.tds+spl.kharcha+spl.loan),rp.street,rp.name,spl.days_amount,spl.grand_total,spl.month_days,spl.total_over_time"\
                    " ,spl.other_salary,spl.other_salary_amount,spl.factory_work from salary_payment_line as spl " \
                    "  left join hr_employee as hr on spl.employee_id=hr.id left join resource_resource as res on (hr.resource_id=res.id) left join  hr_job as desg on (hr.job_id=desg.id) "\
                    "   left join hr_department as hd on (hr.department_id=hd.id) left join res_partner as rp on (hr.partner_id=rp.id) where spl.month='"+str(month.month)+"'"\
                    "  and spl.year_id='"+str(month.year_id.id)+"' and spl.employee_id in "+str(tuple(list_ids))+" "\
                    " group by hr.sinid,res.name,hr.father_name,desg.name,hd.name,hr.esi_number,hr.uan,spl.days,spl.week_leave,spl.holiday_leave,spl.work_day,hr.id ," \
                    " spl.month_days,spl.basic,spl.overtime_amount,spl.esi,spl.epf,spl.tds,spl.month_days,spl.kharcha,spl.loan,rp.street,spl.total_over_time,rp.name,spl.days_amount,spl.grand_total,spl.total_amount,spl.other_salary,spl.other_salary_amount,spl.factory_work order by hr.sinid "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
        if temp :
            for val in  temp :      
                 self.basic_total+=val[12]+val[27] 
                 self.basic1_total+=val[23]+val[28]
                 if val[13]:
                     self.total_ot_amount += val[13]
                 if val[14]:
                     self.gross_pay_total+=val[14]
                 if val[20]:
                     self.total_deduction+=val[20]
                 if val[24]:
                     self.amount_paid_total+=val[24]
                 if val[16]:        
                     self.pf_total+=val[16]
                 if val[15]:    
                     self.esi_total+=val[15]
                 if val[17]:    
                     self.tds_total+=val[17]
                 if val[18]:    
                     self.sal_advance+=val[18]
                 if val[19]:    
                     self.loan_advance+=val[19]  
                                    
            self.get_basic_total()
            self.get_basic1_total()
            self.get_ot_total()
            self.get_gross_pay()
            self.get_total_deduction()
            self.get_amount_paid_total()
            self.get_pf_total()
            self.get_esi_total()
            self.get_tds_total()
            self.get_sal_advance()
            self.get_loan_advance()            
            return temp
    def get_pf_total(self):
        return self.pf_total 
    
    def get_esi_total(self):
        return self.esi_total 
    
    def get_tds_total(self):
        return self.tds_total        
        
    def get_basic_total(self):
        
        return self.basic_total 
    
    def get_ot_total(self):
        
        return self.total_ot_amount
    
    def get_gross_pay(self):
        
        return self.gross_pay_total
    
    def get_total_deduction(self):
        
        return self.total_deduction
    
    def get_amount_paid_total(self):
         
        return self.amount_paid_total 
     
    def get_basic1_total(self):
        
        return self.basic1_total     

    def get_sal_advance(self):
        return self.sal_advance        

    def get_loan_advance(self):
        return self.loan_advance        

class report_contractor_salary_register(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_salary_register'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_salary_register'
    _wrapped_report_class = contractor_salary_register
    
    
 # [[===============================[[ CONTRACTOR SALARY SLIP REPORT  ]]===============================================]]
  
class contractor_salary_slip(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
      
        super(contractor_salary_slip, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_time":self.get_time,
                                  "get_data":self.get_data
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y")
         return date1
  
     
    def get_data(self,month,partner,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if partner and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])
        elif partner :
            list_ids = emp_obj.search(self.cr, 1, [('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])
        
        if len(list_ids) == 1 :
           qry = "select res.name,desg.name,hr.sinid,hd.name,hr.uan,hr.esi_number,spl.work_day,spl.days,spl.week_leave,spl.holiday_leave,sum(spl.casual_leave + spl.sick_leave + spl.compensatory_leave + spl.earned_leave),spl.total_over_time,"\
                    " spl.basic,spl.days_amount,sum(spl.overtime_amount+spl.sun_overtime_amount),sum(spl.days_amount+spl.overtime_amount+spl.sun_overtime_amount+spl.other_salary_amount),spl.esi,spl.epf,spl.loan,spl.kharcha,spl.tds,sum(spl.esi+spl.epf+spl.loan+spl.kharcha+spl.tds),spl.grand_total,rp.name,rp.street,rp.city,rp.zip,spl.other_salary,spl.other_salary_amount,spl.factory_work from salary_payment_line as spl " \
                    "  left join hr_employee as hr on spl.employee_id=hr.id left join resource_resource as res on (hr.resource_id=res.id) left join  hr_job as desg on (hr.job_id=desg.id) "\
                    "   left join hr_department as hd on (hr.department_id=hd.id) left join res_partner as rp on (hr.partner_id=rp.id) "\
                     "  where spl.month='"+str(month.month)+"' and spl.year_id='"+str(month.year_id.id)+"'  and spl.employee_id = '"+str(list_ids[0])+"'  "\
                      " group by res.name,desg.name,hr.sinid,hd.name,hr.uan,hr.esi_number,spl.days,spl.week_leave,spl.casual_leave,spl.holiday_leave,spl.sick_leave,spl.compensatory_leave,spl.earned_leave,rp.name,rp.street,rp.city,rp.zip,"\
                      "spl.basic,spl.days_amount,spl.esi,spl.epf,spl.loan,spl.kharcha,spl.tds,spl.grand_total,spl.work_day,spl.total_over_time,spl.other_salary,spl.other_salary_amount,spl.factory_work order by hr.sinid " 
           self.cr.execute(qry)
           temp = self.cr.fetchall()
           
        else :     
              qry = "select res.name,desg.name,hr.sinid,hd.name,hr.uan,hr.esi_number,spl.work_day,spl.days,spl.week_leave,spl.holiday_leave,sum(spl.casual_leave + spl.sick_leave + spl.compensatory_leave + spl.earned_leave),spl.total_over_time,"\
                    " spl.basic,spl.days_amount,sum(spl.overtime_amount+spl.sun_overtime_amount),sum(spl.days_amount+spl.overtime_amount+spl.sun_overtime_amount+spl.other_salary_amount),spl.esi,spl.epf,spl.loan,spl.kharcha,spl.tds,sum(spl.esi+spl.epf+spl.loan+spl.kharcha+spl.tds),spl.grand_total,rp.name,rp.street,rp.city,rp.zip,spl.other_salary,spl.other_salary_amount,spl.factory_work from salary_payment_line as spl " \
                    "  left join hr_employee as hr on spl.employee_id=hr.id left join resource_resource as res on (hr.resource_id=res.id) left join  hr_job as desg on (hr.job_id=desg.id) "\
                    "   left join hr_department as hd on (hr.department_id=hd.id) left join res_partner as rp on (hr.partner_id=rp.id) "\
                    "  where spl.month='"+str(month.month)+"' and spl.year_id='"+str(month.year_id.id)+"'  and spl.employee_id in "+str(tuple(list_ids))+"  "\
                    " group by res.name,desg.name,hr.sinid,hd.name,hr.uan,hr.esi_number,spl.days,spl.week_leave,spl.casual_leave,spl.holiday_leave,spl.sick_leave,spl.compensatory_leave,spl.earned_leave,rp.name,rp.street,rp.city,rp.zip,"\
                    "spl.basic,spl.days_amount,spl.esi,spl.epf,spl.loan,spl.kharcha,spl.tds,spl.grand_total,spl.work_day,spl.total_over_time,spl.other_salary,spl.other_salary_amount,spl.factory_work order by hr.sinid " 
              self.cr.execute(qry)
              temp = self.cr.fetchall()
                            
        return temp
   
class report_contractor_salary_slip(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_salary_slip'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_salary_slip'
    _wrapped_report_class = contractor_salary_slip
      
  
  # [[===============================[[ CONTRACTOR ESI CONTRIBUTION REPORT  ]]===============================================]]
   
class contractor_esi_contribution(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_esi_contribution, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.esi=0.0
        self.gross=0.0
        self.emp_cont=0.0
        self.total_cont=0.0
        
        
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_time":self.get_time,
                                  "get_data":self.get_data ,
                                  "get_gross":self.get_gross,
                                  "get_esi":self.get_esi,   
                                  "get_emplopyer_cont":self.get_emplopyer_cont ,
                                  "get_total_cont":self.get_total_cont          
                                  })
    
    def get_time(self):
         date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
         date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
         date1 = date1 + timedelta(hours=5,minutes=30)
         date1 = date1.strftime("%d-%m-%Y")
         return date1
      
    def get_sequence(self):
        self.count=self.count+1
        return self.count  
      
    def get_data(self,month,partner,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if partner and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor'),('esi_tick','=',True)])
        elif partner :
            list_ids = emp_obj.search(self.cr, 1, [('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor'),('esi_tick','=',True)])

        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,hr.esi_number,spl.employee_name,hd.name,spl.total_amount,spl.esi,spl.days from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.esi <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,hr.esi_number,spl.employee_name,hd.name,spl.total_amount,spl.esi,spl.days from salary_payment_line as spl  "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.esi <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 

        for val in temp :
            if val[4]:
                self.gross = self.gross + val[4]
            if val[5]:
                self.esi=self.esi+val[5] 
        return temp
    
    
    def get_gross(self) :
        return self.gross
    
    def get_esi(self) :
        return self.esi
    
    def get_emplopyer_cont(self):
        self.emp_cont= (math.ceil((4.75*self.gross)/100 )) 
        return self.emp_cont
    
    def get_total_cont(self):
        self.total_cont=self.emp_cont+self.esi
        return  self.total_cont
         
    
class report_contractor_esi_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_esi_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_esi_contribution'
    _wrapped_report_class = contractor_esi_contribution
    
    
 # [[===============================[[ CONTRACTOR PF CONTRIBUTION REPORT  ]]===============================================]]    
    
class contractor_pf_contribution(report_sxw.rml_parse):
    
    seq = 0
    epf_wages = 0
    epf = 0
    eps = 0
    diff = 0
    def __init__(self, cr, uid, name, context):
        super(contractor_pf_contribution, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  "get_epf_wages":self.get_epf_wages,
                                  "get_epf":self.get_epf,
                                  "get_eps":self.get_eps,
                                  "get_diff":self.get_diff,
                                  })
        
    def get_sequence(self):
        self.seq = self.seq + 1
        return self.seq
        
        
    def get_data(self,month,partner,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if partner and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])
        elif partner :
            list_ids = emp_obj.search(self.cr, 1, [('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])

        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,hr.pf_number,spl.employee_name,spl.gross,spl.epf,spl.epf1,spl.epf2 from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.epf <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,hr.pf_number,spl.employee_name,spl.gross,spl.epf,spl.epf1,spl.epf2 from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.epf <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 

        for val in temp :
            if val[3]:
                self.epf_wages = self.epf_wages + val[3]
            if val[4]:    
                self.epf = self.epf + val[4]
            if val[5]:    
                self.eps = self.eps + val[5]
            if val[6]:    
                self.diff = self.diff + val[6]
        return temp
    
    def get_epf_wages(self) :
        return round(self.epf_wages,0)
    
    def get_epf(self) :
        return round(self.epf,0)

    def get_eps(self) :
        return round(self.eps,0)

    def get_diff(self) :
        return round(self.diff,0)
    
    
class report_contractor_pf_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_pf_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_pf_contribution'
    _wrapped_report_class = contractor_pf_contribution
    
    
# [[===============================[[  CONTRACTOR  TDS CONTRIBUTION REPORT  ]]===============================================]]     

class contractor_tds_contribution(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(contractor_tds_contribution, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.tds=0.0
        self.localcontext.update({
                                  "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  "get_tds":self.get_tds
                    
                                  })   
        
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_data(self,month,partner,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if partner and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])
        elif partner :
            list_ids = emp_obj.search(self.cr, 1, [('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])

        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,desg.name,spl.tds from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id)  left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.tds <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,desg.name,spl.tds from salary_payment_line as spl  "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"'and spl.tds <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 
        
        for val in temp :
            if val[4]:
                  self.tds = self.tds + val[4]
        return temp 
    
    def get_tds(self):   
        return self.tds         
                      
        
class report_contractor_tds_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_tds_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_tds_contribution'
    _wrapped_report_class = contractor_tds_contribution
            
  
  # [[===============================[[ --> CONTRACTOR  LOAN CONTRIBUTION REPORT <-- ]]===============================================]]  
  
class contractor_loan_contribution(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(contractor_loan_contribution, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.curr_loan=0.0
        self.loan_emi=0.0
        self.localcontext.update({
                                 "get_sequence":self.get_sequence,
                                  "get_data":self.get_data,
                                  "get_curr_loan":self.get_curr_loan,
                                  "get_loan_emi":self.get_loan_emi
                    
                                  })   
        
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_data(self,month,partner,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if partner and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])
        elif partner :
            list_ids = emp_obj.search(self.cr, 1, [('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])

        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,desg.name,spl.current_loan,spl.loan from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id)  left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.loan <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,desg.name,spl.current_loan,spl.loan  from salary_payment_line as spl  "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.loan <>0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 

        for val in temp :
            if val[4]:
                  self.curr_loan = self.curr_loan + val[4]
            if val[5]: 
                 self.loan_emi =  self.loan_emi + val[5]           
        return temp
    
    def get_curr_loan(self):   
        return  self.curr_loan   
          
    def get_loan_emi(self):   
        return self.loan_emi        
        
class report_contractor_loan_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_loan_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_loan_contribution'
    _wrapped_report_class = contractor_loan_contribution    
    
    
    
# [[ ===========================================[[ CONTRACTOR ADVANCE REPORT ]]========================================== ]]     
        
class contractor_advance_contribution(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(contractor_advance_contribution, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.kharcha=0.0
        self.localcontext.update({
                                 "get_sequence":self.get_sequence,
                                 "get_data":self.get_data,
                                 "get_kharcha":self.get_kharcha
                                  })   
        
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    
    def get_data(self,month,partner,employee):
        list_ids = []
        temp = []
        emp_obj = self.pool.get('hr.employee')
        if partner and employee:
            list_ids = emp_obj.search(self.cr, 1, [('id', '=', employee.id),('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])
        elif partner :
            list_ids = emp_obj.search(self.cr, 1, [('partner_id', '=', partner.id),('active','=',True),('type','=','Contractor')])

        if len(list_ids) == 1 :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,spl.kharcha,desg.name from salary_payment_line as spl "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id)  left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id = '"+str(list_ids[0])+"' and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.kharcha <> 0.00 order by spl.sinid ")
            temp = self.cr.fetchall()

        else :
            query = self.cr.execute("select spl.sinid,spl.employee_name,hd.name,spl.kharcha,desg.name from salary_payment_line as spl  "
                                    "left join hr_employee as hr on (spl.employee_id=hr.id) left join  hr_job as desg on (hr.job_id=desg.id) left join hr_department as hd on (hr.department_id=hd.id) where spl.employee_id in "+str(tuple(list_ids))+" and spl.month='"+str(month.month)+"' " 
                                    "and spl.year_id='"+str(month.year_id.id)+"' and spl.kharcha <>0.00 order by spl.sinid ")
            temp = self.cr.fetchall() 
        
        for val in temp :
            if val[3]:
                  self.kharcha = self.kharcha + val[3]
        return temp 
    
    def get_kharcha(self):   
        return self.kharcha    
        
class report_contractor_advance_contribution(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_advance_contribution'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_advance_contribution'
    _wrapped_report_class = contractor_advance_contribution                   
       
