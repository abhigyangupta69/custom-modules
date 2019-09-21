from odoo import api, fields, models, _

class VehicleType(models.Model):
    _name = 'vehicle.type'

    name = fields.Char('Vehicle Type')
    axles_no = fields.Char('No. of Axles')
    vehicle_weight = fields.Float('Gross Vehicle Weight (KGs)')
    dimensions_unit = fields.Selection([('feet',"Feet"),('metres','Metres')], string='Dimensions Units', default='feet')
    capacity_uom = fields.Many2one('product.uom', string='Capacity UoM')
    reg_cap = fields.Float('Regular Capacity')
    min_cap = fields.Float('Minimum Capacity')
    max_cap = fields.Float('Max Capacity ')
    len_regular_size = fields.Integer("len.Regular Size")
    wid_regular_size = fields.Integer("WidRegular Size")
    height_regular_size = fields.Integer("Height Regular Size")
    min_len_size = fields.Integer("Min lenght Size for cargo")
    min_wid_size = fields.Integer("Min Width Size for cargo")
    min_height_size = fields.Integer("Min Height Size for cargo")
    max_len_size = fields.Integer("max Lenght Size for cargo")
    max_wid_size = fields.Integer("max Width Size for cargo")
    max_height_size = fields.Integer("max height Size for cargo")



