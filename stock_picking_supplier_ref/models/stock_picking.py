# Copyright 2017 Trey, Kilobytes de Soluciones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    supplier_reference = fields.Char(
        string="Supplier Delivery Reference",
        help="Enter the supplier's delivery note or shipment reference related "
        "to this receipt. This does not sync automatically with the supplier "
        "reference in the purchase order.",
    )
