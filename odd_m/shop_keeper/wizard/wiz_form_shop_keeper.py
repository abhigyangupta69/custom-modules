from odoo import api, fields, models, SUPERUSER_ID

class WizShopKeeperForm(models.TransientModel):
    _name = "wiz.shop.keeper.form"
    product_type = fields.Selection([('toys', 'Toys'), ('jwelery', 'Jwelery'), ('frames', 'Frames'), ('Others', 'Others')],string='Old Product Type',default='Others')
    shipping_date = fields.Date('Old Shipping Date')
    order_date = fields.Date('Old Order Date')
    new_shipping_date = fields.Date('New Shipping Date')
    new_order_date = fields.Date('New Order Date')


    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(WizShopKeeperForm, self).default_get(fields)
        shop_keeper = self.env['shipping.details'].browse(self._context.get('active_id'))
        res.update({'product_type': shop_keeper. product_type, 'order_date': shop_keeper. order_date, 'new_order_date': shop_keeper. order_date, 'shipping_date': shop_keeper. shipping_date, 'new_shipping_date': shop_keeper.shipping_date})
        return res


# create history by button...........
    def create_form(self):
        context = self._context or {}
        shop_lst = []
        shop = self.env['shipping.details'].browse(self._context.get('active_id'))
        each = self.read(['shipping_date','order_date','new_shipping_date','new_order_date','user_id'])
        shop_lst.append([0, False, {'order_date': each[0]['order_date'],'shipping_date': each[0]['shipping_date'],
                                         'new_shipping_date': each[0]['new_shipping_date'], 'new_order_date': each[0]['new_order_date'],
                                         'user_id': self.env.user.id,
                                         'shop_history':shop.id}])
        shop.write({'shipping_date': each[0]['new_shipping_date'],'order_date': each[0]['new_order_date'],
                         'history_detail': shop_lst})
        return {'type': 'ir.actions.act_window_close'}












    # def create_form(self):
    #     context = self._context or {}
    #     shop = self.env['shipping.details'].browse(self._context.get('active_id'))
    #     each = self.read(['product_type', 'order_date', 'new_order_date', 'shipping_date','new_shipping_date'])
    #     shop.write(
    #         {
    #          'order_date': each[0]['new_order_date'],'shipping_date': each[0]['new_shipping_date']})
    #     return {'type': 'ir.actions.act_window_close'}

