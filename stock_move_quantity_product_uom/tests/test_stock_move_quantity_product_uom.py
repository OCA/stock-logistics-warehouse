# Copyright 2025 ForgeFlow
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo.tests.common import TransactionCase


class TestStockMOveQuantityProductUom(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.uom_g = cls.env.ref("uom.product_uom_gram")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
                "uom_id": cls.uom_kg.id,
                "uom_po_id": cls.uom_kg.id,
            }
        )

    def test_01_quantity_product_uom_after_validation(self):
        """Test that quantity_product_uom is correct after
        confirming and validating the picking"""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Move",
                            "product_id": self.product.id,
                            "product_uom": self.uom_g.id,
                            "product_uom_qty": 1000,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        move = picking.move_ids[0]
        move.quantity = 1000
        move.picked = True
        picking.button_validate()
        self.assertEqual(move.quantity, 1000)
        self.assertEqual(move.quantity_product_uom, 1.0)
