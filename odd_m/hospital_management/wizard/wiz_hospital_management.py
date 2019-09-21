from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError, AccessError
import re
import base64
from odoo.exceptions import UserError
import os




class WizHospitalManagement(models.TransientModel):
    _name = "wiz.hospital.management"
    name = fields.Char('Name Of Patient')
# print report by button............
    @api.multi
    def print_report(self, data):
        print("=====data===============",data)          # qweb_id
        return self.env.ref('hospital_management.action_report_doctordetail').report_action(self, data={})





