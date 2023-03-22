# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    INVENTORY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('pending', 'Pending to Approve'),
        ('done', 'Validated')]

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
        compute='_compute_over_discrepancy_line_count',
        store=True)

    @api.multi
    @api.depends('line_ids.product_qty', 'line_ids.theoretical_qty')
    def _compute_over_discrepancy_line_count(self):
        for inventory in self:
            lines = inventory.line_ids.filtered(
                lambda line: line.discrepancy_percent > line.
                discrepancy_threshold
            )
            inventory.over_discrepancy_line_count = len(lines)

    @api.multi
    def action_over_discrepancies(self):
        self.write({'state': 'pending'})

    def _check_group_inventory_validation_always(self):
        grp_inv_val = self.env.ref(
            'stock_inventory_discrepancy.group_'
            'stock_inventory_validation_always')
        if grp_inv_val in self.env.user.groups_id:
            return True
        else:
            raise UserError(
                _('The Qty Update is over the Discrepancy Threshold.\n '
                  'Please, contact a user with rights to perform '
                  'this action.')
            )

    def action_done(self):
        self.ensure_one()
        if self.over_discrepancy_line_count and self.line_ids.filtered(
                lambda t: t.discrepancy_threshold > 0.0):
            if self.env.context.get('normal_view', False):
                self.action_over_discrepancies()
                return True
            else:
                self._check_group_inventory_validation_always()
        return super(StockInventory, self).action_done()

    @api.multi
    def action_force_done(self):
        return super(StockInventory, self).action_done()
