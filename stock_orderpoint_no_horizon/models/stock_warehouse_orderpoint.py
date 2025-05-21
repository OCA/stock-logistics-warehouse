# Copyright 2023 Camptocamp SA
# @author: Jacques-Etienne Baudoux (BCIM) <je@bcim.be>

from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_product_context(self, visibility_days=0):
        ctx = super()._get_product_context(visibility_days)
        if "to_date" in ctx:
            del ctx["to_date"]
        return ctx
