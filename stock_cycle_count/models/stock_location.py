# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, fields, models, tools
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
_logger = logging.getLogger(__name__)

try:
    from numpy import mean
    NUMPY_PATH = tools.find_in_path('numpy')
except (ImportError, IOError) as err:
    _logger.debug(err)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.one
    def _compute_loc_accuracy(self):
        history = self.env['stock.inventory'].search([
            ('location_id', '=', self.id), ('state', '=', 'done')])
        history = history.sorted(key=lambda r: r.write_date, reverse=True)
        if history:
            wh_id = self.get_warehouse(self)
            wh = self.env['stock.warehouse'].browse(wh_id)
            if len(history) > wh.counts_for_accuracy_qty:
                self.loc_accuracy = mean(history[:wh.counts_for_accuracy_qty].
                                         mapped('inventory_accuracy'))
            else:
                self.loc_accuracy = mean(history.mapped('inventory_accuracy'))

    zero_confirmation_disabled = fields.Boolean(
        string='Disable Zero Confirmations',
        default=False,
        help='Define whether this location will trigger a zero-confirmation '
             'validation when a rule for its warehouse is defined to perform '
             'zero-confirmations.')
    cycle_count_disabled = fields.Boolean(
        string='Exclude from Cycle Count',
        default=False,
        help='Define whether the location is going to be cycle counted.')
    qty_variance_inventory_threshold = fields.Float('Acceptable Inventory '
                                                    'Quantity Variance '
                                                    'Threshold')
    loc_accuracy = fields.Float(string='Inventory Accuracy',
                                compute=_compute_loc_accuracy,
                                digits=(3, 2))

    @api.model
    def _get_zero_confirmation_domain(self):
        domain = [('location_id', '=', self.id)]
        return domain

    @api.one
    def check_zero_confirmation(self):
        if not self.zero_confirmation_disabled:
            wh_id = self.get_warehouse(self)
            wh = self.env['stock.warehouse'].browse(wh_id)
            rule_model = self.env['stock.cycle.count.rule']
            zero_rule = rule_model.search([
                ('rule_type', '=', 'zero'),
                ('warehouse_ids', '=', wh.id)])
            if zero_rule:
                quants = self.env['stock.quant'].search(
                    self._get_zero_confirmation_domain())
                if not quants:
                    self.create_zero_confirmation_cycle_count()

    def create_zero_confirmation_cycle_count(self):
        date = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        wh_id = self.get_warehouse(self)
        date_horizon = self.env['stock.warehouse'].browse(
            wh_id).get_horizon_date()[0].strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        counts_planned = self.env['stock.cycle.count'].search([
            ('date_deadline', '<', date_horizon), ('state', '=', 'draft'),
            ('location_id', '=', self.id)])
        if counts_planned:
            counts_planned.write({'state': 'cancelled'})
        rule = self.env['stock.cycle.count.rule'].search([
            ('rule_type', '=', 'zero'), ('warehouse_ids', '=', wh_id)])
        self.env['stock.cycle.count'].create({
            'date_deadline': date,
            'location_id': self.id,
            'cycle_count_rule_id': rule.id,
            'state': 'draft'
        })
        return True
