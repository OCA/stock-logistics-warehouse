# © 2023 FactorLibre - Hugo Córdoba <hugo.cordoba@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sale_reserve_id = fields.Many2one("sale.order", "Sale Stock Reserve")
