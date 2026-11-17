from odoo import api, models
from odoo.tools import formatLang


class StockLot(models.Model):
    _inherit = "stock.lot"

    @api.depends_context("show_available_qty", "reservation_location_id")
    def _compute_display_name(self):
        return super()._compute_display_name()

    def name_get(self):
        result = super().name_get()
        if not self.env.context.get("show_available_qty"):
            return result
        location_id = self.env.context.get("reservation_location_id")
        if not location_id:
            return result
        location = self.env["stock.location"].browse(location_id)
        Quant = self.env["stock.quant"]
        names = dict(result)
        for lot in self:
            if not lot.product_id:
                continue
            available = Quant._get_available_quantity(
                lot.product_id,
                location,
                lot_id=lot,
            )
            quantity = formatLang(self.env, available, digits=2)
            names[lot.id] = f"{names[lot.id]} ({quantity} {lot.product_id.uom_id.name})"
        return [(lot.id, names[lot.id]) for lot in self]
