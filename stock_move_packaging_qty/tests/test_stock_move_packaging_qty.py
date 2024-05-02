# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockMovePackagingQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.user.groups_id |= cls.env.ref("product.group_stock_packaging")
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "consu",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.wh = cls.env["stock.warehouse"].create(
            {"name": "Base Warehouse", "code": "TESTWH"}
        )
        cls.categ_unit = cls.env.ref("uom.product_uom_categ_unit")
        cls.uom_unit = cls.env["uom.uom"].search(
            [("category_id", "=", cls.categ_unit.id), ("uom_type", "=", "reference")],
            limit=1,
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.pack_location = cls.env.ref("stock.location_pack_zone")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def test_product_packaging_qty(self):
        move = self.env["stock.move"].create(
            {
                "name": "Move",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.wh.lot_stock_id.id,
                "partner_id": self.partner.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 3.0,
                "price_unit": 10.0,
            }
        )
        move.write({"product_packaging_id": self.packaging.id})
        move._onchange_product_packaging()
        self.assertEqual(move.product_uom_qty, 5.0)
        self.assertEqual(move.product_packaging_qty, 1.0)
        move.write({"product_packaging_qty": 3.0})
        self.assertEqual(move.product_uom_qty, 15.0)

    def test_product_uom_qty_change(self):
        picking_f = Form(self.env["stock.picking"])
        picking_f.partner_id = self.partner
        picking_f.picking_type_id = self.picking_type_out
        with picking_f.move_ids_without_package.new() as move_f:
            move_f.product_id = self.product
            self.assertEqual(move_f.product_uom_qty, 1)
            self.assertEqual(move_f.product_packaging_qty, 0)
            self.assertFalse(move_f.product_packaging_id)
            move_f.product_packaging_id = self.packaging
            self.assertEqual(move_f.product_uom_qty, 5)
            self.assertEqual(move_f.product_packaging_qty, 1)
        picking = picking_f.save()
        self.assertEqual(picking.state, "draft")
        picking.action_assign()
        picking.action_set_quantities_to_reservation()
        self.assertRecordValues(
            picking.move_ids_without_package,
            [
                {
                    "product_id": self.product.id,
                    "product_packaging_id": self.packaging.id,
                    "product_packaging_qty_done": 1,
                    "product_packaging_qty": 1,
                    "product_uom_qty": 5,
                }
            ],
        )
        picking.button_validate()

    def test_product_packaging_qty_reserved(self):
        """Test that the product packaging quantity reserved is correctly set."""
        product_a = self.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        packaging_product_a = self.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": product_a.id, "qty": 5.0}
        )
        self.pack_location.active = True
        MoveObj = self.env["stock.move"]
        picking_client = self.env["stock.picking"].create(
            {
                "location_id": self.pack_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        dest = MoveObj.create(
            {
                "name": product_a.name,
                "product_id": product_a.id,
                "product_uom_qty": 10,
                "product_uom": product_a.uom_id.id,
                "picking_id": picking_client.id,
                "location_id": self.pack_location.id,
                "location_dest_id": self.customer_location.id,
                "state": "waiting",
                "procure_method": "make_to_order",
                "product_packaging_id": packaging_product_a.id,
            }
        )
        picking_pick = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.pack_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        MoveObj.create(
            {
                "name": product_a.name,
                "product_id": product_a.id,
                "product_uom_qty": 10,
                "product_uom": product_a.uom_id.id,
                "picking_id": picking_pick.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.pack_location.id,
                "move_dest_ids": [(4, dest.id)],
                "state": "confirmed",
                "product_packaging_id": packaging_product_a.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            product_a, self.stock_location, 10
        )
        picking_pick.action_assign()
        self.assertRecordValues(
            picking_pick.move_ids_without_package,
            [
                {
                    "product_id": product_a.id,
                    "product_packaging_id": packaging_product_a.id,
                    "product_packaging_qty": 2,
                    "product_uom_qty": 10,
                    "quantity_done": 0,
                    "product_packaging_qty_done": 0,
                }
            ],
        )
        self.assertRecordValues(
            picking_pick.move_line_ids_without_package,
            [
                {
                    "product_id": product_a.id,
                    "product_packaging_id": packaging_product_a.id,
                    "reserved_uom_qty": 10,
                    "product_packaging_qty_reserved": 2,
                    "qty_done": 0,
                    "product_packaging_qty_done": 0,
                }
            ],
        )
        picking_pick.action_set_quantities_to_reservation()
        self.assertRecordValues(
            picking_pick.move_ids_without_package,
            [
                {
                    "product_id": product_a.id,
                    "product_packaging_id": packaging_product_a.id,
                    "product_packaging_qty": 2,
                    "product_uom_qty": 10,
                    "quantity_done": 10,
                    "product_packaging_qty_done": 2,
                }
            ],
        )
        picking_pick._action_done()
        picking_client.action_assign()
        self.assertRecordValues(
            picking_client.move_ids_without_package,
            [
                {
                    "product_id": product_a.id,
                    "product_packaging_id": packaging_product_a.id,
                    "product_packaging_qty": 2,
                    "product_uom_qty": 10,
                    "quantity_done": 0,
                    "product_packaging_qty_done": 0,
                }
            ],
        )
        self.assertRecordValues(
            picking_client.move_line_ids_without_package,
            [
                {
                    "product_id": product_a.id,
                    "product_packaging_id": packaging_product_a.id,
                    "reserved_uom_qty": 10,
                    "product_packaging_qty_reserved": 2,
                    "qty_done": 0,
                    "product_packaging_qty_done": 0,
                }
            ],
        )
        picking_pick.action_set_quantities_to_reservation()
        self.assertRecordValues(
            picking_pick.move_ids_without_package,
            [
                {
                    "product_id": product_a.id,
                    "product_packaging_id": packaging_product_a.id,
                    "product_packaging_qty": 2,
                    "product_uom_qty": 10,
                    "quantity_done": 10,
                    "product_packaging_qty_done": 2,
                }
            ],
        )
