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
            self._check_responsible_of_inventory()
            # If the option selected is all, this domain will be applied
            domain = [
                ("has_quants", "=", False),
                ("active", "=", True),
                ("type", "=", "product"),
            ]
            if self.product_selection in ["manual", "one"]:
                domain.append(("id", "in", self.product_ids.ids))
            elif self.product_selection == "category":
                domain.append(("categ_id", "=", self.category_id.id))
            elif self.product_selection == "domain":
                domain = self.product_domain
                domain = (
                    domain[:-1]
                    + """,('has_quants', '=', False), ("type", "=", "product"),
                     ("active", "=", True)"""
                    + domain[-1:]
                )
                domain = ast.literal_eval(domain)
            new_quants = self.create_zero_quants(domain)
            res |= new_quants
        return res

    def create_zero_quants(self, domain):
        products = self.env["product.product"].search_read(
            domain, ["id", "tracking", "lot_ids"]
        )
        values = []
        for product in products:
            for location in self.location_ids:
                # If the product is tracked by lot, we create a quant for each lot
                # If the product is not tracked, we create a single quant
                # If the product is tracked but has no lots, we don't create any quant
                if product["tracking"] in ["lot", "serial"] and product.lot_ids:
                    for lot in product.lot_ids:
                        values.append(
                            {
                                "product_id": product["id"],
                                "location_id": location.id,
                                "quantity": 0.0,
                                "lot_id": lot.id,
                                "last_count_date": fields.Datetime.now(),
                            }
                        )
                elif product["tracking"] == "none":
                    values.append(
                        {
                            "product_id": product["id"],
                            "location_id": location.id,
                            "quantity": 0.0,
                            "last_count_date": fields.Datetime.now(),
                        }
                    )
        new_quants = self.env["stock.quant"].create(values)
        return new_quants

    # This method is designed to assing a responsible
    # user to the inventory if it is not assigned
    # this is necessary to avoid _unlink_zero_quants()
    # method to remove quants created by this module
    def _check_responsible_of_inventory(self):
        for record in self:
            if not record.responsible_id:
                record.responsible_id = self.env.user
