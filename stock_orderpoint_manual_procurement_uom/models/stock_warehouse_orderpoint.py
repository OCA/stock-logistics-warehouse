# Copyright 2018-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_procure_recommended_qty(self, virtual_qty, op_qtys):
        product_qty = super(
            StockWarehouseOrderpoint, self
        )._get_procure_recommended_qty(virtual_qty, op_qtys)
        if self.procure_uom_id:
            product_qty = self.product_id.uom_id._compute_quantity(
                product_qty, self.procure_uom_id
            )
        return product_qty
