from odoo import tools
from odoo import api, fields, models



class report_pf_contribution(models.AbstractModel):
    _name = 'report.hospital_management.report_pf_contribution'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['doctor.details'].browse([117])
        print("=========", docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'doctor.details',
            'docs': docs,
            'proforma': True
               }

class report_pf_admit(models.AbstractModel):
    _name = 'report.hospital_management.report_pf_admit'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['admit'].browse(docids)
        print("=========", docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'admit',
            'docs': docs,
            'proforma': True
               }

class report_pf_patientdetail(models.AbstractModel):
    _name = 'report.hospital_management.report_pf_patientdetail'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['patientdetails'].browse(docids)
        print("=========", docs)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'patientdetails',
            'docs': docs,
            'proforma': True
               }