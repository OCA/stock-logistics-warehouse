# Copyright 2014 Camptocamp, Akretion, Numérigraphe
# Copyright 2016 Sodexis
# Copyright 2019 Sergio Díaz <sergiodm.1989@gmail.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockLogisticsWarehouse(TransactionCase):
    def test01_stock_levels(self):
        """
        Checking that immediately_usable_qty actually reflects the variations
        in stock, both on product and template.
        """
        moveObj = self.env["stock.move"]
        templateObj = self.env["product.template"]
        supplier_location = self.env.ref("stock.stock_location_suppliers")
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        uom_unit = self.env.ref("uom.product_uom_unit")

        # Create product template with 2 variant
        templateAB = templateObj.create(
            {"name": "templAB", "uom_id": uom_unit.id, "type": "product"}
        )
        self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": templateAB.id,
                "attribute_id": self.env.ref("product.product_attribute_2").id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("product.product_attribute_value_3").id,
                            self.env.ref("product.product_attribute_value_4").id,
                        ],
                    )
                ],
            }
        )

        # Create product A and B
        productA = templateAB.product_variant_ids[0]
        productB = templateAB.product_variant_ids[1]

        # Create a stock move from INCOMING to STOCK
        stockMoveInA = moveObj.create(
            {
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
                "name": "MOVE INCOMING -> STOCK ",
                "product_id": productA.id,
                "product_uom": productA.uom_id.id,
                "product_uom_qty": 2,
            }
        )

        stockMoveInB = moveObj.create(
            {
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
                "name": "MOVE INCOMING -> STOCK ",
                "product_id": productB.id,
                "product_uom": productB.uom_id.id,
                "product_uom_qty": 3,
            }
        )

        def compare_product_usable_qty(product, value):
            # Refresh, because the function field is not recalculated between
            # transactions
            product.refresh()
            self.assertEqual(product.immediately_usable_qty, value)

        compare_product_usable_qty(productA, 0)
        compare_product_usable_qty(templateAB, 0)

        stockMoveInA._action_confirm()
        compare_product_usable_qty(productA, 0)
        compare_product_usable_qty(templateAB, 0)

        stockMoveInA._action_assign()
        compare_product_usable_qty(productA, 0)
        compare_product_usable_qty(templateAB, 0)

        stockMoveInA.move_line_ids.write({"qty_done": 2.0})
        stockMoveInA._action_done()
        compare_product_usable_qty(productA, 2)
        compare_product_usable_qty(templateAB, 2)

        # will directly trigger action_done on productB
        stockMoveInB._action_confirm()
        stockMoveInB._action_assign()
        stockMoveInB.move_line_ids.write({"qty_done": 3.0})
        stockMoveInB._action_done()
        compare_product_usable_qty(productA, 2)
        compare_product_usable_qty(productB, 3)
        compare_product_usable_qty(templateAB, 5)

        # Create a stock move from STOCK to CUSTOMER
        stockMoveOutA = moveObj.create(
            {
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "name": " STOCK --> CUSTOMER ",
                "product_id": productA.id,
                "product_uom": productA.uom_id.id,
                "product_uom_qty": 1,
                "state": "confirmed",
            }
        )

        stockMoveOutA._action_confirm()
        stockMoveOutA._action_assign()
        stockMoveOutA.move_line_ids.write({"qty_done": 1.0})
        stockMoveOutA._action_done()
        compare_product_usable_qty(productA, 1)
        compare_product_usable_qty(templateAB, 4)

        # Potential Qty is set as 0.0 by default
        self.assertEquals(templateAB.potential_qty, 0.0)
        self.assertEquals(productA.potential_qty, 0.0)
