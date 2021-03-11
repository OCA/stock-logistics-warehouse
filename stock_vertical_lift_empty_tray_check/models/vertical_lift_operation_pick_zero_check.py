# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, fields, models


class VerticalLiftOperationPickZeroCheck(models.TransientModel):
    _name = "vertical.lift.operation.pick.zero.check"
    _description = "Make sure the tray location is empty"

    vertical_lift_operation_pick_id = fields.Many2one("vertical.lift.operation.pick")

    def _get_data_from_operation(self):
        """Return picking, location and product from the operation shuttle"""
        operation = self.vertical_lift_operation_pick_id

        # If the move is split into several move lines, it is
        # moved to another picking, being a backorder of the
        # original one. We are always interested in the original
        # picking that was processed at first, so if the picking
        # is a backorder of another picking, we take that other one.
        picking = operation.picking_id.backorder_id or operation.picking_id
        location = operation.current_move_line_id.location_id
        product = operation.product_id
        return operation, picking, location, product

    def button_confirm_empty(self):
        """User confirms the tray location is empty

        This is in accordance with what we expected, because we only
        call this action if we think the location is empty. We create
        an inventory adjustment that states that a zero-check was
        done for this location."""
        operation, picking, location, product = self._get_data_from_operation()
        inventory_name = _(f"Zero check in location: {location.complete_name}")
        inventory = (
            self.env["stock.inventory"]
            .sudo()
            .create(
                {
                    "name": inventory_name,
                    "product_ids": [(4, product.id)],
                    "location_ids": [(4, location.id)],
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "product_qty": 0,
                                "theoretical_qty": 0,
                                "location_id": location.id,
                            },
                        ),
                    ],
                }
            )
        )
        inventory.action_start()
        inventory.action_validate()

        # Return to the execution of the release,
        # but without checking again if the tray is empty.
        return operation.with_context(skip_zero_quantity_check=True).button_release()

    def button_confirm_not_empty(self):
        """User confirms the tray location is not empty

        This contradicts what we expected, because we only call this
        action if we think the location is empty. We create a draft
        inventory adjustment stating the mismatch.
        """
        operation, picking, location, product = self._get_data_from_operation()
        inventory_name = _(
            f"{picking.name} zero check issue on location {location.complete_name}"
        )
        self.env["stock.inventory"].sudo().create(
            {
                "name": inventory_name,
                "product_ids": [(4, product.id)],
                "location_ids": [(4, location.id)],
            }
        )

        # Return to the execution of the release,
        # but without checking again if the tray is empty.
        return operation.with_context(skip_zero_quantity_check=True).button_release()
