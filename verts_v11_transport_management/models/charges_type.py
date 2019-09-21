from odoo import api, fields, models, _

class ChargesType(models.Model):
    _name = 'charges.type'

    name = fields.Char("Charges Type")