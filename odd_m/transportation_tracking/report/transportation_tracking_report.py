from odoo import tools
from odoo import api, fields, models



class report_pf_contribution(models.AbstractModel):
    _name = 'report.transportation_tracking.report_pf_contribution'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['transport.master'].browse(docids)
        print("=========", docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'transport.master',
            'docs': docs,
            'proforma': True
        }

