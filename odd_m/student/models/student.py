from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
import base64, urllib
import os


class STUDENT(models.Model):
    _name = "student"

    name = fields.Char('Name')
    middle_name = fields.Char('Middle-Name')
    last_name = fields.Char('Last-Name')
    father_name = fields.Char('Father-Name')
    mother_name = fields.Char('Mother-Name')
    section = fields.Selection([('cs','CSE'), ('it','IT')],string='Section')
    class_id = fields.Char('Id')
    gender = fields.Selection([('male','Male'), ('fmale','Female'), ('yymale','Others')],string='Gender')
    mob_no = fields.Char('Mob no')
    acadmic_payment = fields.Selection([('draft', 'Draft'), ('sent', 'Paytm'), ('sale', 'PhonePe'), ('cancel', 'Cancel')], string='Acadmic Payment')
    payment_date = fields.Date('End Date')
    college_line=fields.One2many('college.detail','student_id',string='Colleges')


class CollegeDetail(models.Model):
    _name = "college.detail"

    name_clg = fields.Char('Name Of College')
    name_p = fields.Char('Name')
    last_name = fields.Char('Last-Name')
    father_name = fields.Char('Father-Name')
    section = fields.Selection([('cs','CSE'), ('it','IT')],string='Section')
    class_id = fields.Char('Id')
    gender = fields.Selection([('male','Male'), ('fmale','Female'), ('yymale','Others')],string='Gender')
    mob_no = fields.Char('Mob no')
    acadmic_payment = fields.Selection([('draft', 'Draft'), ('sent', 'Paytm'), ('sale', 'PhonePe'), ('cancel', 'Cancel')], string='Acadmic Payment')
    student_id=fields.Many2one('student',string='Faculty')
    image = fields.Binary('Image', compute='_get_image')
    image_url = fields.Char('Image URL', size=256)


    @api.model
    def _get_image(self):
        for each in self:
            try:
                if each.image_url:
                    (filename, header) = urllib.urlretrieve(
                        '/home/erp/workspace_abhi/erp/odoo11/odoo/abhi/Photo/Stud/' + each['image_url'])
                    f = open(filename, 'rb')
                    each.image = f.read().encode('base64')
                else:
                    (filename, header) = urllib.urlretrieve(
                        'file://' + os.getcwd() + '/odoo/addons/student/images/default.jpg')
                    f = open(filename, 'rb')
                    each.image = f.read().encode('base64')

            except:

                (filename, header) = urllib.urlretrieve(
                    'file://' + os.getcwd() + '/odoo/addons/student/images/default.jpg ')
                f = open(filename, 'rb')
                each.image = f.read().encode('base64')


class BookIssueDetail(models.Model):

    _name = "bookissuedetail"
    name_book= fields.Char('Name Of Book')
    issue_date = fields.Date('Issue-Date')
    section_book= fields.Selection([('cs','CSE'), ('it','IT'),('ec','EC'),('en','EN'),('bt','BT')],string='Book Section')
    stu_id = fields.Char(' Student Id')
    stu_gender = fields.Selection([('male','Male'), ('fmale','Female'), ('yymale','Others')],string='Gender')
    mob_no = fields.Char('Mob no')
    book_payment = fields.Selection([('draft', 'Draft'), ('sent', 'Paytm'), ('sale', 'PhonePe'), ('cancel', 'Cancel')], string='Book Delay Payment')
    re_s = fields.One2many('acadmicdetail','l_s',string='Add info')
        
    
class AcadmicDetail(models.Model):
    _name = "acadmicdetail"
    g_m = fields.Char('Graduation-Marks')    
    g_b = fields.Date('Graduation-board')
    h_m = fields.Char('Highschool-Marks')    
    h_b = fields.Date('Highschoolo-board')
    select_state= fields.Selection([('u.p','Uttar Pradesh'), ('u.k','Uttrakhand'),('a.p','Andhra pradesh')],string='Select-State')
    stu_db = fields.Date('Date Of Birth')
    stu_gender = fields.Selection([('male','Male'), ('fmale','Female'), ('yymale','Others')],string='Gender')
    mob_no = fields.Char('Mob no')
    e_payment = fields.Selection([('draft', 'Draft'), ('sent', 'Paytm'), ('sale', 'PhonePe'), ('cancel', 'Cancel')], string='Exam Payment')
    l_s=fields.Many2one('bookissuedetail',string='YO')






class FeeSubmission(models.Model):
    _name = "feesubmission"

    name = fields.Char('Name', size=16)
    create_date = fields.Datetime('Payment Date', default=fields.Datetime.now)
    active_payment = fields.Boolean(string='Active Payment', default=True)
    old_sequence = fields.Integer(string='Old Payment')
    new_sequence = fields.Integer(string='New Payment')






class ExamDetail(models.Model):
    _name = "exam.detail"
    exam_time = fields.Date('Exam Time')
    slot_name = fields.Char('Slot', size=16)
    select_state = fields.Selection([('u.p', 'Uttar Pradesh'), ('u.k', 'Uttrakhand'), ('a.p', 'Andhra pradesh')],
                                    string='Select-State')
    stu_db = fields.Date('Date Of Birth')
    stu_gender = fields.Selection([('male', 'Male'), ('fmale', 'Female'), ('yymale', 'Others')], string='Gender')
    mob_no = fields.Char('Mob no')
    exam_payment = fields.Selection([('draft', 'Draft'), ('sent', 'Paytm'), ('sale', 'PhonePe'), ('cancel', 'Cancel')],
                                 string='Exam Payment')



class Qualify(models.Model):
    _name="qualify"

    q_b = fields.Selection([('bt' , 'B.Tech'),('mt' , 'M.Tech'),('pd' , 'P.hd')],string="Qualification")
    sl_name = fields.Char('Select Company', size=16)
    select_state = fields.Selection([('u.p', 'Uttar Pradesh'), ('u.k', 'Uttrakhand'), ('a.p', 'Andhra pradesh')],
                                    string='Select-State')
    stu_db = fields.Date('D. O. B')
    st_gender = fields.Selection([('male', 'Male'), ('fmale', 'Female'), ('yymale', 'Others')], string='Gender')
    mobile_no = fields.Char('Mobile  no')
    e_payment = fields.Selection([('draft', 'Net Banking'), ('sent', 'Paytm'), ('sale', 'PhonePe'), ('cancel', 'Cancel')],
                                    string='Exam Payment')
    rel_ation=fields.Many2one('employement',string='relation')



class Employement(models.Model):
    _name="employement"
    no_j=fields.Char('JoB Title')
    Ty_j=fields.Selection([('dv','Developer'),('ts','Tester'),('bd','Bussiness Developement'),('ac',' Software Arctact')], string='Select Domain')
    ex_p=fields.Selection([('0','0 Years'),('1','1+ years'),('2','2+ years'),('3','3+ years')],string='Experience')
    notice_p=fields.Selection([('0','1 month'),('1','2 month'),('m','more')], string='Notice Period')
    applied_job = fields.One2many('qualify', 'rel_ation', string='Summary Data')











