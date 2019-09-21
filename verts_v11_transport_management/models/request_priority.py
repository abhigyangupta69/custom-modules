from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime

class RequestPriority(models.Model):
    _name = 'request.priority'

    name = fields.Char(string='Name',help="Location type is used to identify the category of the location for checking the appropriate category of master for the source or destination address")
    days_required = fields.Char('Days from the required Date')
