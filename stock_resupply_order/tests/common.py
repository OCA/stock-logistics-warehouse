# Copyright 2025 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests import SavepointCase


class StockResupplyOrderBaseCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location = cls.env.ref("stock_resupply_order.location_dest_demo")
        cls.product_attribute = (
            cls.env["product.attribute"].sudo().create({"name": "Packaging"})
        )
        cls.product_attribute_value = (
            cls.env["product.attribute.value"]
            .sudo()
            .create({"attribute_id": cls.product_attribute.id, "name": "Disposable"})
        )
        product_attribute_packaging = (
            cls.env["product.attribute"].sudo().create({"name": "Packaging"})
        )
        product_attribute_value_disposable = (
            cls.env["product.attribute.value"]
            .sudo()
            .create(
                {
                    "attribute_id": product_attribute_packaging.id,
                    "name": "Disposable",
                },
            )
        )

        cls.product_template = (
            cls.env["product.template"]
            .sudo()
            .create(
                {
                    "name": "A product",
                    "tracking": "lot",
                    "type": "product",
                    "default_code": "CODE123",
                    "attribute_line_ids": [
                        (
                            0,
                            0,
                            {
                                "attribute_id": product_attribute_packaging.id,
                                "value_ids": [
                                    (
                                        6,
                                        0,
                                        [product_attribute_value_disposable.id],
                                    ),
                                ],
                            },
                        ),
                    ],
                }
            )
        )
        cls.product_template.categ_id.route_ids = [
            (
                4,
                cls.env.ref("stock_resupply_order.route_demo").id,
            ),
        ]
        cls.product_disposable = cls.product_template.product_variant_ids[0]
