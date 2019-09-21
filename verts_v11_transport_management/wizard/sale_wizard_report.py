import xlwt
from odoo import api,fields, models,_
from xlwt import XFStyle, Font
import base64
from io import StringIO, BytesIO
from datetime import datetime
from odoo.exceptions import ValidationError, UserError, AccessError

class SaleWizardReport(models.TransientModel):
    _name = "sale.wizard.report"

    sale_order_ids = fields.Many2many("sale.order")

    # print report by button............ # qweb_id(action_report_doctordetail)
    @api.multi
    def print_report(self):
        return self.env.ref('verts_v11_transport_management.action_report_vehicle_request').report_action(self)

    @api.multi
    def button_print_sale_report(self):
        filename = 'Sale Wizard Report.xls'
        string = 'sale Report.xls'
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
        fnt.colour_index = 0x8
        fnt.bold = True
        fnt.width = 256 * 30
        style1.font = fnt

        worksheet.write_merge(0, 1, 2, 3, "Transport Sale Report", xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz center;'))
        worksheet.write(2, 0, 'Sale Order No', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 1, 'Customer', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 2, 'Confirmation Date', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 3, 'Product', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 4, 'Order Quantity', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))
        worksheet.write(2, 5, 'Unit', xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on, italic off; align: wrap on, vert centre, horiz left;'))

        a = 3
        # sale_order_ids = self.env['sale.order'].search([])
        sale_order = self.sale_order_ids
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", sale_order)
        if sale_order:
            for sale_id in sale_order:
                # worksheet.write(a, 0, sale_id.name)
                # worksheet.write(a, 1, sale_id.partner_id.name)
                # worksheet.write(a, 2, sale_id.confirmation_date)
                for line in sale_id.order_line:
                    worksheet.write(a, 0, sale_id.name)
                    worksheet.write(a, 1, sale_id.partner_id.name)
                    worksheet.write(a, 2, sale_id.confirmation_date)
                    worksheet.write(a, 3, line.product_id.name)
                    worksheet.write(a, 4, line.product_uom_qty)
                    worksheet.write(a, 5, line.price_unit)
                    a += 1
        else:
            sale_order_ids = self.env['sale.order'].search([])
            for id in sale_order_ids:
                if id.state == "done":
                    # print(id)
                    for sale_id in id:
                        for line in sale_id.order_line:
                            worksheet.write(a, 0, sale_id.name)
                            worksheet.write(a, 1, sale_id.partner_id.name)
                            worksheet.write(a, 2, sale_id.confirmation_date)
                            worksheet.write(a, 3, line.product_id.name)
                            worksheet.write(a, 4, line.product_uom_qty)
                            worksheet.write(a, 5, line.price_unit)
                            a += 1
        fp = BytesIO()
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        view_report_id = self.env['view.report.sale.wizard'].create({'file_name': out, 'datas_fname': filename})
        return {
            'res_id': view_report_id.id,
            'name': '',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'view.report.sale.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }



class view_report(models.TransientModel):
    _name = 'view.report.sale.wizard'

    datas_fname = fields.Char('File Name', size=256)
    file_name = fields.Binary('Report')

