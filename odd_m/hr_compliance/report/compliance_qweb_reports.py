import time
import math
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from openerp.tools.translate import _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp  import api ,models
from dateutil import rrule
import calendar
from datetime import date
import re
from openerp.tools.amount_to_text import amount_to_text
from openerp.tools import amount_to_text_en
from openerp.tools import amount_to_text
from openerp.tools import num2word

class employee_service_record(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_service_record, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_birthday_record":self.get_birthday_record,
                                  "get_detail_record":self.get_detail_record,
                                  "get_increment_record":self.get_increment_record,
                                  "get_promotion_record":self.get_promotion_record,
                                  })
        
    def get_birthday_record(self,emp_id):
        res={}
        date1=''
        if emp_id:
            if emp_id.birthday: 
               date1 = datetime.strptime(emp_id.birthday,"%Y-%m-%d")
               date1 = date1.strftime("%d-%m-%Y")
        return date1       

    def get_detail_record(self,emp_id):
        res={}
        l=[]
        tup=()
        date1=''
        date2=''
        date3=''
        join_salary=''
        if emp_id:
            if emp_id.doa:
               date1 = datetime.strptime(emp_id.doa,"%Y-%m-%d")
               date1 = date1.strftime("%d-%m-%Y")
            if emp_id.doc :
               date2 = datetime.strptime(emp_id.doc,"%Y-%m-%d")
               date2 = date2.strftime("%d-%m-%Y")
            if emp_id.doj:
               date3 = datetime.strptime(emp_id.doj,"%Y-%m-%d")
               date3 = date3.strftime("%d-%m-%Y")
            if emp_id.joining_salary:
                  join_salary =emp_id.joining_salary
                  
            tup=(date1,date2,date3,join_salary) 
            l.append(tup)      

        return l
    
    def get_increment_record(self,emp_id):
        res={}
        increment_detail=[]
        if emp_id:
            if emp_id.increment_id:
                query="select inc_date,amount from increment where employee_id='"+str(emp_id.id)+"' order by  inc_date "
                self.cr.execute(query)
                temp = self.cr.fetchall()
                if temp:
                    for val in temp:
                        inc_date = datetime.strptime(val[0],"%Y-%m-%d")
                        inc_date = inc_date.strftime("%d-%m-%Y")
                        amount=val[1]
                        tup=(inc_date,amount)
                        increment_detail.append(tup)
            return increment_detail

    def get_promotion_record(self,emp_id):
        res={}
        promotion_detail=[]
        if emp_id:
            if emp_id.promotion_id:
                query="select pro_date,desgn_id from promotion where employee_id='"+str(emp_id.id)+"'  order by pro_date"
                self.cr.execute(query)
                temp = self.cr.fetchall()
                if temp:
                    for val in temp:
                        pro_date = datetime.strptime(val[0],"%Y-%m-%d")
                        pro_date = pro_date.strftime("%d-%m-%Y")
                        desig_browse=self.pool.get('hr.job').browse(self.cr,1,val[1]).name
                        tup1=(pro_date,desig_browse)
                        promotion_detail.append(tup1)
            return promotion_detail    
    
class report_employee_service_record(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_service_record'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_service_record'
    _wrapped_report_class = employee_service_record


class employee_bond(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_bond, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  })
        
    
class report_employee_bond(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_bond'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_bond'
    _wrapped_report_class = employee_bond
    
    
class affedavit(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(affedavit, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_father":self.get_father,
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
        
    
class report_affedavit(osv.AbstractModel):
    _name = 'report.hr_compliance.report_affedavit'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_affedavit'
    _wrapped_report_class = affedavit  


class employee_induction(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_induction, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  })
        
    
class report_employee_induction(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_induction'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_induction'
    _wrapped_report_class = employee_induction
    
    
    

class employee_medical(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_medical, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_father":self.get_father,
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
        
    
class report_employee_medical(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_medical'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_medical'
    _wrapped_report_class = employee_medical
    
    
class confirmation_letter(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(confirmation_letter, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                 "get_time":self.get_time,
                                 "get_father":self.get_father
                                  })
    
    def get_time(self,doj):
         if doj :
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             new_date = (date1 + relativedelta(months=+6)).strftime('%d-%m-%Y')
             return new_date
         
    def get_father(self,emp_id):
        res={}
        qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
        self.cr.execute(qry)
        temp = self.cr.fetchall()
        if temp:
            res = temp[0][0]
        else:
            res = ' '    
        return res          
    
class report_confirmation_letter(osv.AbstractModel):
    _name = 'report.hr_compliance.report_confirmation_letter'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_confirmation_letter'
    _wrapped_report_class = confirmation_letter
    
    
class appointment_letter(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(appointment_letter, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                "get_time":self.get_time,
                                "get_father":self.get_father,
                                "get_time1":self.get_time1,
                                  })  
    def get_time(self,doa):
        if doa: 
             date1 = datetime.strptime(doa,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1
#     
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
        
    def get_time1(self,doj):
        if doj: 
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1
     
    
class report_appointment_letter(osv.AbstractModel):
    _name = 'report.hr_compliance.report_appointment_letter'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_appointment_letter'
    _wrapped_report_class = appointment_letter
    
    
    
class employee_form11(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_form11, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_father":self.get_father,
                                   "get_time":self.get_time,
                                   "get_passport":self.get_passport,
                                   "get_aadhaar_no":self.get_aadhaar_no,
                                   "get_pan_no":self.get_pan_no,
                                   "get_bank_acc_no":self.get_bank_acc_no
                                  })
        
    def get_bank_acc_no(self,verf_id,emp_id):
        res=''
        for val in verf_id:
            if val.proof_id=='Bank_ Account_ No':
                qry="select id_no,ifsc_code from verification where proof_id='Bank_ Account_ No' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    if temp[0][0] and temp[0][1] :
                        qry_ifsc="select bic from res_bank where id='"+str(temp[0][1])+"'  "
                        self.cr.execute(qry_ifsc)
                        temp_ifsc = self.cr.fetchall()
                        if temp_ifsc :
                            res = str(temp[0][0])+' '+'&'+' '+str(temp_ifsc[0][0])
                else:
                    res = ' '         
        return res     

    def get_aadhaar_no(self,verf_id,emp_id):
        res=''
        for val in verf_id:
            if val.proof_id=='Aadhar_Card':
                qry="select id_no from verification where proof_id='Aadhar_Card' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' '         
        return res 
    
    def get_pan_no(self,verf_id,emp_id):
        res=''
        for val in verf_id:
            if val.proof_id=='PAN_Card':
                qry="select id_no from verification where proof_id='PAN_Card' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' '         
        return res     
        
        
    def get_passport(self,verf_id,emp_id):
        res=''
        for val in verf_id:
            if val.proof_id=='Passport':
                qry="select id_no from verification where proof_id='Passport' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' '         
        return res 
    

    def get_time(self,doj):
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1        
        
    def get_father(self,emp_id,fam_id):
        res=''
        for val in fam_id: 
            if val.relation=='Husband' :    
                qry = "select name from family where relation='Husband' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' ' 
            else:
                qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' ' 
                           
        return res       
        
    
class report_employee_form11(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_form11'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_form11'
    _wrapped_report_class = employee_form11
    
    
class pf_nomination_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(pf_nomination_form, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_data1":self.get_data1,
                                  "get_data2":self.get_data2,
                                  "get_data3":self.get_data3,
                                  "get_data4":self.get_data4,
                                  "get_data5":self.get_data5,
                                  "get_data6":self.get_data6,
                                  })
        
    def get_data1(self,employee):
        l = []
        tup = ()
        rel_name = ''
        gender=''
        status = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        name = emp_browse.name
        sinid = emp_browse.sinid
        dob = emp_browse.birthday or ''
        dob = datetime.strptime(dob,"%Y-%m-%d")
        dob = dob.strftime("%d-%m-%Y")
        if emp_browse.gender:
            gender = emp_browse.gender.upper()
        if emp_browse.marital:
            status = emp_browse.marital.upper()
        pf_no = emp_browse.pf_number or ''
                
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.relation == 'Father' :
                    rel_name = val.name
                if val.relation == 'Husband' and rel_name == '' :
                    rel_name = val.name
        tup = (name, sinid, rel_name, dob, gender, status, pf_no)
        l.append(tup)
        return l
    
    def get_data2(self,employee):
        l = []
        tup = ()
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        address1 = emp_browse.permanent_add or ''
        address2 = emp_browse.local_add or ''
        tup = (address1, address2)
        l.append(tup)
        return l
    
    def get_data3(self,employee):
        l = []
        tup = ()
        nom_name = ''
        nom_rel = ''
        nom_age  = ''
        nom_share = ''
        nom_val = '---'
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        address = emp_browse.permanent_add or ''
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.nom_tick == True :
                    nom_name = val.name.upper()
                    nom_rel = val.relation.upper()
                    nom_age = str(val.age) + 'YRS'
                    nom_share = str(val.share) + '%'
                    break
        tup = (nom_name, address, nom_rel, nom_age, nom_share, nom_val)
        l.append(tup)
        return l
    
    def get_data4(self,employee):
        l = []
        tup = ()
        f_no = 0
        f_name = ''
        f_age  = ''
        f_rel = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        address = emp_browse.permanent_add or ''
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.reside == True:
                    f_no += 1
                    f_name = val.name.upper()
                    f_age = str(val.age) + 'YRS'
                    f_rel = val.relation.upper()
                    if f_no == 1 and len(emp_browse.family_id) == 1 :
                        address1 = address
                    elif f_no == 1 and len(emp_browse.family_id) > 1 :
                        address1 = address[0:40]
                    elif f_no == 2 :
                        address1 = address[40:80]
                    else :
                        address1 = ''
                    tup = (f_no, f_name, address1, f_age, f_rel)
                    l.append(tup)
        else : 
            tup = (f_no,f_name,address,f_age,f_rel)
            l.append(tup)
        for val1 in l :
            if len(l) != 15 :
                tup = ('','','','','')
                l.append(tup)            
        return l
    
    def get_data5(self,employee):
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        doj = emp_browse.doj or ''
        doj = datetime.strptime(doj,"%Y-%m-%d")
        doj = doj.strftime("%d-%m-%Y")
        return doj
    
    def get_data6(self,employee):
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        com_address = emp_browse.company_id.name or ''
        street1 = emp_browse.company_id.street or ''
        street2 = emp_browse.company_id.street2 or ''
        city = emp_browse.company_id.city or ''
        state = emp_browse.company_id.state_id.name or ''
        zip = emp_browse.company_id.zip or ''
        country = emp_browse.country_id.name or ''
        
        com_address = com_address + ',' + ' ' + street1 + ' ' +  street2 + ' ' +  city + ' ' +  state + ' ' +  zip + ' ' +  country
        return com_address
    
    
class report_pf_nomination_form(osv.AbstractModel):
    _name = 'report.hr_compliance.report_pf_nomination_form'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_pf_nomination_form_temp_id'
    _wrapped_report_class = pf_nomination_form
    
    
 
    
    
    
######### ===================================[[ Employee Transfer ]] ============================================##########   
    
     
class employee_transfer_letter(report_sxw.rml_parse):
     
    def __init__(self, cr, uid, name, context):
        super(employee_transfer_letter, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_data":self.get_data,
                                  "get_company_check":self.get_company_check,
                                  "get_company":self.get_company,
                                  })
        
    def get_data(self,employee):
        transfer_date = ''
        query = self.cr.execute("select transfer_date from company_transfer_history where employee_id='"+str(employee.id)+"' order by transfer_date desc limit 1 ")
        temp =  self.cr.fetchall()
        if temp :
            transfer_date = temp[0][0]
            transfer_date = datetime.strptime(transfer_date,"%Y-%m-%d")
            transfer_date = transfer_date.strftime("%d-%m-%Y")
        return transfer_date        

    def get_company_check(self,employee):
        company_name = employee.company_id.name
        
        match1 = re.match( r'Designco', company_name)
        match2 = re.match( r'Lohia', company_name)
        if match1:
            company = 'Designco'
        elif match2:
            company = 'Lohia'
        else :
            company = company_name
        return company        

    def get_company(self,employee):
        old_company = ''
        new_company = ''
        company_lst = []
        query = self.cr.execute("select old_company_id,new_company_id from company_transfer_history where employee_id='"+str(employee.id)+"' order by transfer_date desc limit 1 ")
        temp =  self.cr.fetchall()
        if temp :
            old_company = self.pool.get('res.company').browse(self.cr, 1, temp[0][0]).name
            new_company = self.pool.get('res.company').browse(self.cr, 1, temp[0][1]).name
        company_lst.append(old_company)
        company_lst.append(new_company)
        return company_lst        

class report_employee_transfer_letter(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_transfer_letter'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_transfer_letter'
    _wrapped_report_class = employee_transfer_letter   
    
     
# ######### ===================================[[ Employee  Promotion  Report ]] ====================================##########       
    
#     
class employee_promotion(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(employee_promotion, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_data":self.get_data,
                                  "get_data1":self.get_data1,
                                  })
    
    def get_data(self,employee):
        l = []
        promotion_date = ''
        old_designation = ''
        curr_designation = ''
        query = self.cr.execute("select previous_designtation,current_designation from hr_active_history where employee_id='"+str(employee.id)+"' and previous_designtation != 'X' and current_designation !='X' order by date desc limit 1 ")
        temp =  self.cr.fetchall()
        query1 = self.cr.execute("select pro_date from promotion where employee_id='"+str(employee.id)+"' order by create_date desc limit 1 ")
        temp1 =  self.cr.fetchall()
        if temp :
            promotion_date = temp1[0][0]
            promotion_date = datetime.strptime(promotion_date,"%Y-%m-%d")
            promotion_date = promotion_date.strftime("%d-%m-%Y")
            old_designation = temp[0][0]
            curr_designation = temp[0][1]
        l.append((promotion_date,old_designation,curr_designation))
        return l        

    def get_data1(self,employee):
        father_name = ''
        query = self.cr.execute("select name from family where employee_id='"+str(employee.id)+"' and relation = 'Father' ")
        temp =  self.cr.fetchall()
        if temp :
            father_name = temp[0][0]
        return father_name        

     
class report_employee_promotion(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_promotion'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_promotion'
    _wrapped_report_class = employee_promotion     
      
             
             
 ## =========================================Employee FnF Details==========================================    
    
class employee_details(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_details, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_bonus_details":self.get_bonus_details,
                                  "get_bonus_lines":self.get_bonus_lines,
                                  "get_sequence":self.get_sequence,
                                  "get_work_total":self.get_work_total,
                                  "get_casual_total":self.get_casual_total,
                                  "get_earned_total":self.get_earned_total,
                                  "get_pre_total_salary":self.get_pre_total_salary,
                                  "get_pre_total_bonus":self.get_pre_total_bonus,
                                  "get_curr_total_salary":self.get_curr_total_salary,
                                  "get_curr_total_bonus":self.get_curr_total_bonus,
                                  "get_leave_details":self.get_leave_details,
                                  "get_month_pay_details":self.get_month_pay_details,
#                                   "get_total_pay_details":self.get_total_pay_details
#                                   "get_final_details":self.get_final_details
                                  })
        
  

    def get_bonus_details(self,last_year,current_year,employee,month,bal_leave):
        leave_enca=bal_leave
        loan_advance=0
        list_ids = []
        l=[]
        tup=()
        curr_salary=0.0
        curr_bonus=0
        pre_salary=0.0
        pre_bonus=0
        total_salary=0.0
        total_bonus=0.0
        basic=0.0
        paid_salary=0.0
        pay_total=0.0
        TOTAL_PAY=0.0
        leave_pay=0.0
        paid_total=0.0
        loan=0.0
        advance=0.0
        gratuity=0.0
        less_total=0.0
        emp_obj = self.pool.get('hr.employee')
        list_ids = emp_obj.search(self.cr, 1, [('id', '=',employee.id),('active','=',True)])  
        if len(list_ids) == 0 :   
                 raise osv.except_osv(('Warning !'),("Record Not Found !!!")) 
        if len(list_ids) == 1 :
             query ="select balance from loan_deduction where emp_id = '"+str(list_ids[0])+"' and state='done' "                       
             self.cr.execute(query)
             temp_loan = self.cr.fetchall()
        else:    
             query ="select balance from loan_deduction where emp_id = '"+str(list_ids[0])+"' and state='done' "                       
             self.cr.execute(query)
             temp_loan = self.cr.fetchall()   
        if temp_loan:
            loan=temp_loan[0][0]
        
        if current_year != last_year:
            if current_year :
                from_year=current_year[0:4]
                from_date=from_year+'-'+'04'+'-'+'01'
                from_date=datetime.strptime(from_date, "%Y-%m-%d")
                till_year=current_year[5:10]
                till_date=till_year+'-'+'03'+'-'+'31'
                till_date=datetime.strptime(till_date, "%Y-%m-%d")
                if len(list_ids) == 1 :
                    query="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(list_ids[0])+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query)
                    temp = self.cr.fetchall()              
                else:
                    query="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(tuple(list_ids))+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query)
                    temp = self.cr.fetchall()
                if temp and temp[0][0]!=None and temp[0][1]!=None :
                    curr_salary=temp[0][0]
                    curr_bonus=temp[0][1]
                else:
                    curr_salary=0.0
                    curr_bonus=0.0
                    
            if last_year :
                from_year=last_year[0:4]
                from_date=from_year+'-'+'04'+'-'+'01'
                from_date=datetime.strptime(from_date, "%Y-%m-%d")
                till_year=last_year[5:10]
                till_date=till_year+'-'+'03'+'-'+'31'
                till_date=datetime.strptime(till_date, "%Y-%m-%d")
                if len(list_ids) == 1 :
                    query1="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(list_ids[0])+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query1)
                    temp1 = self.cr.fetchall() 
                    
                else:
                    query1="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(tuple(list_ids))+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query1)
                    temp1 = self.cr.fetchall()
                if temp1 and temp1[0][0]!=None and temp1[0][1]!=None :
                    pre_salary=temp1[0][0]
                    pre_bonus=temp1[0][1]
                else:
                    pre_salary=0.0
                    pre_bonus=0.0
                    
        elif current_year == last_year:
            if current_year :
                from_year=current_year[0:4]
                from_date=from_year+'-'+'04'+'-'+'01'
                from_date=datetime.strptime(from_date, "%Y-%m-%d")
                till_year=current_year[5:10]
                till_date=till_year+'-'+'03'+'-'+'31'
                till_date=datetime.strptime(till_date, "%Y-%m-%d")
                if len(list_ids) == 1 :
                    query="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(list_ids[0])+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query)
                    temp = self.cr.fetchall()              
                else:
                    query="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(tuple(list_ids))+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query)
                    temp = self.cr.fetchall()
                if temp and temp[0][0]!=None and temp[0][1]!=None :
                    curr_salary=temp[0][0]
                    curr_bonus=temp[0][1]
                    pre_salary=0.0
                    pre_bonus=0.0
                    
                else:
                    curr_salary=0.0
                    curr_bonus=0.0
                    pre_salary=0.0
                    pre_bonus=0.0
                    
                
        if curr_salary and pre_salary :            
            total_salary=curr_salary+pre_salary
            total_bonus=curr_bonus +pre_bonus 
        elif curr_salary :
            total_salary=curr_salary 
            total_bonus=curr_bonus  
        elif pre_salary :
            total_salary=pre_salary 
            total_bonus=pre_bonus     
        else:
            total_salary=0.0
            total_bonus=0.0

        if month:
            if len(list_ids) == 1 :
                 query ="select basic,grand_total,kharcha from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(month.month)+"' and year_id='"+str(month.year_id.id)+"' group by basic,grand_total,kharcha "                       
                 self.cr.execute(query)
                 temp = self.cr.fetchall()
                 query_hr ="select total_salary from hr_employee where id = '"+str(list_ids[0])+"'  group by total_salary"                       
                 self.cr.execute(query_hr)
                 temp_hr = self.cr.fetchall()
                 if temp_hr and temp_hr[0][0] != None:
                     basic=temp_hr[0][0]
                 query_hr1 ="select current_salary from hr_employee where id = '"+str(list_ids[0])+"'  group by current_salary"                       
                 self.cr.execute(query_hr1)
                 temp_hr1 = self.cr.fetchall()
                 if temp_hr1 and temp_hr1[0][0] != None:
                     basic1=temp_hr1[0][0]
                
            else:
                 query ="select basic,grand_total,kharcha from salary_payment_line where employee_id = '"+str(tuple(list_ids))+"' and month='"+str(month.month)+"' and year_id='"+str(month.year_id.id)+"' group by basic,grand_total,kharcha  "                       
                 self.cr.execute(query)
                 temp = self.cr.fetchall() 
                 query_hr ="select total_salary from hr_employee where id = '"+str(tuple(list_ids))+"'  group by total_salary"                       
                 self.cr.execute(query_hr)
                 temp_hr = self.cr.fetchall()
                 if temp_hr and temp_hr[0][0] != None:
                     basic=temp_hr[0][0]
                 query_hr1 ="select current_salary from hr_employee where id = '"+str(tuple(list_ids))+"'  group by current_salary"                       
                 self.cr.execute(query_hr1)
                 temp_hr1 = self.cr.fetchall()
                 if temp_hr1 and temp_hr1[0][0] != None:
                     basic1=temp_hr1[0][0]
                 
            if temp:
#                 basic=temp[0][0]
                 paid_salary=temp[0][1]
                 advance=temp[0][2]
           
        if len(list_ids) == 1 :
            emp_browse =emp_obj.browse(self.cr,1,employee.id)
            doj=emp_browse.doj
            doj = datetime.strptime(doj, "%Y-%m-%d")
            doj=doj.date()
            today_date = date.today()
            days = (today_date - doj).days
            months=days/30
            years=months/12
            months1 = months - (years*12)
            if years >=5 and months1 < 6:
                gratuity=(15*years*basic1)/26
                gratuity=round(gratuity,0)
            elif years >=5 and months1 >= 6:
                years=years+1 
                gratuity=(15*years*basic1)/26 
                gratuity=round(gratuity,0)
            else:
                gratuity=0.0      
                
        leave_pay=(basic / 26 )*(leave_enca) 
        leave_pay=round(leave_pay,0)
        bonus=curr_bonus+pre_bonus
        paid_total=(paid_salary+leave_pay+gratuity+bonus) 
        less_total=loan              
        TOTAL_PAY=paid_total-less_total  
        tup=(curr_salary,curr_bonus,pre_salary,pre_bonus,total_salary,total_bonus,paid_salary,leave_enca,leave_pay,paid_total,loan,advance,gratuity,less_total,TOTAL_PAY)
        l.append(tup)     
        return l   
    
    def get_month_pay_details(self,emp,month):
        tup6=()
        l6=[]
        emp_obj = self.pool.get('hr.employee')
        list_ids = emp_obj.search(self.cr, 1, [('id', '=',emp.id),('active','=',True)])
        if len(list_ids) == 0 :   
                 raise osv.except_osv(('Warning !'),("Record Not Found !!!")) 
        if month :
            if len(list_ids) == 1 : 
                query ="select days,sum(days_amount+other_salary_amount),epf,kharcha,tds,esi,total_over_time,sum(overtime_amount+sun_overtime_amount),grand_total,vpf from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(month.month)+"' and year_id='"+str(month.year_id.id)+"' "\
                       " group by days,epf,kharcha,tds,esi,total_over_time,grand_total,vpf  "                         
                self.cr.execute(query)
                temp_line = self.cr.fetchall()
            else:
                query ="select days,sum(days_amount+other_salary_amount),epf,kharcha,tds,esi,total_over_time,sum(overtime_amount+sun_overtime_amount),grand_total,vpf from salary_payment_line where employee_id = '"+str(tuple(list_ids))+"' and month='"+str(month.month)+"' and year_id='"+str(month.year_id.id)+"' "\
                       " group by days,epf,kharcha,tds,esi,total_over_time,grand_total,vpf  "                         
                self.cr.execute(query)
                temp_line = self.cr.fetchall()
            if temp_line:
                    tup6=(temp_line[0][0],temp_line[0][1],temp_line[0][2],temp_line[0][3],temp_line[0][4],temp_line[0][5],temp_line[0][6],temp_line[0][7],temp_line[0][8],temp_line[0][9]) 
                    l6.append(tup6)            
                    return l6
            else:
                 tup6=(0,0,0,0,0,0,0,0,0,0) 
                 l6.append(tup6)
                 return l6
            

  
    def get_bonus_lines(self,last_year,current_year,month,employee):
        self.work_total=0
        self.pre_total_salary=0.0
        self.curr_total_salary=0.0
        self.curr_total_bonus=0.0
        self.pre_total_bonus=0.0
        self.casual_total=0
        self.earned_total=0
        d=0
        l5=[]
        l=[]
        count=0
        l1=[]
        l2=[]
        l3=[]
        l5=[]
        l11=[]
        l4=[]
        l6=[]
        tup7=()
        c=0
        month_list=[]
        month_list1=[]
        list_ids = []   
        tup=()
        tup1=()
        tup2=()
        tup3=()
        tup4=()
        tup6=()
        curr_salary=''
        curr_bonus=''
        pre_salary=''
        pre_bonus=''
        emp_obj = self.pool.get('hr.employee')
        list_ids = emp_obj.search(self.cr, 1, [('id', '=',employee.id),('active','=',True)])
        if len(list_ids) == 0 :   
                 raise osv.except_osv(('Warning !'),("Record Not Found !!!"))  
        
        if current_year !=  last_year:     
            if current_year :
                from_year=current_year[0:4]
                from_year = int(from_year) 
                
                for month1 in range(4,13):
                    month_tup = calendar.monthrange(from_year,month1)
                    if len(str(month1))==1:
                        month1_str='0'+str(month1)
                    else :
                        month1_str=str(month1)    
                    from_date1= str(from_year)+'-'+month1_str+'-'+'01'
                    till_date1=str(from_year) + '-' + month1_str + '-' + str(month_tup[1])
                    month_list.append((from_date1,till_date1))
                for month2 in range(1,4):
                    from_year1 = int(from_year)+1
                    month_tup = calendar.monthrange(from_year1,month2)
                    if len(str(month2))==1:
                        month2_str='0'+str(month2)
                    from_date2= str(from_year1)+'-'+month2_str+'-'+'01'
                    till_date2=str(from_year1) + '-' + month2_str + '-' + str(month_tup[1])
                    month_list.append((from_date2,till_date2))
                
     
                for from_date,till_date in month_list : 
                    if len(list_ids) == 1 :      
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(list_ids[0])+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall() 
                        if temp :
                            l.append(temp[0])
                            self.curr_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.curr_total_bonus+=temp[0][12]
                        else :
                            l.append((0,0,0,0,0,0,0,0,0,0,0,0))
                    else:
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(tuple(list_ids))+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()   
                        if temp :
                            l.append(temp[0])
                            self.curr_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.curr_total_bonus+=temp[0][12]
                        else :
                            l.append((0,0,0,0,0,0,0,0,0,0,0,0))
                if l:
                    for val in l: 
                        if val[0] > 0.0 and val[12]>0.0:
                            curr_salary= val[0]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[1] > 0.0 and val[12]>0.0:
                            curr_salary= val[1]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup) 
                             
                        elif val[2] > 0.0 and val[12]>0.0:
                            curr_salary= val[2]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                              
                        elif val[3] > 0.0 and val[12]>0.0:
                            curr_salary= val[3]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)        
     
                        elif val[4] > 0.0 and val[12]>0.0:
                            curr_salary= val[4]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[5] > 0.0 and val[12]>0.0:
                            curr_salary= val[5]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[6] > 0.0 and val[12]>0.0:
                            curr_salary= val[6]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[7] > 0.0 and val[12]>0.0:
                            curr_salary= val[7]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[8] > 0.0 and val[12]>0.0:
                            curr_salary= val[8]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)        
     
                        elif val[9] > 0.0 and val[12]>0.0:
                            curr_salary= val[9]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[10] > 0.0 and val[12]>0.0:
                            curr_salary= val[10]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[11] > 0.0 and val[12]>0.0:
                            curr_salary= val[11]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                        else :
                            curr_salary= 0.0
                            curr_salary=0.0 
                            tup=(curr_salary,curr_salary)
                            l1.append(tup) 
                            
                query ="select id from holiday_year where name='"+str(month.year_id.name)+"' "        
                self.cr.execute(query)
                temp_year = self.cr.fetchall() 
                if temp_year:           
                    for number in range(1,13) : 
                        if len(list_ids) == 1 : 
                            query ="select work_day,casual_leave,earned_leave from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(number)+"' and year_id='"+str(temp_year[0][0])+"' "                           
                            self.cr.execute(query)
                            temp_salary_line = self.cr.fetchall()
                            if temp_salary_line:
                                l4.append(temp_salary_line[0])
                                self.work_total+=temp_salary_line[0][0]
                                self.casual_total+=temp_salary_line[0][1]
                                self.earned_total+=temp_salary_line[0][2]
                            else:
                                tup3=(0,0,0)
                                l4.append(tup3)  
                        else:
                            query ="select work_day,casual_leave,earned_leave from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(number)+"' and year_id='"+str(temp_year[0][0])+"' "                           
                            self.cr.execute(query)
                            temp_salary_line = self.cr.fetchall()
                            if temp_salary_line:
                                l4.append(temp_salary_line[0])
                                self.work_total+=temp_salary_line[0][0]
                                self.casual_total+=temp_salary_line[0][1]
                                self.earned_total+=temp_salary_line[0][2]
                            else:
                                tup3=(0,0,0)
                                l4.append(tup3)   
            if last_year :
                from_year=last_year[0:4]
                from_year = int(from_year) 
                for month1 in range(4,13):
                    month_tup = calendar.monthrange(from_year,month1)
                    if len(str(month1))==1:
                        month1_str='0'+str(month1)
                    else :
                        month1_str=str(month1)    
                    from_date1= str(from_year)+'-'+month1_str+'-'+'01'
                    till_date1=str(from_year) + '-' + month1_str + '-' + str(month_tup[1])
                    month_list1.append((from_date1,till_date1))
                for month2 in range(1,4):
                    from_year1 = int(from_year)+1
                    month_tup = calendar.monthrange(from_year1,month2)
                    if len(str(month2))==1:
                        month2_str='0'+str(month2)
                    from_date2= str(from_year1)+'-'+month2_str+'-'+'01'
                    till_date2=str(from_year1) + '-' + month2_str + '-' + str(month_tup[1])
                    month_list1.append((from_date2,till_date2))    
                    
                for from_date,till_date in month_list1: 
                    if len(list_ids) == 1 :      
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(list_ids[0])+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()
                        if temp :
                            l11.append(temp[0])
                            self.pre_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.pre_total_bonus+=temp[0][12]
                        else :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0))
                
                    else:
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(tuple(list_ids))+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()   
                        if temp :
                            l11.append(temp[0])
                            self.pre_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.pre_total_bonus+=temp[0][12]
                        else :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0))
                if l11:
                    for val in l11: 
                        if val[0] > 0.0 and val[12]>0.0:
                            pre_salary= val[0]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[1] > 0.0 and val[12]>0.0:
                            pre_salary= val[1]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1) 
                            
                        elif val[2] > 0.0 and val[12]>0.0:
                            pre_salary= val[2]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                             
                        elif val[3] > 0.0 and val[12]>0.0:
                            pre_salary= val[3]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)        
    
                        elif val[4] > 0.0 and val[12]>0.0:
                            pre_salary= val[4]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[5] > 0.0 and val[12]>0.0:
                            pre_salary= val[5]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[6] > 0.0 and val[12]>0.0:
                            pre_salary= val[6]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[7] > 0.0 and val[12]>0.0:
                            pre_salary= val[7]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[8] > 0.0 and val[12]>0.0:
                            pre_salary= val[8]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)        
    
                        elif val[9] > 0.0 and val[12]>0.0:
                            pre_salary= val[9]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[10] > 0.0 and val[12]>0.0:
                            pre_salary= val[10]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[11] > 0.0 and val[12]>0.0:
                            pre_salary= val[11]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                        else :
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
        elif current_year == last_year:
            if current_year :
                from_year=current_year[0:4]
                from_year = int(from_year) 
                
                for month1 in range(4,13):
                    month_tup = calendar.monthrange(from_year,month1)
                    if len(str(month1))==1:
                        month1_str='0'+str(month1)
                    else :
                        month1_str=str(month1)    
                    from_date1= str(from_year)+'-'+month1_str+'-'+'01'
                    till_date1=str(from_year) + '-' + month1_str + '-' + str(month_tup[1])
                    month_list.append((from_date1,till_date1))
                for month2 in range(1,4):
                    from_year1 = int(from_year)+1
                    month_tup = calendar.monthrange(from_year1,month2)
                    if len(str(month2))==1:
                        month2_str='0'+str(month2)
                    from_date2= str(from_year1)+'-'+month2_str+'-'+'01'
                    till_date2=str(from_year1) + '-' + month2_str + '-' + str(month_tup[1])
                    month_list.append((from_date2,till_date2))
                
     
                for from_date,till_date in month_list : 
                    if len(list_ids) == 1 :      
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(list_ids[0])+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall() 
                        if temp :
                            l.append(temp[0])
                            self.curr_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.curr_total_bonus+=temp[0][12]
                        else :
                            l.append((0,0,0,0,0,0,0,0,0,0,0,0))
                    else:
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(tuple(list_ids))+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()   
                        if temp :
                            l.append(temp[0])
                            self.curr_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.curr_total_bonus+=temp[0][12]
                        else :
                            l.append((0,0,0,0,0,0,0,0,0,0,0,0))
                if l:
                    for val in l: 
                        if val[0] > 0.0 and val[12]>0.0:
                            curr_salary= val[0]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[1] > 0.0 and val[12]>0.0:
                            curr_salary= val[1]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup) 
                             
                        elif val[2] > 0.0 and val[12]>0.0:
                            curr_salary= val[2]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                              
                        elif val[3] > 0.0 and val[12]>0.0:
                            curr_salary= val[3]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)        
     
                        elif val[4] > 0.0 and val[12]>0.0:
                            curr_salary= val[4]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[5] > 0.0 and val[12]>0.0:
                            curr_salary= val[5]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[6] > 0.0 and val[12]>0.0:
                            curr_salary= val[6]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[7] > 0.0 and val[12]>0.0:
                            curr_salary= val[7]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[8] > 0.0 and val[12]>0.0:
                            curr_salary= val[8]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)        
     
                        elif val[9] > 0.0 and val[12]>0.0:
                            curr_salary= val[9]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[10] > 0.0 and val[12]>0.0:
                            curr_salary= val[10]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[11] > 0.0 and val[12]>0.0:
                            curr_salary= val[11]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                        else :
                            curr_salary= 0.0
                            curr_salary=0.0 
                            tup=(curr_salary,curr_salary)
                            l1.append(tup) 
                            
                query ="select id from holiday_year where name='"+str(month.year_id.name)+"' "        
                self.cr.execute(query)
                temp_year = self.cr.fetchall() 
                if temp_year:           
                    for number in range(1,13) : 
                        if len(list_ids) == 1 : 
                            query ="select work_day,casual_leave,earned_leave from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(number)+"' and year_id='"+str(temp_year[0][0])+"' "                           
                            self.cr.execute(query)
                            temp_salary_line = self.cr.fetchall()
                            if temp_salary_line:
                                l4.append(temp_salary_line[0])
                                self.work_total+=temp_salary_line[0][0]
                                self.casual_total+=temp_salary_line[0][1]
                                self.earned_total+=temp_salary_line[0][2]
                            else:
                                tup3=(0,0,0)
                                l4.append(tup3)  
                        else:
                            query ="select work_day,casual_leave,earned_leave from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(number)+"' and year_id='"+str(temp_year[0][0])+"' "                           
                            self.cr.execute(query)
                            temp_salary_line = self.cr.fetchall()
                            if temp_salary_line:
                                l4.append(temp_salary_line[0])
                                self.work_total+=temp_salary_line[0][0]
                                self.casual_total+=temp_salary_line[0][1]
                                self.earned_total+=temp_salary_line[0][2]
                            else:
                                tup3=(0,0,0)
                                l4.append(tup3)   
            if last_year :
                from_year=last_year[0:4]
                from_year = int(from_year) 
                for month1 in range(4,13):
                    month_tup = calendar.monthrange(from_year,month1)
                    if len(str(month1))==1:
                        month1_str='0'+str(month1)
                    else :
                        month1_str=str(month1)    
                    from_date1= str(from_year)+'-'+month1_str+'-'+'01'
                    till_date1=str(from_year) + '-' + month1_str + '-' + str(month_tup[1])
                    month_list1.append((from_date1,till_date1))
                for month2 in range(1,4):
                    from_year1 = int(from_year)+1
                    month_tup = calendar.monthrange(from_year1,month2)
                    if len(str(month2))==1:
                        month2_str='0'+str(month2)
                    from_date2= str(from_year1)+'-'+month2_str+'-'+'01'
                    till_date2=str(from_year1) + '-' + month2_str + '-' + str(month_tup[1])
                    month_list1.append((from_date2,till_date2))    
                    
                for from_date,till_date in month_list1: 
                    if len(list_ids) == 1 :      
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(list_ids[0])+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()
                        if temp :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0,0))
                            self.pre_total_salary+=0
                            self.pre_total_bonus+=0
                        else :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0,0))
                
                    else:
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(tuple(list_ids))+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()   
                        if temp :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0,0))
                            self.pre_total_salary+=0
                            self.pre_total_bonus+=0
                        else :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0,0))
                if l11:
                    for val in l11: 
                        if val[0] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[1] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1) 
                            
                        elif val[2] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                             
                        elif val[3] == 0.0 and val[12]==0.0:
                            pre_salary= 0
                            pre_bonus=0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)        
    
                        elif val[4] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[5] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[6] == 0.0 and val[12]==0.0:
                            pre_salary= 0
                            pre_bonus=0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[7] > 0.0 and val[12]>0.0:
                            pre_salary= val[7]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[8] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)        
    
                        elif val[9] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[10] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[11] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                        else :
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
            
      
        for val1 in l1:       
            tup2=(val1)+(l2[c])+(l4[c])
            c=c+1
            d=d+1
            l3.append(tup2)
        return l3
        
    def get_leave_details(self,month,emp): 
        basic=0
        other_salary=0
        opening_bal =0
        curr_due_leave=0
        erned_total=0
        total_el = 0
        leave_availed=[]
        bal_leave=0
        l=[]
        l1=[]
        l2=[]
        l3=[]
        tup1=()
        tup2=()
        tup3=()
        count=0
        start_date = str(month.year_id.name) + '-' + '01' + '-' + '01'
        end_date=str(month.year_id.name)+'-'+'12'+'-'+'31'
        start_date = datetime.strptime(start_date,"%Y-%m-%d")
        end_date = datetime.strptime(end_date,"%Y-%m-%d")
        emp_obj = self.pool.get('hr.employee')
        list_ids = emp_obj.search(self.cr, 1, [('id', '=',emp.id),('active','=',True)])
        if len(list_ids) == 0 :   
                 raise osv.except_osv(('Warning !'),("Record Not Found !!!"))
             
        opening_date = str(month.year_id.name) + '-01-01'
        que1 = self.cr.execute("select earn_leave from hr_employee where id='"+str(emp.id)+"' ")
        tmp1 = self.cr.fetchall()
        if tmp1 and tmp1[0][0] != None:
            opening_bal = tmp1[0][0]
            
        que2 = self.cr.execute("select sum(curr_earn-prev_earn) from earn_leave_history where employee_id='"+str(emp.id)+"' and name >= '"+str(opening_date)+"'  ")
        tmp2 = self.cr.fetchall()
        if tmp2 and tmp2[0][0] != None :
            opening_bal = opening_bal - tmp2[0][0]
            curr_due_leave=tmp2[0][0] 
            
        que3 = self.cr.execute("select sum(hol.number_of_days_temp) from hr_holidays as hol left join hr_holidays_status as hol_status on (hol.holiday_status_id=hol_status.id) where hol.employee_id='"+str(emp.id)+"' and hol.from_date >= '"+str(opening_date)+"' and hol_status.name='Earned Leaves' and hol.state='validate' and hol.type='remove' ")  
        tmp3 = self.cr.fetchall()
        if tmp3 and tmp3[0][0] != None :
            opening_bal = opening_bal + tmp3[0][0] 
                  
        if opening_bal != None:         
            erned_total=opening_bal+curr_due_leave
        
        
        for val_date in rrule.rrule(rrule.DAILY,dtstart=start_date,until=end_date):
            val_date_str = val_date.strftime('%Y-%m-%d')
            q3 = self.cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp.id)+"' and state='validate' and type='remove' ")
            tmp4 = self.cr.fetchall()
            if tmp4 :    
                for val1 in tmp4 :
                    for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                        if leave_date == val_date :
                            if val1[2] == 'Earned Leaves' : 
                                el_date = leave_date.strftime('%d')
                                leave_availed.append(el_date)
        bal_leave= erned_total-len(leave_availed)
        if month:
            if len(list_ids) == 1 :
                 query ="select current_salary,other_salary from hr_employee where id = '"+str(list_ids[0])+"'  group by current_salary,other_salary"                       
                 self.cr.execute(query)
                 temp = self.cr.fetchall()
                 if temp and temp[0][0] != None:
                     basic=temp[0][0]
                 if temp and temp[0][1] != None:
                     other_salary=temp[0][1]
            else:
                 query ="select current_salary,other_salary from hr_employee where id = '"+str(tuple(list_ids))+"'  group by current_salary,other_salary"                       
                 self.cr.execute(query)
                 temp = self.cr.fetchall()
                 if temp and temp[0][0] != None:
                     basic=temp[0][0]
                 if temp and temp[0][1] != None:
                     other_salary=temp[0][1]
        
        tup=(opening_bal,curr_due_leave,erned_total,len(leave_availed),bal_leave,basic,other_salary) 
        l1.append(tup)  
        return l1 
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_work_total(self):
        return self.work_total
    
    def get_casual_total(self):
        return self.casual_total
    
    def get_earned_total(self):
        return self.earned_total
    
    def get_curr_total_bonus(self):
        return  self.curr_total_bonus
    
    def get_curr_total_salary(self):
        return self.curr_total_salary
    
    def get_pre_total_salary(self):
        return self.pre_total_salary
    
    def get_pre_total_bonus(self):
        return self.pre_total_bonus    
 
      
    
class report_employee_details(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_details'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_details'
    _wrapped_report_class = employee_details  
    
    
#                            [[[[[[[[[[[================Employee PF Forms==========]]]]]]]]]]]]]]]

class employee_pf_form19_form10(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_pf_form19_form10, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_company":self.get_company,
                                   "get_father_form10":self.get_father_form10,
                                   "get_my_date":self.get_my_date,
                                  })
    def get_my_date(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y")
        return date1
        
    def get_company(self,employee):
        comp_name=''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        c_name=emp_browse.company_id.name
        if c_name:
            if c_name[0:1] == 'D':
                comp_name= 'Designco'
            if c_name[0:1]=='L':
                comp_name = 'Lohia Brass Pvt Ltd' 
        return comp_name  
    
    def get_father_form10(self,employee):
        l = []
        tup = ()
        rel_name = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)            
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.relation == 'Father': 
                    rel_name=val.name  
                if val.relation == 'Husband':
                    rel_name = val.name           
        tup = (rel_name)
        l.append(tup)
        return l  
        
class report_employee_pf_form19_form10(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_pf_form19_form10'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_pf_form19_form10'
    _wrapped_report_class = employee_pf_form19_form10  


#                            [[[[[[[[[[[================EMPLOYEE JOINT DECLARATION FORM==========]]]]]]]]]]]]]]]

class employee_joint_declaration_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_joint_declaration_form, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_company":self.get_company,
                                   "get_father_form10":self.get_father_form10,
                                   "get_my_date":self.get_my_date,
                                  })
    def get_my_date(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y")
        return date1
        
    def get_company(self,employee):
        comp_name=''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        c_name=emp_browse.company_id.name
        if c_name:
            if c_name[0:1] == 'D':
                comp_name= 'Designco'
            if c_name[0:1]=='L':
                comp_name = 'Lohia Brass Pvt Ltd' 
        return comp_name  
    
    def get_father_form10(self,employee):
        l = []
        tup = ()
        rel_name = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)            
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.relation == 'Father': 
                    rel_name=val.name  
                if val.relation == 'Husband':
                    rel_name = val.name           
        tup = (rel_name)
        l.append(tup)
        return l  
        
class report_employee_joint_declaration_form(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_joint_declaration_form'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_joint_declaration_form'
    _wrapped_report_class = employee_joint_declaration_form  


####============================= [[ Employee Salary Certificate ]]==================================


class employee_salary_certificate(report_sxw.rml_parse):
    salary_total=0.0
    pf_total=0.0
    
    def __init__(self, cr, uid, name, context):
        super(employee_salary_certificate, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                   "get_company":self.get_company,
                                   "get_my_date":self.get_my_date,
                                   "get_total_salary":self.get_total_salary,
                                   "get_total_pf":self.get_total_pf,
                                   "convert":self.convert,
                                   "convert1":self.convert1,
                                  })
        
    def get_my_date(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y")
        return date1
        
    def get_company(self,employee):
        comp_name=''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        c_name=emp_browse.company_id.name
        if c_name:
            if c_name[0:1] == 'D':
                comp_name= 'Designco'
            if c_name[0:1]=='L':
                comp_name = 'Lohia Brass Pvt Ltd' 
        return comp_name
    
    def get_total_salary(self,curr_year,emp_id):
        year_cal=curr_year[0:4]
        year_cal1=curr_year[5:9]
        total_salary=0.0
        total_salary1=0.0
        final_salary=0.0
        year_qry="select id from holiday_year where name= '"+str(year_cal)+"' "
        self.cr.execute(year_qry)
        year_temp = self.cr.fetchall()
        if year_temp and year_temp[0][0]!=None:
            year_id=year_temp[0][0]
                      
        year_qry1="select id from holiday_year where name= '"+str(year_cal1)+"' "
        self.cr.execute(year_qry1)
        year_temp1 = self.cr.fetchall()
        if year_temp1 and year_temp1[0][0]!=None:
            year_id1=year_temp1[0][0]
            
        if  year_id and year_id1 :
            query ="select sum(total_amount) from salary_payment_line where employee_id = '"+str(emp_id)+"' and month in ('4','5','6','7','8','9','10','11','12') and year_id='"+str(year_id)+"' "                       
            self.cr.execute(query)
            temp = self.cr.fetchall()
            if temp and temp[0][0]!=None :
                total_salary = temp[0][0]
            query1 ="select sum(total_amount) from salary_payment_line where employee_id = '"+str(emp_id)+"' and month in ('1','2','3') and year_id='"+str(year_id1)+"' "                       
            self.cr.execute(query1)
            temp1 = self.cr.fetchall()
            if temp1 and temp1[0][0]!=None :
                total_salary1 = temp1[0][0] 
            final_salary = total_salary + total_salary1
            self.salary_total=final_salary 
        return final_salary                                                                                                                                                                                                                                                                                                                                                                                                            
    
    def get_total_pf(self,curr_year,emp_id):
        year_cal=curr_year[0:4]
        year_cal1=curr_year[5:9]
        total_pf=0
        total_pf1=0
        final_pf=0
        year_qry="select id from holiday_year where name= '"+str(year_cal)+"' "
        self.cr.execute(year_qry)
        year_temp = self.cr.fetchall()
        if year_temp and year_temp[0][0]!=None:
            year_id=year_temp[0][0]
            
        year_qry1="select id from holiday_year where name= '"+str(year_cal1)+"' "
        self.cr.execute(year_qry1)
        year_temp1 = self.cr.fetchall()
        if year_temp1 and year_temp1[0][0]!=None:
            year_id1=year_temp1[0][0]

        if  year_id and year_id1 :
            query ="select sum(epf) from salary_payment_line where employee_id = '"+str(emp_id)+"' and month in ('4','5','6','7','8','9','10','11','12') and year_id='"+str(year_id)+"' "                       
            self.cr.execute(query)
            temp = self.cr.fetchall()
            if temp and temp[0][0]!=None:
                total_pf = temp[0][0]
                
            query1 ="select sum(epf) from salary_payment_line where employee_id = '"+str(emp_id)+"' and month in ('1','2','3') and year_id='"+str(year_id1)+"' "                       
            self.cr.execute(query1)
            temp1 = self.cr.fetchall()
            if temp1 and temp1[0][0]!=None :
                total_pf1 = temp1[0][0] 
            final_pf = total_pf + total_pf1 
            self.pf_total=final_pf     
        return final_pf
        
    def convert(self,curr_year,emp_id):
        amount=self.get_total_salary(curr_year,emp_id)
        amt_en = num2word.convertNumberToWords(amount) 
        a=amt_en.replace('Rupees','Rupees')
        c = a.replace('paise','paise')
        
        return c

    def convert1(self,curr_year,emp_id):
        amount=self.get_total_pf(curr_year,emp_id)
        amt_en = num2word.convertNumberToWords(amount) 
        a=amt_en.replace('Rupees','Rupees')
        c = a.replace('paise','paise')
        
        return c
        
    
class report_employee_salary_certificate(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_salary_certificate'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_salary_certificate'
    _wrapped_report_class = employee_salary_certificate 

####============================= [[ Employee Salary EXP Certificate ]]==================================

class employee_salary_exp_certificate(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_salary_exp_certificate, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_my_date":self.get_my_date,
                                  })

    def get_my_date(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y")
        return date1
        
    
class report_employee_salary_exp_certificate(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_salary_exp_certificate'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_salary_exp_certificate'
    _wrapped_report_class = employee_salary_exp_certificate
    
    
    
###============================ [[ Fire Training Report PDF ]] ==============================###= 

class employee_fire_training(report_sxw.rml_parse):
          
    def __init__(self, cr, uid, name, context):    
        super(employee_fire_training, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  
                                  })

class report_employee_fire_training(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_fire_training'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_fire_training'
    _wrapped_report_class = employee_fire_training 

####============================= [[ Employee Form 15G ]]==================================

class employee_form15g_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_form15g_report, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                                                   
                                })
   
        
class report_employee_form15g_report(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_form15g_report'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_form15g_report'
    _wrapped_report_class = employee_form15g_report 


 ## ========================================Leave Application==========================================    


class employee_leave_application(report_sxw.rml_parse):

    
    def __init__(self, cr, uid, name, context):
        super(employee_leave_application, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                   "get_my_date":self.get_my_date,
                                   "get_from_date":self.get_from_date,
                                   "get_end_date":self.get_end_date,
                                  })
    def get_my_date(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y")
        return date1    
        
    def get_from_date(self,start_date):
        if start_date: 
             date1 = datetime.strptime(start_date,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1

    def get_end_date(self,end_date):
        if end_date: 
             date1 = datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
             date1 = date1.strftime("%d-%m-%Y")
             return date1

class report_employee_leave_application(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_leave_application'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_leave_application'
    _wrapped_report_class = employee_leave_application

    









 ## =========================================Contractor Reports Start==========================================    







 ## =========================================Contractor FnF Details==========================================    
    
class contractor_details(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_details, self).__init__(cr, 1, name, context=context)
        self.count=0
        self.localcontext.update({
                                  "get_bonus_details":self.get_bonus_details,
                                  "get_bonus_lines":self.get_bonus_lines,
                                  "get_sequence":self.get_sequence,
                                  "get_work_total":self.get_work_total,
                                  "get_casual_total":self.get_casual_total,
                                  "get_earned_total":self.get_earned_total,
                                  "get_pre_total_salary":self.get_pre_total_salary,
                                  "get_pre_total_bonus":self.get_pre_total_bonus,
                                  "get_curr_total_salary":self.get_curr_total_salary,
                                  "get_curr_total_bonus":self.get_curr_total_bonus,
                                  "get_leave_details":self.get_leave_details,
                                  "get_month_pay_details":self.get_month_pay_details,
#                                   "get_total_pay_details":self.get_total_pay_details
#                                   "get_final_details":self.get_final_details
                                  })
        
  

    def get_bonus_details(self,last_year,current_year,employee,month,bal_leave):
        leave_enca=bal_leave
        loan_advance=0
        list_ids = []
        l=[]
        tup=()
        curr_salary=0.0
        curr_bonus=0
        pre_salary=0.0
        pre_bonus=0
        total_salary=0.0
        total_bonus=0.0
        basic=0.0
        paid_salary=0.0
        pay_total=0.0
        TOTAL_PAY=0.0
        leave_pay=0.0
        paid_total=0.0
        loan=0.0
        advance=0.0
        gratuity=0.0
        less_total=0.0
        emp_obj = self.pool.get('hr.employee')
        list_ids = emp_obj.search(self.cr, 1, [('id', '=',employee.id),('active','=',True)])  
        if len(list_ids) == 0 :   
                 raise osv.except_osv(('Warning !'),("Record Not Found !!!")) 
        if len(list_ids) == 1 :
             query ="select balance from loan_deduction where emp_id = '"+str(list_ids[0])+"' and state='done' "                       
             self.cr.execute(query)
             temp_loan = self.cr.fetchall()
        else:    
             query ="select balance from loan_deduction where emp_id = '"+str(list_ids[0])+"' and state='done' "                       
             self.cr.execute(query)
             temp_loan = self.cr.fetchall()   
        if temp_loan:
            loan=temp_loan[0][0]
        
        if current_year != last_year:
            if current_year :
                from_year=current_year[0:4]
                from_date=from_year+'-'+'04'+'-'+'01'
                from_date=datetime.strptime(from_date, "%Y-%m-%d")
                till_year=current_year[5:10]
                till_date=till_year+'-'+'03'+'-'+'31'
                till_date=datetime.strptime(till_date, "%Y-%m-%d")
                if len(list_ids) == 1 :
                    query="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(list_ids[0])+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query)
                    temp = self.cr.fetchall()              
                else:
                    query="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(tuple(list_ids))+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query)
                    temp = self.cr.fetchall()
                if temp and temp[0][0]!=None and temp[0][1]!=None :
                    curr_salary=temp[0][0]
                    curr_bonus=temp[0][1]
                else:
                    curr_salary=0.0
                    curr_bonus=0.0
                    
            if last_year :
                from_year=last_year[0:4]
                from_date=from_year+'-'+'04'+'-'+'01'
                from_date=datetime.strptime(from_date, "%Y-%m-%d")
                till_year=last_year[5:10]
                till_date=till_year+'-'+'03'+'-'+'31'
                till_date=datetime.strptime(till_date, "%Y-%m-%d")
                if len(list_ids) == 1 :
                    query1="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(list_ids[0])+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query1)
                    temp1 = self.cr.fetchall() 
                    
                else:
                    query1="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(tuple(list_ids))+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query1)
                    temp1 = self.cr.fetchall()
                if temp1 and temp1[0][0]!=None and temp1[0][1]!=None :
                    pre_salary=temp1[0][0]
                    pre_bonus=temp1[0][1]
                else:
                    pre_salary=0.0
                    pre_bonus=0.0
                    
        elif current_year == last_year:
            if current_year :
                from_year=current_year[0:4]
                from_date=from_year+'-'+'04'+'-'+'01'
                from_date=datetime.strptime(from_date, "%Y-%m-%d")
                till_year=current_year[5:10]
                till_date=till_year+'-'+'03'+'-'+'31'
                till_date=datetime.strptime(till_date, "%Y-%m-%d")
                if len(list_ids) == 1 :
                    query="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(list_ids[0])+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query)
                    temp = self.cr.fetchall()              
                else:
                    query="select sum(total_salary),sum(bonus) from payment_management_bonus_line where employee_id = '"+str(tuple(list_ids))+"' "\
                              " and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' " 
                    self.cr.execute(query)
                    temp = self.cr.fetchall()
                if temp and temp[0][0]!=None and temp[0][1]!=None :
                    curr_salary=temp[0][0]
                    curr_bonus=temp[0][1]
                    pre_salary=0.0
                    pre_bonus=0.0
                    
                else:
                    curr_salary=0.0
                    curr_bonus=0.0
                    pre_salary=0.0
                    pre_bonus=0.0
                    
                
        if curr_salary and pre_salary :            
            total_salary=curr_salary+pre_salary
            total_bonus=curr_bonus +pre_bonus 
        elif curr_salary :
            total_salary=curr_salary 
            total_bonus=curr_bonus  
        elif pre_salary :
            total_salary=pre_salary 
            total_bonus=pre_bonus     
        else:
            total_salary=0.0
            total_bonus=0.0

        if month:
            if len(list_ids) == 1 :
                 query ="select basic,grand_total,kharcha from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(month.month)+"' and year_id='"+str(month.year_id.id)+"' group by basic,grand_total,kharcha "                       
                 self.cr.execute(query)
                 temp = self.cr.fetchall()
                 query_hr ="select total_salary from hr_employee where id = '"+str(list_ids[0])+"'  group by total_salary"                       
                 self.cr.execute(query_hr)
                 temp_hr = self.cr.fetchall()
                 if temp_hr and temp_hr[0][0] != None:
                     basic=temp_hr[0][0]
                 query_hr1 ="select current_salary from hr_employee where id = '"+str(list_ids[0])+"'  group by current_salary"                       
                 self.cr.execute(query_hr1)
                 temp_hr1 = self.cr.fetchall()
                 if temp_hr1 and temp_hr1[0][0] != None:
                     basic1=temp_hr1[0][0]
                
            else:
                 query ="select basic,grand_total,kharcha from salary_payment_line where employee_id = '"+str(tuple(list_ids))+"' and month='"+str(month.month)+"' and year_id='"+str(month.year_id.id)+"' group by basic,grand_total,kharcha  "                       
                 self.cr.execute(query)
                 temp = self.cr.fetchall() 
                 query_hr ="select total_salary from hr_employee where id = '"+str(tuple(list_ids))+"'  group by total_salary"                       
                 self.cr.execute(query_hr)
                 temp_hr = self.cr.fetchall()
                 if temp_hr and temp_hr[0][0] != None:
                     basic=temp_hr[0][0]
                 query_hr1 ="select current_salary from hr_employee where id = '"+str(tuple(list_ids))+"'  group by current_salary"                       
                 self.cr.execute(query_hr1)
                 temp_hr1 = self.cr.fetchall()
                 if temp_hr1 and temp_hr1[0][0] != None:
                     basic1=temp_hr1[0][0]
                 
            if temp:
#                 basic=temp[0][0]
                 paid_salary=temp[0][1]
                 advance=temp[0][2]
                 
        if len(list_ids) == 1 :
            emp_browse =emp_obj.browse(self.cr,1,employee.id)
            doj=emp_browse.doj
            doj = datetime.strptime(doj, "%Y-%m-%d")
            doj=doj.date()
            today_date = date.today()
            days = (today_date - doj).days
            months=days/30
            years=months/12
            months1 = months - (years*12)
            if years >=5 and months1 < 6:
                gratuity=(15*years*basic1)/26
                gratuity=round(gratuity,0)
            elif years >=5 and months1 >= 6:
                years=years+1 
                gratuity=(15*years*basic1)/26 
                gratuity=round(gratuity,0)
            else:
                gratuity=0.0      
                    
        leave_pay=(basic / 26 )*(leave_enca) 
        leave_pay=round(leave_pay,0)
        bonus=curr_bonus+pre_bonus
        paid_total=(paid_salary+leave_pay+gratuity+bonus) 
        less_total=loan               
        TOTAL_PAY=paid_total-less_total  
        tup=(curr_salary,curr_bonus,pre_salary,pre_bonus,total_salary,total_bonus,paid_salary,leave_enca,leave_pay,paid_total,loan,advance,gratuity,less_total,TOTAL_PAY)
        l.append(tup)     
        return l   
    
    def get_month_pay_details(self,emp,month):
        tup6=()
        l6=[]
        emp_obj = self.pool.get('hr.employee')
        list_ids = emp_obj.search(self.cr, 1, [('id', '=',emp.id),('active','=',True)])
        if len(list_ids) == 0 :   
                 raise osv.except_osv(('Warning !'),("Record Not Found !!!")) 
        if month :
            if len(list_ids) == 1 : 
                query ="select days,days_amount,epf,kharcha,tds,esi,total_over_time,sum(overtime_amount+sun_overtime_amount),grand_total from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(month.month)+"' and year_id='"+str(month.year_id.id)+"' "\
                       " group by days,epf,kharcha,tds,esi,total_over_time,grand_total,days_amount  "                         
                self.cr.execute(query)
                temp_line = self.cr.fetchall()
            else:
                query ="select days,days_amount,epf,kharcha,tds,esi,total_over_time,sum(overtime_amount+sun_overtime_amount),grand_total from salary_payment_line where employee_id = '"+str(tuple(list_ids))+"' and month='"+str(month.month)+"' and year_id='"+str(month.year_id.id)+"' "\
                       " group by days,epf,kharcha,tds,esi,total_over_time,grand_total,days_amount  "                         
                self.cr.execute(query)
                temp_line = self.cr.fetchall()
            if temp_line:
                    tup6=(temp_line[0][0],temp_line[0][1],temp_line[0][2],temp_line[0][3],temp_line[0][4],temp_line[0][5],temp_line[0][6],temp_line[0][7],temp_line[0][8]) 
                    l6.append(tup6)            
                    return l6
            else:
                 tup6=(0,0,0,0,0,0,0,0,0) 
                 l6.append(tup6)
                 return l6
            

  
    def get_bonus_lines(self,last_year,current_year,month,employee):
        self.work_total=0
        self.pre_total_salary=0.0
        self.curr_total_salary=0.0
        self.curr_total_bonus=0.0
        self.pre_total_bonus=0.0
        self.casual_total=0
        self.earned_total=0
        d=0
        l5=[]
        l=[]
        count=0
        l1=[]
        l2=[]
        l3=[]
        l5=[]
        l11=[]
        l4=[]
        l6=[]
        tup7=()
        c=0
        month_list=[]
        month_list1=[]
        list_ids = []   
        tup=()
        tup1=()
        tup2=()
        tup3=()
        tup4=()
        tup6=()
        curr_salary=''
        curr_bonus=''
        pre_salary=''
        pre_bonus=''
        emp_obj = self.pool.get('hr.employee')
        list_ids = emp_obj.search(self.cr, 1, [('id', '=',employee.id),('active','=',True)])
        if len(list_ids) == 0 :   
                 raise osv.except_osv(('Warning !'),("Record Not Found !!!"))  
        
        if current_year !=  last_year:     
            if current_year :
                from_year=current_year[0:4]
                from_year = int(from_year) 
                
                for month1 in range(4,13):
                    month_tup = calendar.monthrange(from_year,month1)
                    if len(str(month1))==1:
                        month1_str='0'+str(month1)
                    else :
                        month1_str=str(month1)    
                    from_date1= str(from_year)+'-'+month1_str+'-'+'01'
                    till_date1=str(from_year) + '-' + month1_str + '-' + str(month_tup[1])
                    month_list.append((from_date1,till_date1))
                for month2 in range(1,4):
                    from_year1 = int(from_year)+1
                    month_tup = calendar.monthrange(from_year1,month2)
                    if len(str(month2))==1:
                        month2_str='0'+str(month2)
                    from_date2= str(from_year1)+'-'+month2_str+'-'+'01'
                    till_date2=str(from_year1) + '-' + month2_str + '-' + str(month_tup[1])
                    month_list.append((from_date2,till_date2))
                
     
                for from_date,till_date in month_list : 
                    if len(list_ids) == 1 :      
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(list_ids[0])+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall() 
                        if temp :
                            l.append(temp[0])
                            self.curr_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.curr_total_bonus+=temp[0][12]
                        else :
                            l.append((0,0,0,0,0,0,0,0,0,0,0,0))
                    else:
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(tuple(list_ids))+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()   
                        if temp :
                            l.append(temp[0])
                            self.curr_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.curr_total_bonus+=temp[0][12]
                        else :
                            l.append((0,0,0,0,0,0,0,0,0,0,0,0))
                if l:
                    for val in l: 
                        if val[0] > 0.0 and val[12]>0.0:
                            curr_salary= val[0]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[1] > 0.0 and val[12]>0.0:
                            curr_salary= val[1]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup) 
                             
                        elif val[2] > 0.0 and val[12]>0.0:
                            curr_salary= val[2]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                              
                        elif val[3] > 0.0 and val[12]>0.0:
                            curr_salary= val[3]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)        
     
                        elif val[4] > 0.0 and val[12]>0.0:
                            curr_salary= val[4]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[5] > 0.0 and val[12]>0.0:
                            curr_salary= val[5]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[6] > 0.0 and val[12]>0.0:
                            curr_salary= val[6]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[7] > 0.0 and val[12]>0.0:
                            curr_salary= val[7]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[8] > 0.0 and val[12]>0.0:
                            curr_salary= val[8]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)        
     
                        elif val[9] > 0.0 and val[12]>0.0:
                            curr_salary= val[9]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[10] > 0.0 and val[12]>0.0:
                            curr_salary= val[10]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[11] > 0.0 and val[12]>0.0:
                            curr_salary= val[11]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                        else :
                            curr_salary= 0.0
                            curr_salary=0.0 
                            tup=(curr_salary,curr_salary)
                            l1.append(tup) 
                            
                query ="select id from holiday_year where name='"+str(month.year_id.name)+"' "        
                self.cr.execute(query)
                temp_year = self.cr.fetchall() 
                if temp_year:           
                    for number in range(1,13) : 
                        if len(list_ids) == 1 : 
                            query ="select work_day,casual_leave,earned_leave from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(number)+"' and year_id='"+str(temp_year[0][0])+"' "                           
                            self.cr.execute(query)
                            temp_salary_line = self.cr.fetchall()
                            if temp_salary_line:
                                l4.append(temp_salary_line[0])
                                self.work_total+=temp_salary_line[0][0]
                                self.casual_total+=temp_salary_line[0][1]
                                self.earned_total+=temp_salary_line[0][2]
                            else:
                                tup3=(0,0,0)
                                l4.append(tup3)  
                        else:
                            query ="select work_day,casual_leave,earned_leave from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(number)+"' and year_id='"+str(temp_year[0][0])+"' "                           
                            self.cr.execute(query)
                            temp_salary_line = self.cr.fetchall()
                            if temp_salary_line:
                                l4.append(temp_salary_line[0])
                                self.work_total+=temp_salary_line[0][0]
                                self.casual_total+=temp_salary_line[0][1]
                                self.earned_total+=temp_salary_line[0][2]
                            else:
                                tup3=(0,0,0)
                                l4.append(tup3)   
            if last_year :
                from_year=last_year[0:4]
                from_year = int(from_year) 
                for month1 in range(4,13):
                    month_tup = calendar.monthrange(from_year,month1)
                    if len(str(month1))==1:
                        month1_str='0'+str(month1)
                    else :
                        month1_str=str(month1)    
                    from_date1= str(from_year)+'-'+month1_str+'-'+'01'
                    till_date1=str(from_year) + '-' + month1_str + '-' + str(month_tup[1])
                    month_list1.append((from_date1,till_date1))
                for month2 in range(1,4):
                    from_year1 = int(from_year)+1
                    month_tup = calendar.monthrange(from_year1,month2)
                    if len(str(month2))==1:
                        month2_str='0'+str(month2)
                    from_date2= str(from_year1)+'-'+month2_str+'-'+'01'
                    till_date2=str(from_year1) + '-' + month2_str + '-' + str(month_tup[1])
                    month_list1.append((from_date2,till_date2))    
                    
                for from_date,till_date in month_list1: 
                    if len(list_ids) == 1 :      
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(list_ids[0])+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()
                        if temp :
                            l11.append(temp[0])
                            self.pre_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.pre_total_bonus+=temp[0][12]
                        else :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0))
                
                    else:
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(tuple(list_ids))+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()   
                        if temp :
                            l11.append(temp[0])
                            self.pre_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.pre_total_bonus+=temp[0][12]
                        else :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0))
                if l11:
                    for val in l11: 
                        if val[0] > 0.0 and val[12]>0.0:
                            pre_salary= val[0]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[1] > 0.0 and val[12]>0.0:
                            pre_salary= val[1]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1) 
                            
                        elif val[2] > 0.0 and val[12]>0.0:
                            pre_salary= val[2]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                             
                        elif val[3] > 0.0 and val[12]>0.0:
                            pre_salary= val[3]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)        
    
                        elif val[4] > 0.0 and val[12]>0.0:
                            pre_salary= val[4]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[5] > 0.0 and val[12]>0.0:
                            pre_salary= val[5]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[6] > 0.0 and val[12]>0.0:
                            pre_salary= val[6]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[7] > 0.0 and val[12]>0.0:
                            pre_salary= val[7]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[8] > 0.0 and val[12]>0.0:
                            pre_salary= val[8]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)        
    
                        elif val[9] > 0.0 and val[12]>0.0:
                            pre_salary= val[9]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[10] > 0.0 and val[12]>0.0:
                            pre_salary= val[10]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[11] > 0.0 and val[12]>0.0:
                            pre_salary= val[11]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                        else :
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
        elif current_year == last_year:
            if current_year :
                from_year=current_year[0:4]
                from_year = int(from_year) 
                
                for month1 in range(4,13):
                    month_tup = calendar.monthrange(from_year,month1)
                    if len(str(month1))==1:
                        month1_str='0'+str(month1)
                    else :
                        month1_str=str(month1)    
                    from_date1= str(from_year)+'-'+month1_str+'-'+'01'
                    till_date1=str(from_year) + '-' + month1_str + '-' + str(month_tup[1])
                    month_list.append((from_date1,till_date1))
                for month2 in range(1,4):
                    from_year1 = int(from_year)+1
                    month_tup = calendar.monthrange(from_year1,month2)
                    if len(str(month2))==1:
                        month2_str='0'+str(month2)
                    from_date2= str(from_year1)+'-'+month2_str+'-'+'01'
                    till_date2=str(from_year1) + '-' + month2_str + '-' + str(month_tup[1])
                    month_list.append((from_date2,till_date2))
                
     
                for from_date,till_date in month_list : 
                    if len(list_ids) == 1 :      
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(list_ids[0])+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall() 
                        if temp :
                            l.append(temp[0])
                            self.curr_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.curr_total_bonus+=temp[0][12]
                        else :
                            l.append((0,0,0,0,0,0,0,0,0,0,0,0))
                    else:
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(tuple(list_ids))+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()   
                        if temp :
                            l.append(temp[0])
                            self.curr_total_salary+=temp[0][0]+temp[0][1]+temp[0][2]+temp[0][3]+temp[0][4]+temp[0][5]+temp[0][6]+temp[0][7]+temp[0][8]+temp[0][9]+temp[0][10]+temp[0][11]
                            self.curr_total_bonus+=temp[0][12]
                        else :
                            l.append((0,0,0,0,0,0,0,0,0,0,0,0))
                if l:
                    for val in l: 
                        if val[0] > 0.0 and val[12]>0.0:
                            curr_salary= val[0]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[1] > 0.0 and val[12]>0.0:
                            curr_salary= val[1]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup) 
                             
                        elif val[2] > 0.0 and val[12]>0.0:
                            curr_salary= val[2]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                              
                        elif val[3] > 0.0 and val[12]>0.0:
                            curr_salary= val[3]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)        
     
                        elif val[4] > 0.0 and val[12]>0.0:
                            curr_salary= val[4]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[5] > 0.0 and val[12]>0.0:
                            curr_salary= val[5]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[6] > 0.0 and val[12]>0.0:
                            curr_salary= val[6]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[7] > 0.0 and val[12]>0.0:
                            curr_salary= val[7]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                             
                        elif val[8] > 0.0 and val[12]>0.0:
                            curr_salary= val[8]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)        
     
                        elif val[9] > 0.0 and val[12]>0.0:
                            curr_salary= val[9]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[10] > 0.0 and val[12]>0.0:
                            curr_salary= val[10]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
     
                        elif val[11] > 0.0 and val[12]>0.0:
                            curr_salary= val[11]
                            curr_bonus=val[12] 
                            tup=(curr_salary,curr_bonus)  
                            l1.append(tup)
                        else :
                            curr_salary= 0.0
                            curr_salary=0.0 
                            tup=(curr_salary,curr_salary)
                            l1.append(tup) 
                            
                query ="select id from holiday_year where name='"+str(month.year_id.name)+"' "        
                self.cr.execute(query)
                temp_year = self.cr.fetchall() 
                if temp_year:           
                    for number in range(1,13) : 
                        if len(list_ids) == 1 : 
                            query ="select work_day,casual_leave,earned_leave from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(number)+"' and year_id='"+str(temp_year[0][0])+"' "                           
                            self.cr.execute(query)
                            temp_salary_line = self.cr.fetchall()
                            if temp_salary_line:
                                l4.append(temp_salary_line[0])
                                self.work_total+=temp_salary_line[0][0]
                                self.casual_total+=temp_salary_line[0][1]
                                self.earned_total+=temp_salary_line[0][2]
                            else:
                                tup3=(0,0,0)
                                l4.append(tup3)  
                        else:
                            query ="select work_day,casual_leave,earned_leave from salary_payment_line where employee_id = '"+str(list_ids[0])+"' and month='"+str(number)+"' and year_id='"+str(temp_year[0][0])+"' "                           
                            self.cr.execute(query)
                            temp_salary_line = self.cr.fetchall()
                            if temp_salary_line:
                                l4.append(temp_salary_line[0])
                                self.work_total+=temp_salary_line[0][0]
                                self.casual_total+=temp_salary_line[0][1]
                                self.earned_total+=temp_salary_line[0][2]
                            else:
                                tup3=(0,0,0)
                                l4.append(tup3)   
            if last_year :
                from_year=last_year[0:4]
                from_year = int(from_year) 
                for month1 in range(4,13):
                    month_tup = calendar.monthrange(from_year,month1)
                    if len(str(month1))==1:
                        month1_str='0'+str(month1)
                    else :
                        month1_str=str(month1)    
                    from_date1= str(from_year)+'-'+month1_str+'-'+'01'
                    till_date1=str(from_year) + '-' + month1_str + '-' + str(month_tup[1])
                    month_list1.append((from_date1,till_date1))
                for month2 in range(1,4):
                    from_year1 = int(from_year)+1
                    month_tup = calendar.monthrange(from_year1,month2)
                    if len(str(month2))==1:
                        month2_str='0'+str(month2)
                    from_date2= str(from_year1)+'-'+month2_str+'-'+'01'
                    till_date2=str(from_year1) + '-' + month2_str + '-' + str(month_tup[1])
                    month_list1.append((from_date2,till_date2))    
                    
                for from_date,till_date in month_list1: 
                    if len(list_ids) == 1 :      
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(list_ids[0])+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()
                        if temp :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0,0))
                            self.pre_total_salary+=0
                            self.pre_total_bonus+=0
                        else :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0,0))
                
                    else:
                        query ="select sum(apr_salary),sum(may_salary),sum(june_salary),sum(july_salary),sum(aug_salary),sum(sep_salary),sum(oct_salary),"\
                             "sum(nov_salary),sum(dec_salary),sum(jan_salary),sum(feb_salary),sum(mar_salary),bonus from payment_management_bonus_line  "\
                             "where employee_id = '"+str(tuple(list_ids))+"' and bonus_from >= '"+str(from_date)+"' and bonus_till <= '"+str(till_date)+"' group by bonus  "                           
                        self.cr.execute(query)
                        temp = self.cr.fetchall()   
                        if temp :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0,0))
                            self.pre_total_salary+=0
                            self.pre_total_bonus+=0
                        else :
                            l11.append((0,0,0,0,0,0,0,0,0,0,0,0,0))
                if l11:
                    for val in l11: 
                        if val[0] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[1] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1) 
                            
                        elif val[2] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                             
                        elif val[3] == 0.0 and val[12]==0.0:
                            pre_salary= 0
                            pre_bonus=0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)        
    
                        elif val[4] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[5] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[6] == 0.0 and val[12]==0.0:
                            pre_salary= 0
                            pre_bonus=0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[7] > 0.0 and val[12]>0.0:
                            pre_salary= val[7]
                            pre_bonus=val[12] 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                            
                        elif val[8] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)        
    
                        elif val[9] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[10] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
    
                        elif val[11] == 0.0 and val[12]==0.0:
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
                        else :
                            pre_salary= 0.0
                            pre_bonus=0.0 
                            tup1=(pre_salary,pre_bonus)  
                            l2.append(tup1)
            
      
        for val1 in l1:       
            tup2=(val1)+(l2[c])+(l4[c])
            c=c+1
            d=d+1
            l3.append(tup2)
        return l3
        
    def get_leave_details(self,month,emp): 
        basic=0
        other_salary=0
        opening_bal =0
        curr_due_leave=0
        erned_total=0
        total_el = 0
        leave_availed=[]
        bal_leave=0
        l=[]
        l1=[]
        l2=[]
        l3=[]
        tup1=()
        tup2=()
        tup3=()
        count=0
        start_date = str(month.year_id.name) + '-' + '01' + '-' + '01'
        end_date=str(month.year_id.name)+'-'+'12'+'-'+'31'
        start_date = datetime.strptime(start_date,"%Y-%m-%d")
        end_date = datetime.strptime(end_date,"%Y-%m-%d")
        emp_obj = self.pool.get('hr.employee')
        list_ids = emp_obj.search(self.cr, 1, [('id', '=',emp.id),('active','=',True)])
        if len(list_ids) == 0 :   
                 raise osv.except_osv(('Warning !'),("Record Not Found !!!"))

        opening_date = str(month.year_id.name) + '-01-01'
        que1 = self.cr.execute("select earn_leave from hr_employee where id='"+str(emp.id)+"' ")
        tmp1 = self.cr.fetchall()
        if tmp1 and tmp1[0][0] != None:
            opening_bal = tmp1[0][0]
            print"===opening_bal==",opening_bal
            
        que2 = self.cr.execute("select sum(curr_earn-prev_earn) from earn_leave_history where employee_id='"+str(emp.id)+"' and name >= '"+str(opening_date)+"'  ")
        tmp2 = self.cr.fetchall()
        if tmp2 and tmp2[0][0] != None :
            opening_bal = opening_bal - tmp2[0][0]
            curr_due_leave=tmp2[0][0] 
            print"====opening_bal1111=====",opening_bal , tmp2[0][0]
            
        que3 = self.cr.execute("select sum(hol.number_of_days_temp) from hr_holidays as hol left join hr_holidays_status as hol_status on (hol.holiday_status_id=hol_status.id) where hol.employee_id='"+str(emp.id)+"' and hol.from_date >= '"+str(opening_date)+"' and hol_status.name='Earned Leaves' and hol.state='validate' and hol.type='remove' ")  
        tmp3 = self.cr.fetchall()
        if tmp3 and tmp3[0][0] != None :
            opening_bal = opening_bal + tmp3[0][0]      
            print"=====opening_bal22222222======",opening_bal , tmp3[0][0]
            
        print"=========final=opening_bal=====" ,opening_bal , curr_due_leave 
        if opening_bal != None:        
            erned_total=opening_bal+curr_due_leave

        for val_date in rrule.rrule(rrule.DAILY,dtstart=start_date,until=end_date):
            val_date_str = val_date.strftime('%Y-%m-%d')
            q3 = self.cr.execute("select hol.from_date,hol.date_to,hol1.name from hr_holidays as hol left join hr_holidays_status as hol1 on (hol.holiday_status_id=hol1.id) where employee_id='"+str(emp.id)+"' and state='validate' and type='remove' ")
            tmp4 = self.cr.fetchall()
            if tmp4 :    
                for val1 in tmp4 :
                    for leave_date in rrule.rrule(rrule.DAILY,dtstart=datetime.strptime(val1[0],'%Y-%m-%d'),until=datetime.strptime(val1[1],'%Y-%m-%d %H:%M:%S')):
                        if leave_date == val_date :
                            if val1[2] == 'Earned Leaves' : 
                                el_date = leave_date.strftime('%d')
                                leave_availed.append(el_date)
                                
        bal_leave= erned_total-len(leave_availed)
        if month:
            if len(list_ids) == 1 :
                 query ="select current_salary,other_salary from hr_employee where id = '"+str(list_ids[0])+"'  group by current_salary,other_salary"                       
                 self.cr.execute(query)
                 temp = self.cr.fetchall()
                 if temp and temp[0][0] != None:
                     basic=temp[0][0]
                 if temp and temp[0][1] != None:
                     other_salary=temp[0][1]
            else:
                 query ="select current_salary,other_salary from hr_employee where id = '"+str(tuple(list_ids))+"' group by current_salary,other_salary"                       
                 self.cr.execute(query)
                 temp = self.cr.fetchall()
                 if temp and temp[0][0] != None:
                     basic=temp[0][0]
                 if temp and temp[0][1] != None:
                     other_salary=temp[0][1]
                     
#        print"======tup========",opening_bal,curr_due_leave,erned_total,len(leave_availed),bal_leave,basic,other_salary
        tup=(opening_bal,curr_due_leave,erned_total,len(leave_availed),bal_leave,basic,other_salary) 
        l1.append(tup)  
        return l1 
    
    def get_sequence(self):
        self.count=self.count+1
        return self.count
    
    def get_work_total(self):
        return self.work_total
    
    def get_casual_total(self):
        return self.casual_total
    
    def get_earned_total(self):
        return self.earned_total
    
    def get_curr_total_bonus(self):
        return  self.curr_total_bonus
    
    def get_curr_total_salary(self):
        return self.curr_total_salary
    
    def get_pre_total_salary(self):
        return self.pre_total_salary
    
    def get_pre_total_bonus(self):
        return self.pre_total_bonus    
 
      
    
class report_contractor_details(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_details'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_details'
    _wrapped_report_class = contractor_details  
    
    
#                            [[[[[[[[[[[================Contractor PF Forms==========]]]]]]]]]]]]]]]

class contractor_pf_form19_form10(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_pf_form19_form10, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_company":self.get_company,
                                   "get_father_form10":self.get_father_form10,
                                   "get_my_date":self.get_my_date,
                                  })
    def get_my_date(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y")
        return date1
        
    def get_company(self,employee):
        comp_name=''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        c_name=emp_browse.company_id.name
        if c_name:
            if c_name[0:1] == 'D':
                comp_name= 'Designco'
            if c_name[0:1]=='L':
                comp_name = 'Lohia Brass Pvt Ltd' 
        return comp_name  
    
    def get_father_form10(self,employee):
        l = []
        tup = ()
        rel_name = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)            
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.relation == 'Father': 
                    rel_name=val.name  
                if val.relation == 'Husband':
                    rel_name = val.name           
        tup = (rel_name)
        l.append(tup)
        return l  
        
class report_contractor_pf_form19_form10(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_pf_form19_form10'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_pf_form19_form10'
    _wrapped_report_class = contractor_pf_form19_form10 


####============================= [Contractor Form 15 G]==================================

class contractor_form15g_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_form15g_report, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({                              
                                  })
   
        
class report_contractor_form15g_report(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_form15g_report'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_form15g_report'
    _wrapped_report_class = contractor_form15g_report 




# ######### ===================================[[ Contractor  Promotion  Report ]] ====================================##########       
    
     
class contractor_promotion(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(contractor_promotion, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_data":self.get_data,
                                  "get_data1":self.get_data1,
                                  })
    
    def get_data(self,employee):
        l = []
        promotion_date = ''
        old_designation = ''
        curr_designation = ''
        query = self.cr.execute("select previous_designtation,current_designation from hr_active_history where employee_id='"+str(employee.id)+"' and previous_designtation != 'X' and current_designation !='X' order by date desc limit 1 ")
        temp =  self.cr.fetchall()
        query1 = self.cr.execute("select pro_date from promotion where employee_id='"+str(employee.id)+"' order by create_date desc limit 1 ")
        temp1 =  self.cr.fetchall()
        if temp :
            promotion_date = temp1[0][0]
            promotion_date = datetime.strptime(promotion_date,"%Y-%m-%d")
            promotion_date = promotion_date.strftime("%d-%m-%Y")
            old_designation = temp[0][0]
            curr_designation = temp[0][1]
        l.append((promotion_date,old_designation,curr_designation))
        return l        

    def get_data1(self,employee):
        father_name = ''
        query = self.cr.execute("select name from family where employee_id='"+str(employee.id)+"' and relation = 'Father' ")
        temp =  self.cr.fetchall()
        if temp :
            father_name = temp[0][0]
        return father_name        

     
class report_contractor_promotion(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_promotion'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_promotion'
    _wrapped_report_class = contractor_promotion     

# ######### ===================================[[ Contractor  Medical  Report ]] ====================================##########  

class contractor_medical(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_medical, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_father":self.get_father,
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
        
    
class contractor_medical_report(osv.AbstractModel):
    _name = 'report.hr_compliance.contractor_medical_report'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.contractor_medical_report'
    _wrapped_report_class = contractor_medical


 ######### ===================================[[ Contractor  Confirmation Letter  Report ]] ====================================##########  


class contractor_confirmation_letter(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_confirmation_letter, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                 "get_time":self.get_time,
                                 "get_father":self.get_father
                                  })
    
    def get_time(self,doj):
         if doj :
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             new_date = (date1 + relativedelta(months=+6)).strftime('%d-%m-%Y')
             return new_date
         
    def get_father(self,emp_id):
        res={}
        qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
        self.cr.execute(qry)
        temp = self.cr.fetchall()
        if temp:
            res = temp[0][0]
        else:
            res = ' '    
        return res          
    
class report_contractor_confirmation_letter(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_confirmation_letter'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_confirmation_letter'
    _wrapped_report_class = contractor_confirmation_letter


#                            [[[[[[[[[[[================CONTRACTOR JOINT DECLARATION FORM==========]]]]]]]]]]]]]]]

class contractor_joint_declaration_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_joint_declaration_form, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_company":self.get_company,
                                   "get_father_form10":self.get_father_form10,
                                   "get_my_date":self.get_my_date,
                                  })
    def get_my_date(self):
        date1=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date1 = datetime.strptime(date1,"%Y-%m-%d %H:%M:%S")
        date1 = date1 + timedelta(hours=5,minutes=30)
        date1 = date1.strftime("%d-%m-%Y")
        return date1
        
    def get_company(self,employee):
        comp_name=''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        c_name=emp_browse.company_id.name
        if c_name:
            if c_name[0:1] == 'D':
                comp_name= 'Designco'
            if c_name[0:1]=='L':
                comp_name = 'Lohia Brass Pvt Ltd' 
        return comp_name  
    
    def get_father_form10(self,employee):
        l = []
        tup = ()
        rel_name = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)            
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.relation == 'Father': 
                    rel_name=val.name  
                if val.relation == 'Husband':
                    rel_name = val.name           
        tup = (rel_name)
        l.append(tup)
        return l  
        
class report_contractor_joint_declaration_form(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_joint_declaration_form'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_joint_declaration_form'
    _wrapped_report_class = contractor_joint_declaration_form  


# ==============================================CONTRACTOR Affedavit Report==========================================


class contractor_affedavit(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_affedavit, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_father":self.get_father,
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
        
    
class report_contractor_affedavit(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_affedavit'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_affedavit'
    _wrapped_report_class = contractor_affedavit  

# ==============================================CONTRACTOR Induction Report==========================================

class contractor_induction(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_induction, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  })
        
    
class report_contractor_induction(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_induction'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_induction'
    _wrapped_report_class = contractor_induction

# ==============================================CONTRACTOR Bond==========================================

class contractor_bond(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_bond, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  })
        
    
class report_contractor_bond(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_bond'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_bond'
    _wrapped_report_class = contractor_bond



class contractor_service_record(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_service_record, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_birthday_record":self.get_birthday_record,
                                  "get_detail_record":self.get_detail_record,
                                  "get_increment_record":self.get_increment_record,
                                  "get_promotion_record":self.get_promotion_record,
                                  })
        
    def get_birthday_record(self,emp_id):
        res={}
        date1=''
        if emp_id:
            if emp_id.birthday: 
               date1 = datetime.strptime(emp_id.birthday,"%Y-%m-%d")
               date1 = date1.strftime("%d-%m-%Y")
        return date1       

    def get_detail_record(self,emp_id):
        res={}
        l=[]
        tup=()
        date1=''
        date2=''
        date3=''
        join_salary=''
        if emp_id:
            if emp_id.doa:
               date1 = datetime.strptime(emp_id.doa,"%Y-%m-%d")
               date1 = date1.strftime("%d-%m-%Y")
            if emp_id.doc :
               date2 = datetime.strptime(emp_id.doc,"%Y-%m-%d")
               date2 = date2.strftime("%d-%m-%Y")
            if emp_id.doj:
               date3 = datetime.strptime(emp_id.doj,"%Y-%m-%d")
               date3 = date3.strftime("%d-%m-%Y")
            if emp_id.joining_salary:
                  join_salary =emp_id.joining_salary
                  
            tup=(date1,date2,date3,join_salary) 
            l.append(tup)      

        return l
    
    def get_increment_record(self,emp_id):
        res={}
        increment_detail=[]
        if emp_id:
            if emp_id.increment_id:
                query="select inc_date,amount from increment where employee_id='"+str(emp_id.id)+"' order by  inc_date "
                self.cr.execute(query)
                temp = self.cr.fetchall()
                if temp:
                    for val in temp:
                        inc_date = datetime.strptime(val[0],"%Y-%m-%d")
                        inc_date = inc_date.strftime("%d-%m-%Y")
                        amount=val[1]
                        tup=(inc_date,amount)
                        increment_detail.append(tup)
            return increment_detail

    def get_promotion_record(self,emp_id):
        res={}
        promotion_detail=[]
        if emp_id:
            if emp_id.promotion_id:
                query="select pro_date,desgn_id from promotion where employee_id='"+str(emp_id.id)+"'  order by pro_date"
                self.cr.execute(query)
                temp = self.cr.fetchall()
                if temp:
                    for val in temp:
                        pro_date = datetime.strptime(val[0],"%Y-%m-%d")
                        pro_date = pro_date.strftime("%d-%m-%Y")
                        desig_browse=self.pool.get('hr.job').browse(self.cr,1,val[1]).name
                        tup1=(pro_date,desig_browse)
                        promotion_detail.append(tup1)
            return promotion_detail    
    
class report_contractor_service_record(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_service_record'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_service_record'
    _wrapped_report_class = contractor_service_record


class contractor_form11(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_form11, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_father":self.get_father,
                                   "get_time":self.get_time,
                                   "get_passport":self.get_passport,
                                   "get_aadhaar_no":self.get_aadhaar_no,
                                   "get_pan_no":self.get_pan_no,
                                   "get_bank_acc_no":self.get_bank_acc_no
                                  })
        
    def get_bank_acc_no(self,verf_id,emp_id):
        res=''
        for val in verf_id:
            if val.proof_id=='Bank_ Account_ No':
                qry="select id_no,ifsc_code from verification where proof_id='Bank_ Account_ No' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    if temp[0][0] and temp[0][1] :
                        qry_ifsc="select bic from res_bank where id='"+str(temp[0][1])+"'  "
                        self.cr.execute(qry_ifsc)
                        temp_ifsc = self.cr.fetchall()
                        if temp_ifsc :
                            res = str(temp[0][0])+' '+'&'+' '+str(temp_ifsc[0][0])
                else:
                    res = ' '         
        return res     

    def get_aadhaar_no(self,verf_id,emp_id):
        res=''
        for val in verf_id:
            if val.proof_id=='Aadhar_Card':
                qry="select id_no from verification where proof_id='Aadhar_Card' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' '         
        return res 
    
    def get_pan_no(self,verf_id,emp_id):
        res=''
        for val in verf_id:
            if val.proof_id=='PAN_Card':
                qry="select id_no from verification where proof_id='PAN_Card' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' '         
        return res     
        
        
    def get_passport(self,verf_id,emp_id):
        res=''
        for val in verf_id:
            if val.proof_id=='Passport':
                qry="select id_no from verification where proof_id='Passport' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' '         
        return res 
    

    def get_time(self,doj):
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1        
        
    def get_father(self,emp_id,fam_id):
        res=''
        for val in fam_id: 
            if val.relation=='Husband' :    
                qry = "select name from family where relation='Husband' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' ' 
            else:
                qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
                self.cr.execute(qry)
                temp = self.cr.fetchall()
                if temp:
                    res = temp[0][0]
                else:
                    res = ' ' 
                           
        return res       
        
    
class report_contractor_form11(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_form11'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_form11'
    _wrapped_report_class = contractor_form11



class contractor_fire_training(report_sxw.rml_parse):
          
    def __init__(self, cr, uid, name, context):    
        super(contractor_fire_training, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  
                                  })

class report_contractor_fire_training(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_fire_training'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_fire_training'
    _wrapped_report_class = contractor_fire_training 



class contractor_pf_nomination_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_pf_nomination_form, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_data1":self.get_data1,
                                  "get_data2":self.get_data2,
                                  "get_data3":self.get_data3,
                                  "get_data4":self.get_data4,
                                  "get_data5":self.get_data5,
                                  "get_data6":self.get_data6,
                                  })
        
    def get_data1(self,employee):
        l = []
        tup = ()
        rel_name = ''
        gender=''
        status = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        name = emp_browse.name
        sinid = emp_browse.sinid
        dob = emp_browse.birthday or ''
        dob = datetime.strptime(dob,"%Y-%m-%d")
        dob = dob.strftime("%d-%m-%Y")
        if emp_browse.gender:
            gender = emp_browse.gender.upper()
        if emp_browse.marital:
            status = emp_browse.marital.upper()
        pf_no = emp_browse.pf_number or ''
                
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.relation == 'Father' :
                    rel_name = val.name
                if val.relation == 'Husband' and rel_name == '' :
                    rel_name = val.name
        tup = (name, sinid, rel_name, dob, gender, status, pf_no)
        l.append(tup)
        return l
    
    def get_data2(self,employee):
        l = []
        tup = ()
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        address1 = emp_browse.permanent_add or ''
        address2 = emp_browse.local_add or ''
        tup = (address1, address2)
        l.append(tup)
        return l
    
    def get_data3(self,employee):
        l = []
        tup = ()
        nom_name = ''
        nom_rel = ''
        nom_age  = ''
        nom_share = ''
        nom_val = '---'
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        address = emp_browse.permanent_add or ''
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.nom_tick == True :
                    nom_name = val.name.upper()
                    nom_rel = val.relation.upper()
                    nom_age = str(val.age) + 'YRS'
                    nom_share = str(val.share) + '%'
                    break
        tup = (nom_name, address, nom_rel, nom_age, nom_share, nom_val)
        l.append(tup)
        return l
    
    def get_data4(self,employee):
        l = []
        tup = ()
        f_no = 0
        f_name = ''
        f_age  = ''
        f_rel = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        address = emp_browse.permanent_add or ''
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.reside == True:
                    f_no += 1
                    f_name = val.name.upper()
                    f_age = str(val.age) + 'YRS'
                    f_rel = val.relation.upper()
                    if f_no == 1 and len(emp_browse.family_id) == 1 :
                        address1 = address
                    elif f_no == 1 and len(emp_browse.family_id) > 1 :
                        address1 = address[0:40]
                    elif f_no == 2 :
                        address1 = address[40:80]
                    else :
                        address1 = ''
                    tup = (f_no, f_name, address1, f_age, f_rel)
                    l.append(tup)
        else : 
            tup = (f_no,f_name,address,f_age,f_rel)
            l.append(tup)
        for val1 in l :
            if len(l) != 15 :
                tup = ('','','','','')
                l.append(tup)            
        return l
    
    def get_data5(self,employee):
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        doj = emp_browse.doj or ''
        doj = datetime.strptime(doj,"%Y-%m-%d")
        doj = doj.strftime("%d-%m-%Y")
        return doj
    
    def get_data6(self,employee):
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        com_address = emp_browse.company_id.name or ''
        street1 = emp_browse.company_id.street or ''
        street2 = emp_browse.company_id.street2 or ''
        city = emp_browse.company_id.city or ''
        state = emp_browse.company_id.state_id.name or ''
        zip = emp_browse.company_id.zip or ''
        country = emp_browse.country_id.name or ''
        
        com_address = com_address + ',' + ' ' + street1 + ' ' +  street2 + ' ' +  city + ' ' +  state + ' ' +  zip + ' ' +  country
        return com_address
    
    
class report_contractor_pf_nomination_form(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_pf_nomination_form'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_pf_nomination_form'
    _wrapped_report_class = contractor_pf_nomination_form
    

class contractor_appointment_letter(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_appointment_letter, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                "get_time":self.get_time,
                                "get_father":self.get_father,
                                "get_time1":self.get_time1,
                                  })  
    def get_time(self,doa):
        if doa: 
             date1 = datetime.strptime(doa,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1
#     
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
        
    def get_time1(self,doj):
        if doj: 
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1
     
    
class report_contractor_appointment_letter(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_appointment_letter'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_appointment_letter'
    _wrapped_report_class = contractor_appointment_letter
    
    
    
######### ===================================[[ Contractor Transfer ]] ============================================##########   
    
     
class contractor_transfer_letter(report_sxw.rml_parse):
     
    def __init__(self, cr, uid, name, context):
        super(contractor_transfer_letter, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                  "get_data":self.get_data,
                                  "get_company_check":self.get_company_check,
                                  "get_company":self.get_company,
                                  })
        
    def get_data(self,employee):
        transfer_date = ''
        query = self.cr.execute("select transfer_date from company_transfer_history where employee_id='"+str(employee.id)+"' order by transfer_date desc limit 1 ")
        temp =  self.cr.fetchall()
        if temp :
            transfer_date = temp[0][0]
            transfer_date = datetime.strptime(transfer_date,"%Y-%m-%d")
            transfer_date = transfer_date.strftime("%d-%m-%Y")
        return transfer_date        

    def get_company_check(self,employee):
        company_name = employee.company_id.name
        
        match1 = re.match( r'Designco', company_name)
        match2 = re.match( r'Lohia', company_name)
        if match1:
            company = 'Designco'
        elif match2:
            company = 'Lohia'
        else :
            company = company_name
        return company        

    def get_company(self,employee):
        old_company = ''
        new_company = ''
        company_lst = []
        query = self.cr.execute("select old_company_id,new_company_id from company_transfer_history where employee_id='"+str(employee.id)+"' order by transfer_date desc limit 1 ")
        temp =  self.cr.fetchall()
        if temp :
            old_company = self.pool.get('res.company').browse(self.cr, 1, temp[0][0]).name
            new_company = self.pool.get('res.company').browse(self.cr, 1, temp[0][1]).name
        company_lst.append(old_company)
        company_lst.append(new_company)
        return company_lst        

class report_contractor_transfer_letter(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_transfer_letter'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_transfer_letter'
    _wrapped_report_class = contractor_transfer_letter    
