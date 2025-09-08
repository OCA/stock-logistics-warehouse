# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    use_maturity_date = fields.Boolean(related="product_id.use_maturity_date")
    maturity_date = fields.Datetime()
    product_maturity_alert = fields.Boolean(
        compute="_compute_product_maturity_alert",
        help="The product isn't mature and can't be reserved",
    )

    @api.depends("maturity_date")
    def _compute_product_maturity_alert(self):
        current_date = fields.Datetime.now()
        self.product_maturity_alert = False
        for lot in self.filtered("maturity_date"):
            lot.product_maturity_alert = lot.maturity_date > current_date
