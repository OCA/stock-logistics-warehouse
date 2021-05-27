# Copyright 2017-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    state = fields.Selection(
        selection_add=[("pending", "Pending to Approve"), ("done",)],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        help="States of the Inventory Adjustment:\n"
        "- Draft: Inventory not started.\n"
        "- In Progress: Inventory in execution.\n"
        "- Pending to Approve: Inventory have some discrepancies "
        "greater than the predefined threshold and it's waiting for the "
        "Control Manager approval.\n"
        "- Validated: Inventory Approved.",
    )
    over_discrepancy_line_count = fields.Integer(
        string="Number of Discrepancies Over Threshold",
        compute="_compute_over_discrepancy_line_count",
        store=True,
    )

    @api.depends("line_ids.product_qty", "line_ids.theoretical_qty")
    def _compute_over_discrepancy_line_count(self):
        for inventory in self:
            lines = inventory.line_ids.filtered(
                lambda line: line._has_over_discrepancy()
            )
            inventory.over_discrepancy_line_count = len(lines)

    def action_over_discrepancies(self):
        self.write({"state": "pending"})

    def _check_group_inventory_validation_always(self):
        grp_inv_val = self.env.ref(
            "stock_inventory_discrepancy.group_stock_inventory_validation_always"
        )
        if grp_inv_val in self.env.user.groups_id:
            return True
        else:
            raise UserError(
                _(
                    "The Qty Update is over the Discrepancy Threshold.\n "
                    "Please, contact a user with rights to perform "
                    "this action."
                )
            )

    def _action_done(self):
        for inventory in self:
            if inventory.over_discrepancy_line_count > 0.0:
                if self.user_has_groups(
                    "stock_inventory_discrepancy.group_stock_inventory_validation"
                ) and not self.user_has_groups(
                    "stock_inventory_discrepancy."
                    "group_stock_inventory_validation_always"
                ):
                    inventory.action_over_discrepancies()
                    return True
                else:
                    inventory._check_group_inventory_validation_always()
        return super(StockInventory, self)._action_done()

    def action_force_done(self):
        return super(StockInventory, self)._action_done()
