from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime

class VehicleModels(models.Model):
    _name = 'vehicle.models'
    model_name = fields.Char("Model Name")
    brand_name = fields.Many2one('vehicle.brands',string='Brand Name')
    standard_kmp = fields.Float("Standard Transit KMs per day")
