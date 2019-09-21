from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError, AccessError
import re
import base64
from odoo.exceptions import UserError
import os


class WizTransportationTrackingForm(models.TransientModel):
    _name = "wiz.transportation.tracking.form"
    move_date = fields.Date('Old Move-Date')
    new_move_date = fields.Date('New Move-Date')
    driver_name = fields.Char('Driver Name')
    new_driver_name = fields.Char('New Driver Name')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(WizTransportationTrackingForm, self).default_get(fields)
        transportation_tracking = self.env['transport.master'].browse(self._context.get('active_id'))
        res.update({'move_date': transportation_tracking.move_date,'new_move_date': transportation_tracking.move_date,'driver_name': transportation_tracking.driver_name, 'new_driver_name': transportation_tracking.driver_name})
        return res


  # create history by button.......
    def create_form(self):
        context = self._context or {}
        transport_lst = []
        transport = self.env['transport.master'].browse(self._context.get('active_id'))
        each = self.read(['move_date', 'new_move_date','driver_name','new_driver_name','user_id'])
        transport_lst.append([0, False, {'move_date': each[0]['move_date'], 'new_move_date': each[0]['new_move_date'],
                                         'driver_name': each[0]['driver_name'], 'new_driver_name': each[0]['new_driver_name'],
                                         'user_id': self.env.user.id,
                                         'transport_history':transport.id}])
        transport.write({'move_date': each[0]['new_move_date'],'driver_name': each[0]['new_driver_name'],
                         'history_detail': transport_lst})
        return {'type': 'ir.actions.act_window_close'}
