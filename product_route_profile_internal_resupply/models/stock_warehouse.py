# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def _get_inter_warehouse_route_values(self, supplier_warehouse):
        res = super()._get_inter_warehouse_route_values(supplier_warehouse)
        res["internal_supply"] = True
        return res
