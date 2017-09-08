# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

PERCENT = 100.0


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    @api.depends("state", "line_ids")
    def _compute_inventory_accuracy(self):
        for inv in self:
            theoretical = sum(inv.line_ids.mapped(
                lambda x: abs(x.theoretical_qty)))
            abs_discrepancy = sum(inv.line_ids.mapped(
                lambda x: abs(x.discrepancy_qty)))
            if theoretical:
                inv.inventory_accuracy = max(
                    PERCENT * (theoretical - abs_discrepancy) / theoretical,
                    0.0)
            if not inv.line_ids and inv.state == 'done':
                inv.inventory_accuracy = PERCENT

    cycle_count_id = fields.Many2one(
        comodel_name='stock.cycle.count', string='Stock Cycle Count',
        ondelete='restrict', readonly=True)
    inventory_accuracy = fields.Float(
        string='Accuracy', compute='_compute_inventory_accuracy',
        digits=(3, 2), store=True, group_operator="avg")

    def _update_cycle_state(self):
        for inv in self:
            if inv.cycle_count_id and inv.state == 'done':
                inv.cycle_count_id.state = 'done'
        return True

    @api.multi
    def action_done(self):
        res = super(StockInventory, self).action_done()
        self._update_cycle_state()
        return res

    @api.multi
    def action_force_done(self):
        res = super(StockInventory, self).action_force_done()
        self._update_cycle_state()
        return res

    @api.multi
    def write(self, vals):
        for inventory in self:
            if (inventory.cycle_count_id and 'state' not in vals.keys() and
                    inventory.state == 'draft'):
                raise UserError(
                    _('You cannot modify the configuration of an Inventory '
                      'Adjustment related to a Cycle Count.'))
        return super(StockInventory, self).write(vals)
