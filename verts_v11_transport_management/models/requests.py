from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, UserError, AccessError
from dateutil.relativedelta import *
from datetime import datetime


class Requests(models.Model):
    _name = "requests"


    name = fields.Char('Request No.')
    req_desc = fields.Char('Request Description')
    vehicle_required = fields.Datetime('Vehicle Required On')
    vehicle_req = fields.Char('Vehicle Request Type')
    erp_no = fields.Char('ERP PO Number ')
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    project_type = fields.Char('Project Type')
    project_name = fields.Char('Project ID/Name')
    source_location = fields.Char(string='Source Location')
    destination_location = fields.Char('Destination Location')
    pickup_location = fields.Many2one("location_types",string='Pickup Location Type ')
    destination_location_type = fields.Many2one('location_types',string='Destination Location type',default=lambda self: self.env.user)
    supplier = fields.Many2one('res.users',string='Pickup Partner/Supplier')
    customer = fields.Many2one('res.users',string='Destination Partner/Customer')
    pickup_address = fields.Text('Pickup Address ')
    destination_address = fields.Text('Destination Address')
    item_desc = fields.Text('Item Description')
    remarks = fields.Text('Remarks')
    supplier_invoice_value = fields.Float('Supplier Invoice Value')
    custom_invoice_no = fields.Char('Custom Invoice No')
    uom = fields.Selection([('feet','Feet'),('meters',"Meters")],string="UOM",default='feet')
    length = fields.Char('Length')
    width = fields.Char('Width')
    height = fields.Char('Height')
    weight_unit = fields.Selection([("kg","KG")],string='Weight Unit',default="kg")
    material_weight = fields.Float('Material Weigh')
    no_packages = fields.Integer('No. of Packages')
    vehicle_type = fields.Many2one("vehicle.type",string='Vehicle Type')
    under_utilization_reason = fields.Many2one("odc.reasons",string='ODC/Under utilization Reason')
    length_utilization = fields.Integer(string='Length Utilization (%)')
    width_utilization = fields.Integer(string='Width Utilization (%)')
    height_utilization = fields.Integer(string='Height Utilization (%)')
    weight_utilization = fields.Integer(string='Weight Utilization (%)')
    s_no = fields.Char('S.NO')
    checklist = fields.One2many('vehicle.request.checklist',"name",string="Check List")
    attached = fields.One2many("vehicle.request.checklist",'active',string='Attached')
    requested_on = fields.Datetime("Requested On")
    requestor = fields.Many2one('res.users', string='Requestor', default=lambda self: self.env.user)
    request_priority = fields.Char(string='Request Priority')
    items = fields.Char("Items")
    stage = fields.Selection([('Pending','Pending'),('Done','Done')],string="Stage")
    checklist_line = fields.One2many("checklist","request_id",string="Check list Line")
    priority_from_date = fields.Date("Priority From Date")
    priority_to_date = fields.Datetime("Priority To Date")
    priority_day = fields.Integer(string="Priority Days")
    state = fields.Selection([("draft","Draft"),("send_for_approval","Send For Approval"),("approved","Approved"),("confirm","Confirm")],string="State",default="draft")
    confirm_on_date = fields.Datetime("confirm on date")
    priority_id = fields.Many2one('request.priority',string="Priority")

    @api.multi
    def print_report(self):
        return self.env.ref('verts_v11_transport_management.action_report_vehicle_request').report_action(self)

    @api.multi
    def action_test_button(self):
        if self.state == "draft":
            self.state = "confirm"
            self.requested_on = datetime.now()
            self.confirm_on_date = datetime.now()
            self.vehicle_required = datetime.now()
            req_date = datetime.strptime(self.requested_on, '%Y-%m-%d %H:%M:%S')
            requested_on_data = req_date.strftime("%H:%M")
            if requested_on_data < '04:00':
                self.priority_from_date = self.confirm_on_date
            else:
                self.priority_from_date = datetime.now() + relativedelta(days=+1)
            self.priority_to_date = self.vehicle_required

            print("XXXXXXXXXXXXXXXXXXXXX",self.priority_from_date,self.priority_to_date,self.priority_day)
        return True


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('requests')
        vals.update({'name': seq})
        res = super(Requests,self).create(vals)
        return res

    @api.multi
    def action_approval(self):
        if self.checklist_line:
            for val in self.checklist_line:
                if val.status == 'not_req' or not val.status:
                    raise ValidationError(_('Your Documents are not complete. Please complete those and update status'))

                elif val.status == "pending":
                    raise ValidationError(_('Your Documents are in pending staze'))
        else:
            if not self.checklist_line:
                raise ValidationError(_('Here is not any record in checklist.Please insert the record'))

        return True


class Checklist(models.Model):
    _name = 'checklist'
    request_id = fields.Many2one("requests",string="Request")
    s_no = fields.Char(string='S.NO')
    checklist = fields.Boolean(string='Checklist')
    status = fields.Selection([("draft","Draft"),("pending","Pending"),("not_req","Not Required")],string="Status")


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('checklist')
        vals.update({'s_no': seq})
        res = super(Checklist, self).create(vals)
        return res
















