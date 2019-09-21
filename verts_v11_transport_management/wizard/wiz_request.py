from odoo import api,fields, models,_


class WizRequest(models.TransientModel):
    _name = "wiz.request"

    erp_no = fields.Char('ERP PO Number ')
    vehicle_req = fields.Char('Vehicle Request Type')
    source_location = fields.Char(string='Source Location')
    destination_location = fields.Char('Destination Location')
    item_desc = fields.Text('Item Description')
    remarks = fields.Text('Remarks')

    @api.model
    def default_get(self, val):
        res = super(WizRequest, self).default_get(val)
        req = self.env['requests'].browse(self._context.get('active_id'))
        res.update({'erp_no': req.erp_no, 'vehicle_req': req.vehicle_req, 'source_location': req.source_location,'destination_location': req.destination_location,'item_desc': req.item_desc,'remarks': req.remarks})
        return res

    def update_form(self):
        req = self.env['requests'].search([])
        each = self.read(['erp_no', 'vehicle_req','source_location','destination_location','item_desc','remarks'])
        req.write({'erp_no': each[0]['erp_no'], 'vehicle_req': each[0]['vehicle_req'], 'source_location': each[0]['source_location'],'destination_location': each[0]['destination_location'],'item_desc': each[0]['item_desc'],'remarks': each[0]['remarks']})
        return {'type': 'ir.actions.act_window_close'}
