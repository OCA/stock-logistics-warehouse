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
        picking_f.picking_type_id = self.env.ref("stock.picking_type_out")
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
