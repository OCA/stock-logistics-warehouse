# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import SavepointCase


class TestReservationBasedOnPlannedConsumedDate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.output_loc = cls.env.ref("stock.stock_location_output")

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_ship"})
        cls.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )
        cls.location_1 = cls.env["stock.location"].create(
            {"name": "loc1", "location_id": cls.warehouse.lot_stock_id.id}
        )
        cls.location_2 = cls.env["stock.location"].create(
            {"name": "loc2", "location_id": cls.warehouse.lot_stock_id.id}
        )

        product_attribute_packaging = (
            cls.env["product.attribute"].sudo().create({"name": "Packaging"})
        )
        (product_attribute_value_disposable, product_attribute_value_reusable,) = (
            cls.env["product.attribute.value"]
            .sudo()
            .create(
                [
                    {
                        "attribute_id": product_attribute_packaging.id,
                        "name": "Disposable",
                    },
                    {
                        "attribute_id": product_attribute_packaging.id,
                        "name": "Modified atmosphere",
                    },
                ]
            )
        )
        cls.product_template = (
            cls.env["product.template"]
            .sudo()
            .create(
                [
                    {
                        "name": "A Dish",
                        "tracking": "lot",
                        "use_expiration_date": True,
                        "type": "product",
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
                                            [
                                                product_attribute_value_disposable.id,
                                                product_attribute_value_reusable.id,
                                            ],
                                        ),
                                    ],
                                },
                            ),
                        ],
                    }
                ]
            )
        )
        cls.product_template.categ_id.route_ids |= cls.env[
            "stock.location.route"
        ].search([("name", "ilike", "deliver in 2")])
        (
            cls.product_disposable,
            cls.product_atmosphere,
        ) = cls.product_template.product_variant_ids

        # (
        #     cls.product_disposable | cls.product_atmosphere
        # ).write({"tracking": "lot", "use_expiration_date": True})

        cls.lot_disposable_0125 = cls.env["stock.production.lot"].create(
            {
                "name": "lot disposable",
                "expiration_date": "2024-01-25",
                "product_id": cls.product_disposable.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.lot_atmosphere_0125 = cls.env["stock.production.lot"].create(
            {
                "name": "lot disposable",
                "expiration_date": "2024-01-25",
                "product_id": cls.product_atmosphere.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.lot_atmosphere_0202 = cls.env["stock.production.lot"].create(
            {
                "name": "lot atmosphere",
                "expiration_date": "2024-02-02",
                "product_id": cls.product_atmosphere.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product_atmosphere.id,
                "location_id": cls.location_2.id,
                "lot_id": cls.lot_atmosphere_0125.id,
                "quantity": 3,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product_disposable.id,
                "location_id": cls.location_1.id,
                "lot_id": cls.lot_disposable_0125.id,
                "quantity": 2,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product_atmosphere.id,
                "location_id": cls.location_2.id,
                "lot_id": cls.lot_atmosphere_0202.id,
                "quantity": 7,
            }
        )

    def test_procurement_using_product_template(self):
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_template,
                    1.0,
                    self.product_template.uom_id,
                    self.customer_loc,
                    "Test",
                    "Odoo test",
                    self.env.company,
                    {},
                )
            ]
        )
        moves = self.env["stock.move"].search(
            [("product_id", "=", self.product_disposable.id)]
        )
        self.assertEqual(len(moves), 2, "Expected two stock.move: 1 pick + 1 ship")
