# Copyright 2019-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockRequest(models.Model):
    _name = "stock.request"
    _inherit = ["stock.request", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["open"]

    @api.model
    def _get_under_validation_exceptions(self):
        res = super()._get_under_validation_exceptions()
        res.append("route_id")
        return res

    def action_confirm(self):
        """
        Method to confirm the stock request order.
        Checks if there are open validation processes for related orders.
        If found, raises a validation error; otherwise,
        calls super() method to confirm the action.
        """
        for rec in self:
            # Search for stock request orders related to the current order
            related_orders = self.env["stock.request.order"].search(
                [("stock_request_ids", "=", rec.order_id.id)]
            )
            for order in related_orders:
                # Check if there are open validation processes for the related order
                if order.review_ids and not order.validated:
                    raise ValidationError(
                        _(
                            "A validation process is still open for "
                            f"at least one related record in {rec.order_id.name}."
                        )
                    )

        # Call the super() method action_confirm() only if no open validations are found
        return super().action_confirm()
