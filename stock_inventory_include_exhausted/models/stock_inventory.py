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
            non_exhausted_set = {(l["product_id"], l["location_id"]) for l in vals}
            if self.product_ids:
                product_ids = self.product_ids.ids
            else:
                product_ids = self.env["product.product"].search_read(
                    [
                        "|",
                        ("company_id", "=", self.company_id.id),
                        ("company_id", "=", False),
                        ("type", "=", "product"),
                        ("active", "=", True),
                    ],
                    ["id"],
                )
                product_ids = [p["id"] for p in product_ids]
            if self.location_ids:
                location_ids = self.location_ids.ids
            else:
                location_ids = (
                    self.env["stock.warehouse"]
                    .search([("company_id", "=", self.company_id.id)])
                    .lot_stock_id.ids
                )
            for product in product_ids:
                for location_id in location_ids:
                    if (product, location_id) not in non_exhausted_set:
                        vals.append(
                            {
                                "inventory_id": self.id,
                                "product_id": product,
                                "location_id": location_id,
                                "theoretical_qty": 0,
                            }
                        )
        return vals
