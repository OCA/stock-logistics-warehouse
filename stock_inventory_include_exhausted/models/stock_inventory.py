# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    include_exhausted = fields.Boolean(
        string="Include Exhausted",
        help="If you select this option, you will receive the "
        "out of stock inventory products",
    )

    def _get_inventory_lines_values(self):
        vals = super()._get_inventory_lines_values()

        if self.include_exhausted:
            domain = [("qty_available", "=", 0), ("type", "=", "product")]
            if self.product_ids:
                domain.append(("id", "in", self.product_ids.ids))
            exhausted_products = self.env["product.product"].search(domain)
            vals_dic = {
                "inventory_id": self.id,
                "company_id": self.company_id.id,
                "product_qty": 0,
                "theoretical_qty": 0,
            }
            vals_dic["location_id"] = (
                self.env["stock.warehouse"]
                .search([("company_id", "=", vals_dic["company_id"])], limit=1)
                .lot_stock_id.id
            )
            for product in exhausted_products:
                vals_dic["product_id"] = product.id
                vals_dic["product_uom_id"] = product.uom_id.id

                vals.append(vals_dic.copy())

        return vals
