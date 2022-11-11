# Copyright 2017 Trey, Kilobytes de Soluciones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    supplier_reference = fields.Char(
        string="Supplier Reference Available in PO",
        help="This field adds the supplier reference added in related purchase order",
    )
