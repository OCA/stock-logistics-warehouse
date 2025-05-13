# Copyright Iryna Vyshnevska 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.base.tests.common import BaseCommon


class TestFillwithStock(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.pack_location = cls.env.ref("stock.location_pack_zone")
        cls.shelf1_location = cls.env["stock.location"].create(
            {
                "name": "Test location",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
            }
        )

        cls.env["stock.quant"].create(
            {
                "product_id": cls.product1.id,
                "location_id": cls.shelf1_location.id,
                "quantity": 5.0,
                "reserved_quantity": 0.0,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product1.id,
                "location_id": cls.shelf1_location.id,
                "quantity": 10.0,
                "reserved_quantity": 5.0,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product2.id,
                "location_id": cls.shelf1_location.id,
                "quantity": 5.0,
                "reserved_quantity": 0.0,
            }
        )

    def test_fillwithstock(self):
        picking_stock_pack = self.env["stock.picking"].create(
            {
                "location_id": self.shelf1_location.id,
                "location_dest_id": self.pack_location.id,
                "picking_type_id": self.env.ref("stock.picking_type_internal").id,
            }
        )
        self.assertFalse(picking_stock_pack.move_ids)
        picking_stock_pack.button_fillwithstock()
        # picking filled with quants in bin
        self.assertEqual(len(picking_stock_pack.move_ids), 2)
        self.assertEqual(
            picking_stock_pack.move_ids.filtered(
                lambda m: m.product_id == self.product1
            ).product_uom_qty,
            15.0,
        )
        self.assertEqual(
            picking_stock_pack.move_ids.filtered(
                lambda m: m.product_id == self.product2
            ).product_uom_qty,
            5.0,
        )
