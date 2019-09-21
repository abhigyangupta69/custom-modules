from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo import osv

class ShopDetails(models.Model):
    _name = "shop.details"
    _rec_name = 'shop_name'
    shop_name = fields.Char('Shop Name')
    gst_no = fields.Char(string='Gst No')
    shop_type = fields.Selection([('kirana', 'Kirana'), ('jwelery', 'Jwelery'), ('photographer', 'Photographer'),('Others', 'Others')],string ='Shop Type',default='Others')
    gst = fields.Float(string='Gst percent')



class ShippingDetails(models.Model):
    _name = "shipping.details"
    product_type = fields.Selection([('toys', 'Toys'), ('jwelery', 'Jwelery'), ('frames', 'Frames'), ('Others', 'Others')],string='Product Type',default='Others')
    order_date = fields.Date(string='Order date')
    shipping_date = fields.Date(string='Shipping date')
    expected_date = fields.One2many('full.details','product',string='Dispatch date')
    ref_no = fields.Char('Bill No')
    history_detail = fields.One2many('history.shop','shop_history',string="History")

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('shipping.details')
        vals.update({'ref_no': seq})
        res = super(ShippingDetails, self).create(vals)
        return res

    @api.model
    def create(self, vals):
        if 'shipping_date' in vals and vals['shipping_date'] == self.order_date:
            raise ValidationError(_('Item can not deliver at the same date'))
        res = super(ShippingDetails, self).create(vals)
        return res

    @api.multi
    def write(self, values):
        if 'shipping_date' in values and values['shipping_date'] == self.order_date:
            raise ValidationError(_('Item can not deliver at the same date'))
        else:
            values['order_date'] = '2019-1-1'

        res = super(ShippingDetails, self).write(values)
        return res


class FullDetails(models.Model):
    _name = "full.details"
    shop_name = fields.Many2one('shop.details',string='Shop Name')
    gst_no = fields.Char(string='Gst No')
    product_type = fields.Selection([('toys', 'Toys'), ('jwelery', 'Jwelery'), ('frames', 'Frames')],string='Product Type')
    product_name = fields.Char('Product Name')
    product = fields.Many2one('shipping.details',string='Product')
    cost = fields.Float('Cost Of Product')
    total_price = fields.Char(compute='_compute_cost',string='price including Gst', store=True)


    @api.depends('shop_name','cost')
    def _compute_cost(self):
        if self.product_type == 'toys':
            self.update({'total_price': self.cost +(self.cost*10)/100})
        elif self.product_type == 'jwelery':
                self.update({'total_price': self.cost +(self.cost*self.shop_name.gst)/100})
        elif self.product_type == 'frames':
            self.update({'total_price': self.cost +(self.cost*5)/100})
        else:
            self.update({'total_price': self.cost})

    @api.onchange('shop_name')
    def onchange_shop_name(self):
        if self.shop_name:
            self.gst_no = self.shop_name.gst_no




class HistoryShop(models.Model):
    _name = "history.shop"
    shipping_date = fields.Date('Old Shipping date')
    new_shipping_date = fields.Date('New Shipping date')
    order_date = fields.Date('Old Order date')
    new_order_date = fields.Date('New Order date')
    shop_history = fields.Many2one('shipping.details', string='Shop History')
    user_id = fields.Many2one('res.users', string='Deliver By', default=lambda self: self.env.user)


class CustomerDetail(models.Model):
    _name = "customer.detail"
    name_customer = fields.Char("Customer Name")
    customer_address = fields.Char("Customer Address")
    product_payment = fields.Selection([('net','Net Banking'),('cod','Cash On Delivery'),('paytm','Paytm'),('Others','Others')],string='Payment method',default='Others')
    delivery_time = fields.Selection([('home','Home'),('Office','OfficeTime(9a.m to 6 p.m)'),('all','All Time Delivery')],string='Delivery Time')
    feed = fields.One2many('customer.support','update_details',string='Feeds')


class CustomerSupport(models.Model):
    _name = 'customer.support'
    ref_no = fields.Char('Bill No')
    experience = fields.Selection([('notg','Notgood'),('good','Good'),('exe','Exelent')],string='Your Experience')
    rating = fields.Selection([('1','*'),('2','**'),('3','***'),('4','****'),('5','****')],string='Rating of product')
    update_details = fields.Many2one('customer.detail',string='Update Details')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('customer.support')
        vals.update({'ref_no': seq})
        res = super(CustomerSupport, self).create(vals)
        return res





