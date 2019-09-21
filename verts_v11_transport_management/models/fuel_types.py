from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime


class FuelTypes(models.Model):
    _name = 'fuel.types'

    name = fields.Char('Fuel type')

