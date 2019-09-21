from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime


class OdcReasons(models.Model):
    _name = 'odc.reasons'

    name = fields.Char('ODC/Under Utilization Reasons')