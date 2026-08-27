# Copyright 2020 Camptocamp SA
# Copyright 2021 ForgeFlow, S.L.
# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import exceptions, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_packaging_quantity = fields.Float(
        inverse="_inverse_product_packaging_quantity",
        # Explicit dependencies may drift from core, but avoid storing the field or
        # overriding writes while preserving manual package counts on quantity changes.
        depends=(
            "product_uom",
            "product_packaging_id",
            "move_line_ids.product_packaging_quantity",
        ),
    )

    def _compute_product_packaging_quantity(self):
        for move in self:
            if not move.product_packaging_id:
                continue
            move.product_packaging_quantity = sum(
                move.move_line_ids.mapped("product_packaging_quantity")
            )

    def _inverse_product_packaging_quantity(self):
        for move in self:
            if not move.move_line_ids or not move.product_packaging_quantity:
                continue
            if len(move.move_line_ids) != 1:
                raise exceptions.UserError(
                    self.env._(
                        "There are %d move lines involved. "
                        "Please set their product packaging done qty directly.",
                        len(move.move_line_ids),
                    )
                )
            move.move_line_ids.product_packaging_quantity = (
                move.product_packaging_quantity
            )

    def _action_assign(self, force_qty=False):
        """Set the packaging quantity when assigning."""
        res = super()._action_assign(force_qty=force_qty)
        moves_to_assign = self
        move_lines_origin = self.env["stock.move.line"].read_group(
            [
                ("move_id", "in", moves_to_assign.mapped("move_orig_ids").ids),
                (
                    "move_id.state",
                    "not in",
                    ("draft", "waiting", "confirmed", "cancel"),
                ),
                ("move_id.product_packaging_id", "!=", False),
            ],
            ["quantity", "product_packaging_quantity"],
            ["move_id", "location_dest_id", "lot_id", "result_package_id", "owner_id"],
            lazy=False,
        )
        move_lines_origin_dict = {
            (
                ml.get("location_dest_id")[0] if ml.get("location_dest_id") else False,
                ml.get("lot_id")[0] if ml.get("lot_id") else False,
                ml.get("result_package_id")[0]
                if ml.get("result_package_id")
                else False,
                ml.get("owner_id")[0] if ml.get("owner_id") else False,
            ): {
                "quantity": ml.get("quantity"),
                "product_packaging_quantity": ml.get("product_packaging_quantity"),
            }
            for ml in move_lines_origin
        }
        for line in moves_to_assign.move_line_ids.filtered("product_packaging_id"):
            found_move_lines_origin = move_lines_origin_dict.get(
                (
                    line.location_id.id,
                    line.lot_id.id,
                    line.package_id.id,
                    line.owner_id.id,
                ),
                {},
            )
            if found_move_lines_origin and found_move_lines_origin.get(
                "quantity"
            ) == round(
                line.quantity,
                self.env["decimal.precision"].precision_get("Product Unit of Measure"),
            ):
                line.product_packaging_quantity = found_move_lines_origin.get(
                    "product_packaging_quantity"
                )
        return res
