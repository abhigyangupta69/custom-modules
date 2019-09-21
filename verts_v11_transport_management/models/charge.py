from odoo import api, fields, models, _



class Charge(models.Model):
    _name = 'charge'

    name = fields.Char("Charge Name")
    charge_type_id = fields.Many2one('charges.type',string='Charge Type')
