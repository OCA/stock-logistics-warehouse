# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2021 Xtendoo - Manuel Calero

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    expiration_date = fields.Datetime(
        related="lot_id.expiration_date",
    )
    use_date = fields.Datetime(
        related="lot_id.use_date",
    )
    alert_date = fields.Datetime(
        related="lot_id.alert_date",
    )
