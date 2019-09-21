from odoo import api, fields, models, _

class LocationTypes(models.Model):
    _name = 'location_types'

    name = fields.Char(string='Location Type',help="Location type is used to identify the category of the location for checking the appropriate category of master for the source or destination address")
