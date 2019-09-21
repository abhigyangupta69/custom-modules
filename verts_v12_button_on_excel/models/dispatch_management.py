from odoo import api,fields, models,_
import xlrd
from io import BytesIO
import base64
from odoo.exceptions import ValidationError, UserError, AccessError

class ExcelButton(models.Model):
    _name = 'excel.button'

    xls_file = fields.Binary("Add File")

    @api.multi
    def upload_product(self):
        for self_obj in self:
            data_decode = self_obj.xls_file
            if not data_decode:
                raise UserError(_('Please Choose The File!'))
            val = base64.decodestring(data_decode)
            fp = BytesIO()
            fp.write(val)
            wb = xlrd.open_workbook(file_contents=fp.getvalue())
            wb.sheet_names()
            sheet_name = wb.sheet_names()
            sh = wb.sheet_by_name(sheet_name[0])
            n_rows = sh.nrows
            for row in range(1, n_rows):
                dict = {}
                if sh.row_values(row)[0]:
                    dispatch_id = int(sh.row_values(row)[0])
                    remarks = sh.row_values(row)[1]
                    dispatch_obj = self.env['dispatch.management'].search([('dispatch_id', '=', dispatch_id)])

                    dispatch_obj.write({
                        'remarks': remarks,
                    })
                    amount = sh.row_values(row)[2]
                    for line in dispatch_obj.dispatch_line:

                        line.write({
                            'amount':amount
                        })
                self._cr.commit()
        return True




