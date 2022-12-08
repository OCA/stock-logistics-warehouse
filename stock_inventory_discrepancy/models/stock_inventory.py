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

    def action_view_inventory_adjustment(self):
        res = super().action_view_inventory_adjustment()
        res.update(
            {
                "view_id": self.env.ref(
                    "stock_inventory_discrepancy.stock_quant_discrepency_tree_view"
                ).id
            }
        )
        return res

    @api.depends("stock_quant_ids.inventory_quantity", "stock_quant_ids.quantity")
    def _compute_over_discrepancy_line_count(self):
        for inventory in self:
            lines = inventory.stock_quant_ids.filtered(
                lambda line: line._has_over_discrepancy()
            )
            inventory.over_discrepancy_line_count = len(lines)

    def action_over_discrepancies(self):
        self.write({"state": "pending"})
        notification = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("The inventory needs to be approved."),
                "type": "warning",
                "sticky": False,  # True/False will display for few seconds if false
            },
        }
        return notification

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

    def action_state_to_done(self):
        for inventory in self:
            if inventory.over_discrepancy_line_count > 0.0:
                if self.user_has_groups(
                    "stock_inventory_discrepancy.group_stock_inventory_validation"
                ) and not self.user_has_groups(
                    "stock_inventory_discrepancy."
                    "group_stock_inventory_validation_always"
                ):
                    return inventory.action_over_discrepancies()
                else:
                    inventory._check_group_inventory_validation_always()
        return super(StockInventory, self).action_state_to_done()

    def action_force_done(self):
        return super(StockInventory, self).action_state_to_done()
