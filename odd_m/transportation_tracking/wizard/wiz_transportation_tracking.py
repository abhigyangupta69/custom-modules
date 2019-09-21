from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError, AccessError
import re
import base64
from odoo.exceptions import UserError
import os

class WizTransportationTracking(models.TransientModel):
    _name = "wiz.transportation.tracking"
    create_date = fields.Date('Create Date')
    move_date = fields.Date('Move Date')

# print report by button........
    @api.multi
    def print_report(self, data):

        return self.env.ref('transportation_tracking.action_report_transportmaster').report_action(self, data=data)
# print("=====data===============",data)
        # sr_lst = self.env['transport.master'].search([('create_date', '<=','2018-12-30'),
        #                                                      ('create_date','>=','2018-12-1')])
        # print("--------------------",sr_lst)
        # data = {'ids': sr_lst}
        # # return sr_lst
        # # # else:



















