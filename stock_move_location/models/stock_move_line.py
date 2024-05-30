# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _reservation_is_updatable(self, quantity, reserved_quant):
        res = super()._reservation_is_updatable(quantity, reserved_quant)
        if (
            self.env.context.get("planned")
            and self.product_id.tracking != "serial"
            and self.location_id.id == reserved_quant.location_id.id
            and self.lot_id.id == reserved_quant.lot_id.id
            and self.package_id.id == reserved_quant.package_id.id
            and self.owner_id.id == reserved_quant.owner_id.id
        ):
            return True
        return res
