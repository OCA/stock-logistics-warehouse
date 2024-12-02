# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    block_stock_entrance = fields.Boolean(
        help="If this box is checked, putting stock on this location won't be "
        "allowed. Use this to temporarily block stock movements or to enforce "
        "restrictions in both physical and virtual locations."
    )

    # Raise error if the location that you're trying to block
    # has already got quants
    def write(self, values):
        res = super().write(values)

        if "block_stock_entrance" in values and values["block_stock_entrance"]:
            # Unlink zero quants before checking
            # if there are quants on the location
            self.env["stock.quant"]._unlink_zero_quants()
            if self.mapped("quant_ids"):
                raise UserError(
                    self.env._(
                        "It is impossible to prohibit this location from\
                    receiving products as it already contains some."
                    )
                )
        return res
