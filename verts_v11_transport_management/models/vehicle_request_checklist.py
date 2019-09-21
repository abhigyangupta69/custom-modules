from odoo import api, fields, models, _



class VehicleRequestChecklist(models.Model):
    _name = 'vehicle.request.checklist'

    name = fields.Char(string='Checklist name')
    default = fields.Boolean(string='Default',default=True,help="Default Checklist will  populate in the Vehicle request form automatically, while Non-Default are optional, and user can add these manually")
    active = fields.Boolean(string='Active',default=True,help="Only active checklist will be available for use in the vehicle request form. Any old checklist,you should mark as Inactive")
    