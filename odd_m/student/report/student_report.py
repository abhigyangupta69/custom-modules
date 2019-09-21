from odoo import tools
from odoo import api, fields, models



class report_of_studentdetail(models.AbstractModel):
    _name = 'report.student.report_of_studentdetail'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['feesubmission'].browse(docids)
        print("=========", docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'feesubmission',
            'docs': docs,
            'proforma': True
               }

