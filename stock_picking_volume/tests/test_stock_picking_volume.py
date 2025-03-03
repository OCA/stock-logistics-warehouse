# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingVolume(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.wh = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "BWH",
            }
        )
        cls.loc_stock = cls.wh.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.product = cls._create_product("Unittest P1", 10.0, 5.0, 3.0)
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _create_product(cls, name, length, width, height):
        product = cls.env["product.product"].create(
            {
                "name": name,
                "product_length": length,
                "product_width": width,
                "product_height": height,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "dimensional_uom_id": cls.env.ref("uom.product_uom_meter").id,
                "is_storable": True,
            }
        )
        return product

    def _set_product_qty(self, product, qty):
        self.env["stock.quant"]._update_available_quantity(product, self.loc_stock, qty)

    def test_picking_draft_volume(self):
        """
        Data:
            one picking with one move line with 5 units of product
        Test Case:
            get the volume of the picking
        Expected result:
            volume is 5 * 10 * 5 * 3 = 750
            The volume is computed from the expected quantity
        """
        self.assertEqual(self.picking.volume, 750)

    def test_picking_partially_available_volume(self):
        """
        Data:
            one picking with one move line with 5 units of product
        Test Case:
            set 1 unit of product as available
            get the volume of the picking
        Expected result:
            volume is 1 * 10 * 5 * 3 = 150
            The volume is computed from the available quantity
        """
        self._set_product_qty(self.product, 1)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.assertEqual(self.picking.volume, 150)

    def test_picking_available_volume(self):
        """
        Data:
            one picking with one move line with 5 units of product
        Test Case:
            set 5 unit of product as available
            get the volume of the picking
        Expected result:
            volume is 5 * 10 * 5 * 3 = 750
            The volume is computed from the expected quantity
        """
        self._set_product_qty(self.product, 5)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.assertEqual(self.picking.volume, 750)

    def test_picking_done_volume(self):
        """
        Data:
            one picking with one move line with 5 units of product
        Test Case:
            set 1 unit of product as done
            confirm the picking
            get the volume of the picking
        Expected result:
            volume is 1 * 10 * 5 * 3 = 150
            The volume is computed from the done quantity
        """
        self._set_product_qty(self.product, 1)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_line_ids.quantity = 1
        self.picking.button_validate()
        self.assertEqual(self.picking.volume, 150)

    def test_picking_cancel_volume(self):
        """
        Data:
            one picking with one move line with 5 units of product
        Test Case:
            set 1 unit of product as done
            confirm the picking
            cancel the picking
            get the volume of the picking
        Expected result:
            volume is 5 * 10 * 5 * 3 = 750
            The volume is computed from the expected quantity
        """
        self._set_product_qty(self.product, 1)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_line_ids.quantity = 1
        self.picking.button_validate()
        self.picking.action_cancel()
        self.assertEqual(self.picking.volume, 750)

    def test_picking_with_canceled_move(self):
        """
        Data:
            one picking with two move lines with 5 units of product
        Test Case:
            set 5 unit of product as available
            get the volume of the picking
        Expected result:
            volume is 5 * 10 * 5 * 3 = 750
            The volume is computed from the expected quantity
        """
        product2 = self._create_product("Product2", 10.0, 5.0, 3.0)
        self._set_product_qty(self.product, 5)
        self._set_product_qty(product2, 5)
        self.picking.write(
            {
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product2.name,
                            "product_id": product2.id,
                            "product_uom": product2.uom_id.id,
                            "product_uom_qty": 5.0,
                            "location_id": self.loc_stock.id,
                            "location_dest_id": self.loc_customer.id,
                        },
                    )
                ]
            }
        )
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.invalidate_model()
        self.assertEqual(self.picking.volume, 750 * 2)
        self.picking.move_ids[1]._action_cancel()
        self.picking.invalidate_model()
        self.assertEqual(self.picking.volume, 750)

    def test_product_volume(self):
        self.assertEqual(self.product._get_volume_for_qty(5), 750)
        from_uom = self.env.ref("uom.product_uom_dozen")
        self.assertEqual(
            self.product._get_volume_for_qty(5 * from_uom.factor, from_uom), 750
        )
