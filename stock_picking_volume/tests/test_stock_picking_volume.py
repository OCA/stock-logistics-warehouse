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
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Unittest P1",
                "product_length": 10.0,
                "product_width": 5.0,
                "product_height": 3.0,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.product = cls.product_template.product_variant_ids
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
        self.picking.move_line_ids.qty_done = 1
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
        self.picking.move_line_ids.qty_done = 1
        self.picking.button_validate()
        self.picking.action_cancel()
        self.assertEqual(self.picking.volume, 750)
