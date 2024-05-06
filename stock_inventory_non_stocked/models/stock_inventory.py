# Copyright 2024 Ivan Perez <iperez@coninpe.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast

from odoo import fields, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    create_non_stocked = fields.Boolean(
        string="Create non stocked products",
        help="If you select this option, a new quant with zero "
        "quantity will be created for products without any stock and any quants",
    )

    def _get_quants(self, locations):
        res = super(StockInventory, self)._get_quants(locations)
        if self.create_non_stocked:
            if self.product_selection == "all":
                product_ids = self.env["product.product"].search(
                    [
                        ("has_quants", "=", False),
                        ("active", "=", True),
                        ("type", "=", "product"),
                    ]
                )
                new_quants = self.create_zero_quants(product_ids)
                res |= new_quants
            elif self.product_selection in ["manual", "one"]:
                product_ids = self.product_ids.filtered(lambda x: not x.has_quants)
                new_quants = self.create_zero_quants(product_ids)
                res |= new_quants
            elif self.product_selection == "category":
                product_ids = self.env["product.product"].search(
                    [
                        ("has_quants", "=", False),
                        ("active", "=", True),
                        ("type", "=", "product"),
                        ("categ_id", "=", self.category_id.id),
                    ]
                )
                new_quants = self.create_zero_quants(product_ids)
                res |= new_quants
            elif self.product_selection == "domain":
                domain = self.product_domain
                domain = (
                    domain[:-1]
                    + """,('has_quants', '=', False), ("type", "=", "product"), ("active", "=", True)"""
                    + domain[-1:]
                )
                domain = ast.literal_eval(domain)
                product_ids = self.env["product.product"].search(domain)
                new_quants = self.create_zero_quants(product_ids)
                res |= new_quants
        return res

    def create_zero_quants(self, products):
        new_quants = self.env["stock.quant"]
        for product in products:
            for location in self.location_ids:
                # If the product is tracked by lot, we create a quant for each lot
                # If the product is not tracked, we create a single quant
                # If the product is tracked but has no lots, we don't create any quant
                if product.tracking == "lot" and product.lot_ids:
                    for lot in product.lot_ids:
                        new_quants |= self.env["stock.quant"].create(
                            {
                                "product_id": product.id,
                                "location_id": location.id,
                                "quantity": 0.0,
                                "lot_id": lot.id,
                                "user_id": self.env.uid,
                                "last_count_date": fields.Datetime.now(),
                            }
                        )
                elif product.tracking == "none":
                    new_quants |= self.env["stock.quant"].create(
                        {
                            "product_id": product.id,
                            "location_id": location.id,
                            "quantity": 0.0,
                            "user_id": self.env.uid,
                            "last_count_date": fields.Datetime.now(),
                        }
                    )
        return new_quants
