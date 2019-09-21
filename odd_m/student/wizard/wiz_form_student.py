from odoo import api, fields, models, SUPERUSER_ID
import re
import base64
from odoo.exceptions import UserError
import os




class WizStudentForm(models.TransientModel):
    _name="wiz.student.form"

    exam_time = fields.Date('Exam Time')
    slot_name = fields.Char('Slot', size=16)
    select_state = fields.Selection([('u.p', 'Uttar Pradesh'), ('u.k', 'Uttrakhand'), ('a.p', 'Andhra pradesh')],string='Select-State')

    stu_db = fields.Date('Date Of Birth')
    stu_gender = fields.Selection([('male', 'Male'), ('fmale', 'Female'), ('yymale', 'Others')], string='Gender')
    mob_no = fields.Char('Mob no')
    exam_payment = fields.Selection([('draft', 'Draft'), ('sent', 'Paytm'), ('sale', 'PhonePe'), ('cancel', 'Cancel')],
                                    string='Exam Payment')

    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(WizStudentForm, self).default_get(fields)
        student = self.env['exam.detail'].browse(self._context.get('active_id'))
        res.update({'exam_time': student.exam_time, 'slot_name': student.slot_name, 'select_state': student.select_state,'stu_db': student.stu_db,'stu_gender': student.stu_gender,'mob_no': student.mob_no,'exam_payment': student.exam_payment})
        return res


    def create_form(self):
        context = self._context or {}
        stud = self.env['exam.detail'].browse(self._context.get('active_id'))
        each = self.read(['exam_time', 'slot_name','select_state','stu_db','stu_gender','mob_no','exam_payment'])
        stud.write({'exam_time': each[0]['exam_time'], 'slot_name': each[0]['slot_name'], 'select_state': each[0]['select_state'],'stu_db': each[0]['stu_db'],'stu_gender': each[0]['stu_gender'],'mob_no': each[0]['mob_no'],'exam_payment': each[0]['exam_payment']})
        return {'type': 'ir.actions.act_window_close'}

