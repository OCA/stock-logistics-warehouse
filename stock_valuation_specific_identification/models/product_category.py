# Copyright 2024 Matt Taylor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = "product.category"

    # This should fall back to FIFO for products that are not tracked
    property_specific_ident_cost = fields.Boolean(
        string="Cost by Lot/Serial",
        default=False,
        company_dependent=True,
        help="""Specific Identification Valuation:
        - Tracked products are valued according to specific lot/serial numbers.
        - Untracked products are valued according to the FIFO Method.
        """,
    )

    @api.constrains("property_cost_method", "property_specific_ident_cost")
    def _validate_specific_ident_cost(self):
        if (
            self.property_specific_ident_cost
            and self.property_cost_method
            and self.property_cost_method != "fifo"
        ):
            raise ValidationError(
                _(
                    "Costing by Lot/Serial requires FIFO as a "
                    "fallback for untracked products"
                )
            )
