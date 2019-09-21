from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime



class VehicleBrands(models.Model):
    _name = 'vehicle.brands'
    name = fields.Char(string="Brand Name")