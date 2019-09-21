from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime


class FuelPriceList(models.Model):
    _name = 'fuel.price.list'

    fuel_type = fields.Many2one('fuel.types',string='Fuel Type')
    city = fields.Char("City")
    date = fields.Datetime("Date")
    price = fields.Char("Price")
    source = fields.Char("Source")

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            fuel_type = str(record.fuel_type.name) + ' ' + record.price
            result.append((record.id, fuel_type))
        return result