# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # Raise an error when trying to change a quant
    # which corresponding stock location is blocked
    @api.constrains("location_id", "quantity")
    def check_location_blocked(self):
        for record in self:
            if record.location_id.is_physical_count_lockdown:
                raise ValidationError(
                    _(
                        "The location %(location)s is blocked and can "
                        "not be used for moving any product."
                    )
                    % {
                        "location": record.location_id.display_name,
                    }
                )
