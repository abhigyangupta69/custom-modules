from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime


class MaterialStatus(models.Model):
    _name = 'material.status'

    name = fields.Char('Material State')