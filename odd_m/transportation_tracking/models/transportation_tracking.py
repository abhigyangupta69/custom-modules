from odoo import api, fields, models._
from odoo.exceptions import ValidationError, UserError, AccessError
from odoo import osv

class TransportTrack(models.Model):
    _name = "transport.track"
    _rec_name = "vehicle_no"
    vehicle_no = fields.Char('Vehicle No')
    vehicle_model = fields.Char('Model-Name')
    vehicle_type = fields.Selection([('Bus', 'Bus'), ('Car', 'Car'), ('Auto', 'Auto'), ('Ambulance', 'Ambulance')], string='Vehicle-Type')
    vehicle_avg = fields.Float('Vehicle-Average')
    outside_avg = fields.Float('Outside-Average')
    local_avg = fields.Float('Local Average ')
    state = fields.Selection([('Draft', 'Draft'), ('Done', 'Done')],string='State', default='Draft')


class TransportMaster(models.Model):
    _name = "transport.master"
    create_date = fields.Datetime('Create Date', default=fields.Datetime.now)
    ref_no = fields.Char('Reference No')
    move_date = fields.Date('Move-Date')
    driver_name = fields.Char('Driver Name')
    transport_line = fields.One2many('journey.detail','journey_line',string='Transport Line')
    history_detail = fields.One2many('transport.detail.history','transport_history',string="History")
    state = fields.Selection([('Draft', 'Draft'), ('Done', 'Done')],
                             string='State', default='Draft')

    # print report by button..........# qweb_id(action_report_transportmaster)..
    @api.multi
    def print_report(self):
        return self.env.ref('transportation_tracking.action_report_transportmaster').report_action(self)



    # Random No generate by system(with xml)
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('transport.master')
        vals.update({'ref_no': seq})
        res = super(TransportMaster, self).create(vals)
        return res

    # @api.multi
    # def write(self, values):
    #     print"=insert=in=one2many=using=create=method===="
    #
    #     for val in [self] :
    #         if 'move_date' in values and values['move_date'] and'new_move_date' in values and values['new_move_date']and'driver_name' in values and values['driver_name'] and 'new_driver_name' in values and values['new_driver_name']:
    #             self.env['transport.detail.history'].create({'transport_history': val.id, 'move_date':val.move_date,'new_move_date':values['new_move_date'],
    #                                                'driver_name': val.driver_name, 'new_driver_name': values['new_driver_name']})
    #         elif 'move_date' in values and values['move_date'] and 'new_move_date' in values and values['new_move_date'] and 'driver_name' in values and values['driver_name']:
    #             self.env['transport.detail.history'].create(
    #                 {'transport_history': val.id, 'move_date': val.move_date, 'new_move_date': values['new_move_date'],
    #                  'driver_name': val.driver_name, 'new_driver_name': values['new_driver_name']})
    #         elif 'move_date' in values and values['move_date'] and 'new_move_date' in values and values['new_move_date']:
    #             self.env['transport.detail.history'].create(
    #                 {'transport_history': val.id, 'move_date': val.move_date, 'new_move_date': values['new_move_date'],
    #                  'driver_name': val.driver_name, 'new_driver_name': values['new_driver_name']})
    #         elif 'move_date' in values and values['move_date']:
    #             self.env['transport.detail.history'].create(
    #                 {'transport_history': val.id, 'move_date': val.move_date, 'driver_name': val.driver_name})
    #
    #     res = super(TransportMaster, self).write(values)
    #     return res

class JourneyDetail(models.Model):
    _name = "journey.detail"

    @api.depends('opening_reading', 'closing_reading')
    def _compute_distance(self):
        self.update({'distance': self.closing_reading - self.opening_reading})



    @api.depends('distance', 'vehicle_no' ,'journey_type')
    def _compute_cost(self):
        if self.journey_type == 'local':
            self.update({'cost': self.distance * self.vehicle_no.local_avg})
        else:
            self.update({'cost': self.distance * self.vehicle_no.outside_avg})


    vehicle_no = fields.Many2one('transport.track',string='Vehicle No')
    vehicle_type = fields.Selection([('bus', 'Bus'), ('car', 'Car'), ('auto', 'Auto'), ('ambulance', 'Ambulance')], string='Vehicle-Type')
    journey_type = fields.Selection([('local', 'Local'), ('outside', 'Outside')],string="Journey-Type")
    destination = fields.Char('Destination')
    opening_reading = fields.Float('Opening-Reading')
    closing_reading = fields.Float('Closing-Reading')
    distance = fields.Float(compute='_compute_distance',string='Distance(K.M)', store=True)
    cost = fields.Float(compute='_compute_cost',string='Cost', store=True)
    journey_line = fields.Many2one('transport.master',string='Journey Line')
    # THE BELOW FIELD IS FROM OTHER CLaSS SO MAKE IT RELATED FIELD To show for Tree view.
    move_date = fields.Date(related='journey_line.move_date', string='Move-Date', store=True, readonly=True)
    driver_name = fields.Char(related='journey_line.driver_name', string='Driver Name', store=True, readonly=True)

    @api.onchange('vehicle_no')
    def onchange_vehicle_no(self):
        if self.vehicle_no:
            self.vehicle_type = self.vehicle_no.vehicle_type


    @api.model
    def create(self, vals):
        if 'cost' in vals and vals['cost'] <= 0:
            raise ValidationError(_('cost should be greater than zero'))
        res = super(JourneyDetail, self).create(vals)
        return res


    @api.multi
    def write(self, values):
        if 'cost' in values and values['cost'] <= 0:
            raise ValidationError(_('cost should be greater than zero'))
        else:
            values['cost'] = 10

        res = super(JourneyDetail, self).write(values)
        return res

    # @api.model
    # def create(self, vals):
    #     if 'opening_reading' in vals and vals['opening_reading'] > self.closing_reading:
    #         raise ValidationError(_('Opening reading should be less than than closing reading'))
    #     else:
    #         vals['opening_reading'] = 50
    #     res = super(JourneyDetail, self).create(vals)
    #     return res



class TransportDetailHistory(models.Model):
    _name = "transport.detail.history"
    move_date = fields.Date('Old Move-Date')
    new_move_date = fields.Date('New Move-Date')
    driver_name = fields.Char('Old Driver Name')
    new_driver_name = fields.Char('New Driver Name')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    transport_history = fields.Many2one('transport.master', string='Transport History')












































