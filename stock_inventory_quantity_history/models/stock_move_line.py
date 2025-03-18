# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    inventory_theoretical_qty = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        help="Theoretical Quantity right before the inventory",
    )
    inventory_real_qty = fields.Float(
        digits="Product Unit of Measure",
        readonly=True,
        help="Real Quantity at the time of the inventory",
    )
