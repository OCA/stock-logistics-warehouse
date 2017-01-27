# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    INVENTORY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('pending', 'Pending to Approve'),
        ('done', 'Validated')]

    state = fields.Selection(selection=INVENTORY_STATE_SELECTION,
                             string='Status', readonly=True,
                             select=True, copy=False)

    @api.model
    @api.depends('line_ids.product_qty', 'line_ids.theoretical_qty')
    def _compute_over_discrepancies(self):
        threshold = 0.0
        discrepancies = self.line_ids.mapped('discrepancy_percentage')
        wh_id = self.location_id.get_warehouse(self.location_id)
        wh = self.env['stock.warehouse'].browse(wh_id)
        if self.location_id.discrepancy_threshold > 0.0:
            threshold = self.location_id.discrepancy_threshold
        elif wh.discrepancy_threshold > 0.0:
            threshold = wh.discrepancy_threshold
        else:
            pass
        if threshold:
            self.over_discrepancies = sum(d > threshold for d in discrepancies)

    cycle_count_id = fields.Many2one(comodel_name='stock.cycle.count',
                                     string='Stock Cycle Count')
    over_discrepancies = fields.Integer(string='Number of Discrepancies over '
                                               'Threshold',
                                        compute=_compute_over_discrepancies,
                                        store=True)

    @api.model
    def action_over_discrepancies(self):
        self.state = 'pending'
        self.env.cr.commit()
        raise UserError(
            _('Cannot validate the Inventory Adjustment.\n Found %s over '
              'discrepancies') % self.over_discrepancies)

    @api.multi
    def action_done(self):
        wh_id = self.location_id.get_warehouse(self.location_id)
        wh = self.env['stock.warehouse'].browse(wh_id)
        if self.over_discrepancies and (wh.discrepancy_threshold > 0.0 or
                self.location_id.discrepancy_threshold > 0.0):
            self.action_over_discrepancies()
        else:
            return super(StockInventory, self).action_done()

    @api.multi
    def action_force_done(self):
        return super(StockInventory, self).action_done()
