# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockInventoryLine(models.Model):

    _name = "stock.inventory.line"
    _inherit = ["stock.inventory.line", "product.qty_by_packaging.mixin"]

    _qty_by_pkg__qty_field_name = "theoretical_qty"
