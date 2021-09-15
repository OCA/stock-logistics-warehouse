# Copyright 2020 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# @author: Sébastien Alix <sebastien.alix@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ["stock.move.line", "product.qty_by_packaging.mixin"]

    _qty_by_pkg__qty_field_name = "product_qty"
