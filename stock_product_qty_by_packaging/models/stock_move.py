# Copyright 2020 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# @author: Sébastien Alix <sebastien.alix@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "product.qty_by_packaging.mixin"]

    _qty_by_pkg__qty_field_name = "product_uom_qty"
