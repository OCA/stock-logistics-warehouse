# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from odoo.addons.stock.models.stock_inventory import Inventory


def post_load_hook():
    def action_validate_discrepancy(self):
        """Override method to avoid inline group validation"""
        if not self.exists():
            return
        self.ensure_one()
        # START HOOK: - Allow specific group to validate inventory
        #             - Allow validate on pending status
        if (
            not self.user_has_groups("stock.group_stock_manager")
            and not self.user_has_groups(
                "stock_inventory_discrepancy.group_stock_inventory_validation"
            )
            and not self.user_has_groups(
                "stock_inventory_discrepancy.group_stock_inventory_validation_always"
            )
        ):
            raise UserError(
                _("Only a stock manager can validate an inventory adjustment.")
            )
        if self.state not in ["confirm", "pending"]:
            raise UserError(
                _(
                    "You can't validate the inventory '%s', maybe this inventory "
                    + "has been already validated or isn't ready."
                )
                % (self.name)
            )
        # END HOOK
        inventory_lines = self.line_ids.filtered(
            lambda l: l.product_id.tracking in ["lot", "serial"]
            and not l.prod_lot_id
            and l.theoretical_qty != l.product_qty
        )
        lines = self.line_ids.filtered(
            lambda l: float_compare(
                l.product_qty, 1, precision_rounding=l.product_uom_id.rounding
            )
            > 0
            and l.product_id.tracking == "serial"
            and l.prod_lot_id
        )
        if inventory_lines and not lines:
            wiz_lines = [
                (0, 0, {"product_id": product.id, "tracking": product.tracking})
                for product in inventory_lines.mapped("product_id")
            ]
            wiz = self.env["stock.track.confirmation"].create(
                {"inventory_id": self.id, "tracking_line_ids": wiz_lines}
            )
            return {
                "name": _("Tracked Products in Inventory Adjustment"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "views": [(False, "form")],
                "res_model": "stock.track.confirmation",
                "target": "new",
                "res_id": wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        return True

    if not hasattr(Inventory, "action_validate_original"):
        Inventory.action_validate_original = Inventory.action_validate

    Inventory._patch_method("action_validate", action_validate_discrepancy)
