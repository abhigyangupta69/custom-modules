import time
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime
from openerp.tools.translate import _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

#                            EMPLOYEE MASTER REPORT

class employee_master_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(employee_master_report, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                "get_time_appointment":self.get_time_appointment,
                                "get_father_appointment":self.get_father_appointment,
                                "get_time_confirmation":self.get_time_confirmation,
                                "get_father_confirmation":self.get_father_confirmation,
                                "get_father_medical":self.get_father_medical,
                                "get_doj_form16":self.get_doj_form16,
                                "get_form16_data":self.get_form16_data,
                                "get_time_form11":self.get_time_form11,
                                "get_data_formf":self.get_data_formf,
                                "get_data1_nomination":self.get_data1_nomination,
                                "get_data2_nomination":self.get_data2_nomination,
                                "get_data3_nomination":self.get_data3_nomination,
                                "get_data4_nomination":self.get_data4_nomination,
                                "get_data5_nomination":self.get_data5_nomination,
                                "get_data6_nomination":self.get_data6_nomination,
                                "get_birthday_record":self.get_birthday_record,
                                "get_detail_record":self.get_detail_record,
                                "get_increment_record":self.get_increment_record,
                                "get_promotion_record":self.get_promotion_record,
                                "get_father_form11":self.get_father_form11,
                                "get_dob":self.get_dob,
                                "get_passport_form11":self.get_passport_form11,
                                "get_aadhaar_no_form11":self.get_aadhaar_no_form11,
                                "get_pan_no_form11":self.get_pan_no_form11,
                                "get_bank_acc_no_form11":self.get_bank_acc_no_form11,
                                "get_time_appointment1":self.get_time_appointment1,
                                
                                  })
        
    def get_time_appointment(self,doa):
        if doa: 
             date1 = datetime.strptime(doa,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1

    def get_time_appointment1(self,doj):
        if doj: 
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1

#     
    def get_father_appointment(self,emp_id):
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
    
    def get_time_confirmation(self,doj):
         if doj :
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             new_date = (date1 + relativedelta(months=+6)).strftime('%d-%m-%Y')
             return new_date
         
    def get_father_confirmation(self,emp_id):
        res=' '
        qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
        self.cr.execute(qry)
        temp = self.cr.fetchall()
        if temp:
            res = temp[0][0]
        else:
            res = ' '    
        return res 
    
    def get_father_medical(self,emp_id):
        res=''
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res 
    
    def get_form16_data(self,emp_id):
        l = []
        tup = ()
        nom_name = ''
        nom_rel = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,emp_id)
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.nom_tick == True :
                    nom_name = val.name.upper()
                    nom_rel = val.relation.upper()
                    break
        tup = (nom_name,nom_rel)
        l.append(tup)
        return l
           
        
    def get_doj_form16(self,doj): 
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
        return date1 
    
    
    def get_bank_acc_no_form11(self,verf_id,emp_id):
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

    def get_aadhaar_no_form11(self,verf_id,emp_id):
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
    
    def get_pan_no_form11(self,verf_id,emp_id):
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
        
        
    def get_passport_form11(self,verf_id,emp_id):
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

    def get_time_form11(self,doj):
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1        

    def get_dob(self,birthday):
        if birthday:
             date1 = datetime.strptime(birthday,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1        
        
    def get_father_form11(self,emp_id,fam_id):
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
      
        
    def get_father_form11(self,emp_id,fam_id):
        res=' '
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
    
    
    def get_data_formf(self,emp_id,family_id):
        res={}
        if family_id :
            qry = "select name,relation,age,share from family where nom_tick=True and employee_id='"+str(emp_id)+"' order by age"
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp
            else:
                res = [('','','','')]    
        return res 
    
    def get_data1_nomination(self,employee):
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
    
    def get_data2_nomination(self,employee):
        l = []
        tup = ()
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        address1 = emp_browse.permanent_add or ''
        address2 = emp_browse.local_add or ''
        tup = (address1, address2)
        l.append(tup)
        return l
    
    def get_data3_nomination(self,employee):
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
    
    def get_data4_nomination(self,employee):
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
    
    def get_data5_nomination(self,employee):
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        doj = emp_browse.doj or ''
        doj = datetime.strptime(doj,"%Y-%m-%d")
        doj = doj.strftime("%d-%m-%Y")
        return doj
    
    def get_data6_nomination(self,employee):
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
                    
                        

class report_employee_master_report(osv.AbstractModel):
    _name = 'report.hr_compliance.report_employee_master_report'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_employee_master_report'
    _wrapped_report_class = employee_master_report









#                            CONTRACTOR MASTER REPORT

class contractor_master_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(contractor_master_report, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                "get_time_appointment":self.get_time_appointment,
                                "get_father_appointment":self.get_father_appointment,
                                "get_time_confirmation":self.get_time_confirmation,
                                "get_father_confirmation":self.get_father_confirmation,
                                "get_father_medical":self.get_father_medical,
                                "get_doj_form16":self.get_doj_form16,
                                "get_form16_data":self.get_form16_data,
                                "get_time_form11":self.get_time_form11,
                                "get_data_formf":self.get_data_formf,
                                "get_data1_nomination":self.get_data1_nomination,
                                "get_data2_nomination":self.get_data2_nomination,
                                "get_data3_nomination":self.get_data3_nomination,
                                "get_data4_nomination":self.get_data4_nomination,
                                "get_data5_nomination":self.get_data5_nomination,
                                "get_data6_nomination":self.get_data6_nomination,
                                "get_birthday_record":self.get_birthday_record,
                                "get_detail_record":self.get_detail_record,
                                "get_increment_record":self.get_increment_record,
                                "get_promotion_record":self.get_promotion_record,
                                "get_father_form11":self.get_father_form11,
                                "get_dob":self.get_dob,
                                "get_passport_form11":self.get_passport_form11,
                                "get_aadhaar_no_form11":self.get_aadhaar_no_form11,
                                "get_pan_no_form11":self.get_pan_no_form11,
                                "get_bank_acc_no_form11":self.get_bank_acc_no_form11,
                                "get_time_appointment1":self.get_time_appointment1,
                                
                                  })
        
    def get_time_appointment(self,doa):
        if doa: 
             date1 = datetime.strptime(doa,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1

    def get_time_appointment1(self,doj):
        if doj: 
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1

#     
    def get_father_appointment(self,emp_id):
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
    
    def get_time_confirmation(self,doj):
         if doj :
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             new_date = (date1 + relativedelta(months=+6)).strftime('%d-%m-%Y')
             return new_date
         
    def get_father_confirmation(self,emp_id):
        res=' '
        qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
        self.cr.execute(qry)
        temp = self.cr.fetchall()
        if temp:
            res = temp[0][0]
        else:
            res = ' '    
        return res 
    
    def get_father_medical(self,emp_id):
        res=''
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res 
    
    def get_form16_data(self,emp_id):
        l = []
        tup = ()
        nom_name = ''
        nom_rel = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,emp_id)
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.nom_tick == True :
                    nom_name = val.name.upper()
                    nom_rel = val.relation.upper()
                    break
        tup = (nom_name,nom_rel)
        l.append(tup)
        return l
           
        
    def get_doj_form16(self,doj): 
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
        return date1 
    
    
    def get_bank_acc_no_form11(self,verf_id,emp_id):
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

    def get_aadhaar_no_form11(self,verf_id,emp_id):
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
    
    def get_pan_no_form11(self,verf_id,emp_id):
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
        
        
    def get_passport_form11(self,verf_id,emp_id):
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

    def get_time_form11(self,doj):
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1        

    def get_dob(self,birthday):
        if birthday:
             date1 = datetime.strptime(birthday,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
             return date1        
        
    def get_father_form11(self,emp_id,fam_id):
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
      
        
    def get_father_form11(self,emp_id,fam_id):
        res=' '
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
    
    
    def get_data_formf(self,emp_id,family_id):
        res={}
        if family_id :
            qry = "select name,relation,age,share from family where nom_tick=True and employee_id='"+str(emp_id)+"' order by age"
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp
            else:
                res = [('','','','')]    
        return res 
    
    def get_data1_nomination(self,employee):
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
    
    def get_data2_nomination(self,employee):
        l = []
        tup = ()
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        address1 = emp_browse.permanent_add or ''
        address2 = emp_browse.local_add or ''
        tup = (address1, address2)
        l.append(tup)
        return l
    
    def get_data3_nomination(self,employee):
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
    
    def get_data4_nomination(self,employee):
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
    
    def get_data5_nomination(self,employee):
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,employee.id)
        doj = emp_browse.doj or ''
        doj = datetime.strptime(doj,"%Y-%m-%d")
        doj = doj.strftime("%d-%m-%Y")
        return doj
    
    def get_data6_nomination(self,employee):
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
                    
                        

class report_contractor_master_report(osv.AbstractModel):
    _name = 'report.hr_compliance.report_contractor_master_report'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_contractor_master_report'
    _wrapped_report_class = contractor_master_report
    
    
    
    
    
    
    
#        ============       Neem  Trainee  MASTER REPORT   ====================

class neem_trainee_master_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(neem_trainee_master_report, self).__init__(cr, 1, name, context=context)
        self.localcontext.update({
                                "get_father_medical":self.get_father_medical,
                                "get_doj_form16":self.get_doj_form16,
                                "get_form16_data":self.get_form16_data,
                               
                                
                                  })
        
   
    
    def get_father_medical(self,emp_id):
        res=''
        if emp_id:
            qry = "select name from family where relation='Father' and employee_id='"+str(emp_id)+"'  "
            self.cr.execute(qry)
            temp = self.cr.fetchall()
            if temp:
                res = temp[0][0]
            else:
                res = ' '    
        return res 
    
    def get_form16_data(self,emp_id):
        l = []
        tup = ()
        nom_name = ''
        nom_rel = ''
        emp_browse = self.pool.get('hr.employee').browse(self.cr,1,emp_id)
        if emp_browse.family_id :
            for val in emp_browse.family_id :
                if val.nom_tick == True :
                    nom_name = val.name.upper()
                    nom_rel = val.relation.upper()
                    break
        tup = (nom_name,nom_rel)
        l.append(tup)
        return l
           
        
    def get_doj_form16(self,doj): 
        if doj:
             date1 = datetime.strptime(doj,"%Y-%m-%d")
             date1 = date1.strftime("%d-%m-%Y")
        return date1 
    
    
    
                        

class report_neem_trainee_master_report(osv.AbstractModel):
    _name = 'report.hr_compliance.report_neem_trainee_master_report'
    _inherit = 'report.abstract_report'
    _template = 'hr_compliance.report_neem_trainee_master_report'
    _wrapped_report_class = neem_trainee_master_report    
