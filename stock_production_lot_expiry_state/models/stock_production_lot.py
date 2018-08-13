# Copyright (C) 2018 - TODAY, Open Source Integrators

from datetime import datetime
from odoo import fields, models, api


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    state = fields.Selection([
        ('best_before', 'Best Before'),
        ('still_good', 'Still Good'),
        ('removal', 'Removal'),
        ('end_of_life', 'End Of Life'),
        ('alert', 'Alert')],
        readonly=True, default='best_before', copy=False)

    @api.model
    def _update_state(self):
        lots = self.env['stock.production.lot'].search([])
        for lot in lots:
            date = str(datetime.now())

            if lot.use_date:
                if date < lot.use_date:
                    lot.state = 'best_before'
            if lot.use_date and lot.removal_date:
                if date > lot.use_date and date < lot.removal_date:
                    lot.state = 'still_good'
            if lot.removal_date and lot.life_date:
                if date > lot.removal_date and date < lot.life_date:
                    lot.state = 'removal'
            if lot.life_date and lot.alert_date:
                if date > lot.life_date and date < lot.alert_date:
                    lot.state = 'end_of_life'
            if lot.alert_date:
                if date > lot.alert_date:
                    lot.state = 'alert'
