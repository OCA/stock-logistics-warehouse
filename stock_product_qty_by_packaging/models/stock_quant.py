# Copyright 2020 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# @author: Sébastien Alix <sebastien.alix@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockQuant(models.Model):
    _name = "stock.quant"
    _inherit = ["stock.quant", "product.qty_by_packaging.mixin"]

    _qty_by_pkg__qty_field_name = "quantity"
