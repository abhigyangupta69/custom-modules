from odoo import api, fields, models, SUPERUSER_ID, _
import base64, urllib
import os
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class DoctorDetails(models.Model):
    _name = "doctor.details"
    name_doc = fields.Char('Name Of Doctor')
    doc_id = fields.Char('Doctor-Id')
    qualification = fields.Selection([('Mm', 'M.B.B.S'), ('ms', 'M.S'), ('Others', 'Others')], string='Qualification', default='Others')
    department = fields.Selection([('cr','critical-care'),('dr','Diagnosis'),('qq','ENT'),])
    specialization = fields.Selection([('sir','surgon'),('new','neorologics'),('phy','Physlogist'), ('Others', 'Others')],string='Specilization')
    op_d = fields.Char('O.P.D')
    mob_no = fields.Char('Mob no')
    create_date = fields.Datetime('Date & Timing', default=fields.Datetime.now)
    mp = fields.Many2one('patientdetails',string='Additional')
    age = fields.Char(related='mp.age', string='Age', store=True,readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner")

    # print report by button............ # qweb_id(action_report_doctordetail)
    @api.multi
    def print_report(self):
        return self.env.ref('hospital_management.action_report_doctordetail').report_action(self)

    @api.model
    def create(self, vals) :
        vals.update({'specialization': 'Others'})
        res = super(DoctorDetails, self).create(vals)
        return res

    @api.multi
    def write(self, values):
        values['mob_no'] = 123
        res = super(DoctorDetails, self).write(values)
        return res


    @api.multi # function to create duplicate in  simple class without many2one/one2many....
    def create_duplicate(self):
        doctor_id = self.copy(default={'name_doc': '',
                                       'doc_id': self.doc_id,
                                       'qualification': self.qualification,
                                       'department': self.department,
                                       'specialization':self.specialization,
                                       'op_d':self.op_d,
                                       'mob_no':self.mob_no,
                                       'create_date':fields.Datetime.now,
                                       'mp':self.mp,
                                       'age':self.age,
                                        })
        model_str = ''
        view_ref = self.env['ir.model.data'].get_object_reference('hospital_management', 'hospital_management_form_view')
        view_id = view_ref and view_ref[1] or False,
        return {
                'type': 'ir.actions.act_window',
                'name': model_str,
                'res_model': 'doctor.details',
                'res_id': doctor_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id[0],
                'target': 'current',
                'nodestroy': True,
                }
 
class PatientDetails(models.Model):
    _name = "patientdetails"
    _rec_name="first_pat"
    name_pat = fields.Selection([('mr','Mr.'),('ms','Ms.'),('mrs','Mrs.')],string='Mr./Ms./Mrs.')
    first_pat = fields.Char('First Name')
    last_pat = fields.Char('Last Name')
    age = fields.Char('Age')
    relation_name = fields.Selection([('sin','single'),('marry','married')],string='Material Status')
    dicease = fields.Selection([('hp','Head Pain'),('cvp','Viral-Infactionin'),('cv','Genetic-Disorder')],string='Diseases')
    who_m = fields.Selection([('d','Dr. Chadda'),('dr','Dr. Gupta'),('di','Dr. Agarwal')],string='Whom To Meet')
    sp = fields.One2many('doctor.details','mp',string='Additional')
    patient_image = fields.Binary(string='Patient Image')
    partner_id = fields.Many2one('res.partner', string="Partner")
    one_many= fields.One2many('patient.detail.history','many_one',string='Patient-Detail')

    @api.model
    def create(self, vals) :
        res = super(PatientDetails, self).create(vals)
        print"=insert=in=one2many=using=create=method===="
        self.env['patient.detail.history'].create(
            {'many_one': res.id, 'first_pat': res.first_pat, 'new_name': res.first_pat,
             'relation_name': res.relation_name, 'new_relation': res.relation_name,
             'dicease': res.dicease, 'new_dicease': res.dicease,
             'who_m': res.who_m, 'new_meet': res.who_m})

    #     self.env['doctor.details'].create({'mp': res.id, 'name_doc': 'Abhigyan', 'doc_id': '99',
    #                                            'qualification': 'Mm','department': 'cr',
    #                                            'specialization': 'new','mob_no': '9997490035',
    #                                            'create_date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    #                                            'op_d': ''})

        return res

    @api.multi
    def write(self, values):
        print"=insert=in=one2many=using=create=method===="
        history_list = []
        for val in [self] :
            if 'first_pat' in values and values['first_pat'] and 'relation_name' in values and values['relation_name'] and 'dicease' in values and values['dicease'] and 'who_m' in values and values['who_m']:
                self.env['patient.detail.history'].create({'many_one': val.id, 'first_pat':val.first_pat,'new_name':values['first_pat'],
                                                   'relation_name': val.relation_name, 'new_relation': values['relation_name'],
                                                   'dicease': val.dicease, 'new_dicease': values['dicease'],
                                                   'who_m': val.who_m, 'new_meet': values['who_m']})
            elif 'first_pat' in values and values['first_pat'] and 'relation_name' in values and values['relation_name'] and 'dicease' in values and values['dicease'] :
                self.env['patient.detail.history'].create({'many_one': val.id, 'first_pat':val.first_pat,'new_name':values['first_pat'],
                                                   'relation_name': val.relation_name, 'new_relation': values['relation_name'],
                                                   'dicease': val.dicease, 'new_dicease': values['dicease'],
                                                   'who_m': val.who_m, 'new_meet': val.who_m})

            elif 'first_pat' in values and values['first_pat'] and 'relation_name' in values and values['relation_name']:
                self.env['patient.detail.history'].create({'many_one': val.id, 'first_pat':val.first_pat,'new_name':values['first_pat'],
                                                   'relation_name': val.relation_name, 'new_relation': values['relation_name'],
                                                   'dicease': val.dicease, 'new_dicease': val.dicease,
                                                   'who_m': val.who_m, 'new_meet': val.who_m})

            elif 'first_pat' in values and values['first_pat'] :
                self.env['patient.detail.history'].create({'many_one': val.id, 'first_pat':val.first_pat,'new_name':values['first_pat'],
                                                   'relation_name': val.relation_name, 'new_relation': val.relation_name,
                                                   'dicease': val.dicease, 'new_dicease': val.dicease,
                                                   'who_m': val.who_m, 'new_meet': val.who_m})


        res = super(PatientDetails, self).write(values)
        return res


    @api.multi  # function to create duplicate in relational class(many2one/one2many).....
    def create_duplicate(self):
        doc_lst = []
        for val1 in self.sp:
            doc_lst.append([0, False, {'name_doc': val1.name_doc, 'doc_id': val1.doc_id,
                                       'qualification':val1.qualification,'specialization':val1.specialization,
                                       'department': val1.department,'op_d':val1.op_d,'mob_no':val1.mob_no,
                                       'create_date':val1.create_date,'mp':val1.mp.id}])

        patient_id = self.copy(default={'name_pat': self.name_pat,
                                       'first_pat': self.first_pat,
                                       'last_pat': self.last_pat,
                                       'age': self.age,
                                       'relation_name':self.relation_name,
                                       'dicease':self.dicease,
                                       'who_m':self.who_m,
                                       'sp':doc_lst,
                                        })


class Admit(models.Model):
    _name = "admit"
    name_pat = fields.Char('Patient Name')
    bad_no = fields.Selection([('10','1'),('11','2'),('12','3'),('13','4'),('14','5')],string="Bed No")
    dicease = fields.Selection([('hp', 'Head Pain'), ('cvp', 'Viral-Infactionin'), ('cv', 'Genetic-Disorder')],string='Diseases')
    who_m = fields.Selection([('d','surgon'), ('dr','neorologics'), ('di','Physlogist')], string='Doctors')
    pat_relation = fields.Char('Patient Relative Name')
    em_no = fields.Char('Emergency no')
    image = fields.Binary('Image', compute='_get_image')
    image_url = fields.Char('Image URL', size=256)
    partner_id = fields.Many2one('res.partner', string="Partner")


    @api.model
    def _get_image(self):
        for each in self:
            try:
                if each.image_url:
                    (filename, header) = urllib.urlretrieve(
                        '/home/erp/workspace_abhi/erp/odoo11/odoo/abhi/Photo/Hospital/' + each['image_url'])
                    f = open(filename, 'rb')
                    each.image = f.read().encode('base64')
                else:
                    (filename, header) = urllib.urlretrieve(
                        'file://' + os.getcwd() + '/odoo/addons/hospital_management/images/default.jpg')
                    f =  open(filename, 'rb')
                    each.image = f.read().encode('base64')

            except:

                (filename, header) = urllib.urlretrieve(
                    'file://' + os.getcwd() + '/odoo/addons/hospital_management/images/default.jpg ')
                f = open(filename, 'rb')
                each.image = f.read().encode('base64')



class VehicleMaster(models.Model):
    _name = "vehicle.master"
    _rec_name ="vehicle_no"
    vehicle_no = fields.Char('Vehicle No')
    vehicle_model = fields.Char('Model')
    vehicle_type =fields.Selection([('bus', 'BUS'), ('van', 'VAN'), ('car', 'CAR'),('magic', 'MAGIC')],string='Vehicle Type')
    vehicle_avg = fields.Char('Vehicle Average')
    vehicle_driver = fields.Char('Driver Name')
    driver_mob = fields.Char('Mobile No')
    rel_no = fields.One2many('ambulance.detail','ambulance_no',string='Relation')




class AmbulanceDetail(models.Model):
    _name = "ambulance.detail"
    ambulance_no = fields.Many2one('vehicle.master', string='Ambulance NO')
    vehicle_driver = fields.Char('Driver Name')
    driver_mob = fields.Char('Mobile No')
    destination_distance = fields.Many2many('vehicle.master',string='Destination')


    @api.onchange('ambulance_no')
    def onchange_ambulance_no(self):
        if self.ambulance_no:
            self.vehicle_driver = self.ambulance_no.vehicle_driver
            self.driver_mob = self.ambulance_no.driver_mob



class PatientDetailHistory(models.Model):
    _name = "patient.detail.history"
    first_pat = fields.Char('OldFirst Name')
    new_name  = fields.Char('New First Name')
    relation_name = fields.Selection([('sin', 'single'), ('marry', 'married')], string='Old Material Status')
    new_relation = fields.Selection([('sin', 'single'), ('marry', 'married')], string='New Material Status')
    dicease = fields.Selection([('hp', 'Head Pain'), ('cvp', 'Viral-Infactionin'), ('cv', 'Genetic-Disorder')],
                               string='Old Diseases')
    new_dicease = fields.Selection([('hp', 'Head Pain'), ('cvp', 'Viral-Infactionin'), ('cv', 'Genetic-Disorder')],
                               string='New Diseases')
    who_m = fields.Selection([('d', 'Dr. Chadda'), ('dr', 'Dr. Gupta'), ('di', 'Dr. Agarwal')], string='old Meet')
    new_meet = fields.Selection([('d', 'Dr. Chadda'), ('dr', 'Dr. Gupta'), ('di', 'Dr. Agarwal')], string='New Meet')
    many_one = fields.Many2one('patientdetails',string='History of patient')














