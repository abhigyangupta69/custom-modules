import xlwt
from odoo import api,fields, models,_
from xlwt import XFStyle, Font
import base64
from io import StringIO, BytesIO
from datetime import datetime

class VehicleReport(models.TransientModel):
    _name = "vehicle.report"

    from_date = fields.Datetime("From Date")
    to_date = fields.Datetime("To Date")

    @api.multi
    def button_print_vehicle_report(self):
        filename = 'Vehicle Report Import.xls'
        string = 'Vehicle Report.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        style = XFStyle()
        fnt = Font()
        fnt.colour_index = 0x36
        fnt.bold = True
        fnt.width = 256 * 30
        style.font = fnt
        style1 = XFStyle()
        fnt = Font()
        fnt.colour_index = 0x86
        fnt.bold = True
        fnt.width = 256 * 30
        style1.font = fnt

        worksheet.write_merge(0, 1, 2, 3, "Vehicle Report", xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))
        worksheet.write(2, 0, 'Sequence No', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 1, 'ERP PO Number', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 2, 'Project Type', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 3, 'Project ID/Name', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 4, 'Source Location', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 5, 'Destination Location', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 6, 'Pickup Address', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 7, 'priority_from_date', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 8, 'Priority_to_date', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))

        # worksheet.write(3, 0, self.erp_no)

        a = 3
        cus_inv_obj = self.env['requests'].search([('priority_from_date','=',self.from_date),('Priority_to_date', '=', self.to_date)])
        print("XXXXXXXXXXXXXXXXXX",self.from_date,self.to_date)
        # print ("WWWWWWWWWWWWWWWWW",cus_inv_obj(2,3))
        for rec in cus_inv_obj:
            worksheet.write(a, 0, rec.name)
            worksheet.write(a, 1, rec.erp_no)
            worksheet.write(a, 2, rec.project_type)
            worksheet.write(a, 3, rec.project_name)
            worksheet.write(a, 4, rec.source_location)
            worksheet.write(a, 5, rec.destination_location)
            worksheet.write(a, 6, rec.pickup_address)
            worksheet.write(a, 7, rec.priority_from_date)
            worksheet.write(a, 8, rec.Priority_to_date)

            a += 1

        fp = BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_id = self.env['view.report.veichel'].create({'file_name': out, 'datas_fname': filename})
        return {
            'res_id': view_report_id.id,
            'name': 'Tally Import Format',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'view.report.veichel',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


class view_report(models.TransientModel):
    _name = 'view.report.veichel'

    datas_fname = fields.Char('File Name', size=256)
    file_name = fields.Binary('Report')

