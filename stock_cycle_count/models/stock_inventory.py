# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError

PERCENT = 100.0


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.one
    def _compute_inventory_accuracy(self):
        total_qty = sum(self.line_ids.mapped('theoretical_qty'))
        abs_discrepancy = sum(self.line_ids.mapped(
            lambda x: abs(x.discrepancy_qty)))
        if total_qty:
            self.inventory_accuracy = PERCENT * (
                total_qty - abs_discrepancy) / total_qty
        if not self.line_ids and self.state == 'done':
            self.inventory_accuracy = 100.0

    cycle_count_id = fields.Many2one(
        comodel_name='stock.cycle.count', string='Stock Cycle Count',
        ondelete='cascade', readonly=True)
    inventory_accuracy = fields.Float(string='Accuracy',
                                      compute=_compute_inventory_accuracy,
                                      digits=(3, 2))

    @api.multi
    def action_done(self):
        if self.cycle_count_id:
            self.cycle_count_id.state = 'done'
        return super(StockInventory, self).action_done()

    @api.multi
    def write(self, vals):
        for inventory in self:
            if (inventory.cycle_count_id and 'state' not in vals.keys() and
                    inventory.state == 'draft'):
                raise UserError(
                    _('You cannot modify the configuration of an Inventory '
                      'Adjustment related to a Cycle Count.'))
        return super(StockInventory, self).write(vals)
