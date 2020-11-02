# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    block_stock_entrance = fields.Boolean(
        help="if this box is checked, putting stock on this location won't be "
        "allowed. Usually used for a virtual location that has "
        "childrens."
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
                    _(
                        "It is impossible to prohibit this location from\
                    receiving products as it already contains some."
                    )
                )
        return res
