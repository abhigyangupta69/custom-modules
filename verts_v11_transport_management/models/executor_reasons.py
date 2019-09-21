from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime


class ExecutorReasons(models.Model):
    _name = 'executor.reasons'

    name = fields.Char('Execute Reason')