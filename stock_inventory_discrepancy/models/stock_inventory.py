# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    INVENTORY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('pending', 'Pending to Approve'),
        ('done', 'Validated')]

    @api.one
    @api.depends('line_ids.product_qty', 'line_ids.theoretical_qty')
    def _compute_over_discrepancy_line_count(self):
        lines = self.line_ids
        self.over_discrepancy_line_count = sum(
            d.discrepancy_percent > d.discrepancy_threshold
            for d in lines)

    state = fields.Selection(
        selection=INVENTORY_STATE_SELECTION,
        string='Status', readonly=True, index=True, copy=False,
        help="States of the Inventory Adjustment:\n"
             "- Draft: Inventory not started.\n"
             "- In Progress: Inventory in execution.\n"
             "- Pending to Approve: Inventory have some discrepancies "
             "greater than the predefined threshold and it's waiting for the "
             "Control Manager approval.\n"
             "- Validated: Inventory Approved.")
    over_discrepancy_line_count = fields.Integer(
        string='Number of Discrepancies Over Threshold',
        compute=_compute_over_discrepancy_line_count,
        store=True)

    @api.model
    def action_over_discrepancies(self):
        self.state = 'pending'

    @api.multi
    def action_done(self):
        wh_id = self.location_id.get_warehouse(self.location_id)
        wh = self.env['stock.warehouse'].browse(wh_id)
        if self.over_discrepancy_line_count and \
                (wh.discrepancy_threshold > 0.0 or
                 self.location_id.discrepancy_threshold > 0.0):
            self.action_over_discrepancies()
        else:
            return super(StockInventory, self).action_done()

    @api.multi
    def action_force_done(self):
        return super(StockInventory, self).action_done()
