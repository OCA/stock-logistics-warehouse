# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AddMultiProducts(models.TransientModel):
    _name = "stock.add.multi.product"
    _description = "Add Multi Products"

    product_ids = fields.Many2many("product.product")

    def add_products(self):
        cost_adj_line_obj = self.env["stock.cost.adjustment.line"]
        for rec in self:
            for product in rec.product_ids:
                cost_line_id = cost_adj_line_obj.create(
                    [
                        {
                            "product_id": product.id,
                            "cost_adjustment_id": self._context.get(
                                "default_cost_adjustment_id"
                            ),
                        }
                    ]
                )
                cost_line_id._set_costs()
