# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class VerticalLiftOperationPickZeroCheck(models.TransientModel):
    _name = "vertical.lift.operation.pick.zero.check"
    _description = "Make sure the tray location is empty"

    # Case 1: Maybe No quant
    #  - Case 1.1: No stock -> nothing to do, or write inventory_quantity zero
    #  - Case 1.2: Stock -> create or update quants with inventory_quantity 1
    vertical_lift_operation_pick_id = fields.Many2one("vertical.lift.operation.pick")

    def _get_data_from_operation(self):
        """Return picking, location and product from the operation shuttle"""
        operation = self.vertical_lift_operation_pick_id

        # If the move is split into several move lines, it is
        # moved to another picking, being a backorder of the
        # original one. We are always interested in the original
        # picking that was processed at first, so if the picking
        # is a backorder of another picking, we take that other one.
        location = operation.current_move_line_id.location_id
        product = operation.product_id
        return operation, location, product

    def button_confirm_empty(self):
        """User confirms the tray location is empty

        This is in accordance with what we expected, because we only
        call this action if we think the location is empty. We create
        an inventory adjustment that states that a zero-check was
        done for this location."""
        # Case 1.1
        operation, location, product = self._get_data_from_operation()
        quants = self.env["stock.quant"]._gather(product, location)
        if not quants:
            quants = self.env["stock.quant"].create(
                {
                    "location_id": location.id,
                    "product_id": product.id,
                    "user_id": self.env.user.id,
                    "inventory_quantity": 0,
                }
            )
        else:
            quants = fields.first(quants)
            quants.write(
                {
                    "user_id": self.env.user.id,
                    "inventory_quantity": 0,
                }
            )
        quants.action_apply_inventory()

        # Return to the execution of the release,
        # but without checking again if the tray is empty.
        return operation.with_context(skip_zero_quantity_check=True).button_release()

    def button_confirm_not_empty(self):
        """User confirms the tray location is not empty

        This contradicts what we expected, because we only call this
        action if we think the location is empty. We create a draft
        inventory adjustment stating the mismatch.
        """
        # Case 1.2
        operation, location, product = self._get_data_from_operation()
        quants = self.env["stock.quant"]._gather(product, location)
        if not quants:
            quants = self.env["stock.quant"].create(
                {
                    "location_id": location.id,
                    "product_id": product.id,
                    "user_id": self.env.user.id,
                    "inventory_quantity": 1,
                }
            )
        else:
            quants = fields.first(quants)
            quants.write(
                {
                    "user_id": self.env.user.id,
                    "inventory_quantity": 1,
                }
            )
        # breakpoint()
        quants.action_apply_inventory()

        # Return to the execution of the release,
        # but without checking again if the tray is empty.
        return operation.with_context(skip_zero_quantity_check=True).button_release()
