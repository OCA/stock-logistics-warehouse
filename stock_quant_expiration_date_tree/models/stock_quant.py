# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2021 Xtendoo - Manuel Calero

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    life_date = fields.Datetime(
        string='End of Life Date',
        related='lot_id.life_date',
    )
    use_date = fields.Datetime(
        string='Best before Date',
        related='lot_id.use_date',
    )
    removal_date = fields.Datetime(
        string='Removal Date',
        related='lot_id.removal_date',
    )
    alert_date = fields.Datetime(
        string='Alert Date',
        related='lot_id.alert_date',
    )
