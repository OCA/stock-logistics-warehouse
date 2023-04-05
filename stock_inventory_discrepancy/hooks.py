# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import _, fields
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from odoo.addons.stock.models.stock_quant import StockQuant


def post_load_hook():
    def _apply_inventory_discrepancy(self):
        """Override method to avoid inline group validation"""
        move_vals = []
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
        # Allow to write last_inventory_date on stock.location
        self = self.sudo()
        # END HOOK
        for quant in self:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if (
                float_compare(
                    quant.inventory_diff_quantity,
                    0,
                    precision_rounding=quant.product_uom_id.rounding,
                )
                > 0
            ):
                move_vals.append(
                    quant._get_inventory_move_values(
                        quant.inventory_diff_quantity,
                        quant.product_id.with_company(
                            quant.company_id
                        ).property_stock_inventory,
                        quant.location_id,
                    )
                )
            else:
                move_vals.append(
                    quant._get_inventory_move_values(
                        -quant.inventory_diff_quantity,
                        quant.location_id,
                        quant.product_id.with_company(
                            quant.company_id
                        ).property_stock_inventory,
                        out=True,
                    )
                )
        moves = (
            self.env["stock.move"].with_context(inventory_mode=False).create(move_vals)
        )
        moves._action_done()
        self.location_id.write({"last_inventory_date": fields.Date.today()})
        date_by_location = {
            loc: loc._get_next_inventory_date() for loc in self.mapped("location_id")
        }
        for quant in self:
            quant.inventory_date = date_by_location[quant.location_id]
        self.write({"inventory_quantity": 0, "user_id": False})
        self.write({"inventory_diff_quantity": 0})

    StockQuant._patch_method("_apply_inventory", _apply_inventory_discrepancy)
