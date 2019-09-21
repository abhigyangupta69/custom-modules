from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date
from dateutil.relativedelta import *
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment = fields.Float("Payment")
    payment_records = fields.Char("Payment Record")


class AddNew(models.Model):
    _name = 'add.new'
    _rec_name = 'seq_name'
    payment = fields.Float("Payment")
    payment_records = fields.Char(string="Payment Record")
    pay_role_line = fields.One2many('pay.role','add_new_id',string="More")
    seq_name = fields.Char('Seq. No')
    state = fields.Selection([('Draft', 'Draft'), ('Done', 'Done')],string='State', default='Draft')
    no_days = fields.Float("No. Days")
    first_date = fields.Datetime("First Date")
    add_month = fields.Integer("Add Months")
    date_output = fields.Datetime("Date output")

    @api.model
    def create(self, vals):
        res = super(AddNew, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('add.new')
        print("11111111111111",self,vals)
        res['seq_name'] = seq
        res["payment_records"] = vals['payment'] / vals['no_days']
        return res


    @api.multi
    def action_confirm(self):
        if self.state == "Draft":
            self.state = "Done"
        return True

    @api.onchange("no_days")
    def onchange_payment(self):
        if self.payment or self.no_days:
            self.payment_records = self.payment / self.no_days

    @api.onchange("first_date",'add_month')
    def onchange_date_output(self):
        if self.first_date or self.add_month:
            self.date_output = datetime.now() + relativedelta(months=self.add_month)

    @api.multi
    def write(self, vals):
       # res = super(AddNew, self).write(vals)
        if 'payment' in vals and vals['payment'] and 'no_days' in vals and vals['no_days']:
            vals["payment_records"] = vals['payment'] / vals['no_days']
        elif 'no_days' in vals and vals['no_days']:
            vals["payment_records"] = self.payment / vals['no_days']
        elif 'payment' in vals and vals['payment']:
            vals["payment_records"] = vals['payment'] / self.no_days
        return super(AddNew, self).write(vals)


    # @api.depends('no_days')
    # def _compute_payment(self):
    #     if (self.payment > 0) or (self.no_days > 0):
    #         self.update({'payment_records': self.payment / self.no_days})
    #     else:
    #         self.update({'payment_records': self.payment})

class PayRole(models.Model):
    _name = 'pay.role'
    add_new_id = fields.Many2one('add.new', string='Additional')
    name = fields.Char('Name Of Merchant')
    merchant_id = fields.Char('Merchant-Id')
    payment_type = fields.Selection([('paytm', 'Paytm'), ('phonepe', 'Phonepe'), ('banking', 'Banking'), ])
    mob_no = fields.Char('Mob no')
    payment_date = fields.Datetime('Payment Date', default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', string="Partner")





