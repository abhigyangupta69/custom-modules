from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, UserError, AccessError
from dateutil.relativedelta import *
from datetime import datetime



class RequestExecution(models.Model):
    _name = "request.execution"

    name = fields.Char("Execution No")
    execution_reason = fields.Text("Execution Reasons")
    transporter = fields.Many2one("res.partner",string="Transporter")
    vehicle_placed_on = fields.Char("Vehicle placed On")
    vehicle_type = fields.Many2one("vehicle.type",string="Vehicle Type")
    vehicle_no = fields.Char("Vehicle No")
    weight = fields.Float("Weight(K.g)")
    rate_per_kg = fields.Float("Rate Per(K.g)")
    amount = fields.Float("Amount")
    remarks = fields.Text("Remarks")
    # vehicle_request_ids = fields.Many2many('requests',string="Vehicle Req.")



    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('request.execution')
        vals.update({'name': seq})
        res = super(RequestExecution, self).create(vals)
        return res