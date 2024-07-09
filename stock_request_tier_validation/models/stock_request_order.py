# Copyright 2019-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockRequestOrder(models.Model):
    _name = "stock.request.order"
    _inherit = ["stock.request.order", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["open"]

    @api.model
    def _get_under_validation_exceptions(self):
        res = super()._get_under_validation_exceptions()
        res.append("route_id")
        return res

    def action_confirm(self):
        """
        Confirms the stock request order.

        Validates if needed, ensures tier validation,
        and checks for open validation processes.
        This method reinforces tier.validation due to
        the state being a computed method, aligning
        Stock Request Orders (SROs) with Stock Requests (SRs).
        """
        for rec in self:
            # Validate if needed
            if rec.need_validation:
                reviews = rec.request_validation()
                rec._validate_tier(reviews)
                if not self._calc_reviews_validated(reviews):
                    raise ValidationError(
                        _(
                            "This action needs to be validated for at least "
                            "one record. \nPlease request a validation."
                        )
                    )

            # Check for open validation processes
            if rec.review_ids and not rec.validated:
                raise ValidationError(
                    _("A validation process is still open for at least one record.")
                )

        return super().action_confirm()
