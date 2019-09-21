from odoo import tools
from odoo import api, fields, models



class report_of_shop_keeper(models.AbstractModel):
    _name = 'report.shop_keeper.report_of_shop_keeper'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['shipping.details'].browse(docids)
        print("=========", docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'shipping.details',
            'docs': docs,
            'proforma': True
        }

class report_of_customer_feedback(models.AbstractModel):
    _name = 'report.shop_keeper.report_of_customer_feedback'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['customer.detail'].browse(docids)
        print("=========", docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'customer.detail',
            'docs': docs,
            'proforma': True
        }
