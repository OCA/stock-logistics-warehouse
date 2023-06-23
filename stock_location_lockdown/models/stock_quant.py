# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # Raise an error when trying to change a quant
    # which corresponding stock location is blocked
    @api.constrains("location_id", "quantity")
    def check_location_blocked(self):
        for record in self:
            if record.location_id.block_stock_entrance:
                raise ValidationError(
                    _(
                        "The location %(location)s is blocked and can "
                        "not be used for moving the product %(product)s"
                    )
                    % {
                        "location": record.location_id.display_name,
                        "product": record.product_id.display_name,
                    }
                )
