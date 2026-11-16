# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleStockReserveRelease(models.TransientModel):
    _name = "sale.stock.reserve.release"
    _description = "Confirm Release of Stock Reservations"

    sale_order_id = fields.Many2one("sale.order", readonly=True)
    reservation_ids = fields.Many2many(
        "stock.reservation",
        string="Stock Reservations",
        readonly=True,
    )

    def button_release(self):
        self.ensure_one()
        self.sale_order_id.release_all_stock_reservation()
