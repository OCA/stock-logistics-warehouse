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
                "is_storable": True,
                "tracking": "none",
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

    def test_product_packaging_quantity(self):
        """Test product packaging quantity workflow in stock move lines."""
        picking_f = Form(self.env["stock.picking"])
        picking_f.partner_id = self.partner
        picking_f.picking_type_id = self.picking_type_out
        with picking_f.move_ids_without_package.new() as move_f:
            move_f.location_id = self.stock_location  # Force WH/Stock location
            move_f.product_id = self.product
            move_f.product_uom_qty = 1.0
            move_f.product_packaging_id = self.packaging
        picking = picking_f.save()
        self.assertEqual(picking.state, "draft")
        self.assertEqual(picking.move_ids_without_package.product_packaging_qty, 0.2)
        picking.action_confirm()
        picking.action_assign()
        # No quant to reserve
        self.assertEqual(
            picking.move_ids_without_package.product_packaging_quantity, 0.0
        )
        picking.do_unreserve()
        # Add quant
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 10
        )
        # Disable Automatic Done Packaging Calculation
        picking.picking_type_id.automatic_done_packaging_calculation = False
        picking.action_assign()
        self.assertEqual(
            picking.move_ids_without_package.product_packaging_quantity, 0.0
        )
        picking.do_unreserve()
        # Re-Enable Automatic Done Packaging Calculation
        picking.picking_type_id.automatic_done_packaging_calculation = True
        # Initial packaging quantity should be set
        picking.action_assign()
        self.assertEqual(
            picking.move_ids_without_package.product_packaging_quantity, 0.2
        )
        picking.picking_type_id.automatic_done_packaging_calculation = False
        # Allow to modify the packaging quantity
        picking.move_ids_without_package.write({"product_packaging_quantity": 1.0})
        picking.move_ids_without_package.write({"quantity": 2.0})
        self.assertRecordValues(
            picking.move_ids_without_package,
            [
                {
                    "product_id": self.product.id,
                    "product_packaging_id": self.packaging.id,
                    "product_packaging_qty": 0.2,
                    "product_packaging_quantity": 1.0,
                    "product_uom_qty": 1,
                    "quantity": 2.0,
                }
            ],
        )
        picking.button_validate()

    def test_product_packaging_quantity_propagation(self):
        """Test product packaging quantity is propagated to the dest move lines."""
        self.pack_location.active = True
        picking_step2 = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "location_id": self.pack_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        dest = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 10,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_step2.id,
                "location_id": self.pack_location.id,
                "location_dest_id": self.customer_location.id,
                "state": "waiting",
                "procure_method": "make_to_order",
                "product_packaging_id": self.packaging.id,
            }
        )
        picking_step1 = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.pack_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 10,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_step1.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.pack_location.id,
                "move_dest_ids": [(4, dest.id)],
                "state": "confirmed",
                "product_packaging_id": self.packaging.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock_location, 10
        )
        # Step 1
        picking_step1.action_confirm()
        picking_step1.action_assign()
        # Force the packaging quantity to 3.0 to test propagation
        picking_step1.move_ids_without_package.write(
            {"product_packaging_quantity": 3.0}
        )
        picking_step1.button_validate()
        self.assertRecordValues(
            picking_step1.move_ids_without_package,
            [
                {
                    "product_id": self.product.id,
                    "product_packaging_id": self.packaging.id,
                    "product_packaging_qty": 2.0,
                    "product_uom_qty": 10.0,
                    "quantity": 10.0,
                    "product_packaging_quantity": 3.0,
                }
            ],
        )
        # Step 2
        picking_step2.action_confirm()
        picking_step2.action_assign()
        self.assertRecordValues(
            picking_step2.move_ids_without_package,
            [
                {
                    "product_id": self.product.id,
                    "product_packaging_id": self.packaging.id,
                    "product_packaging_qty": 2.0,
                    "product_uom_qty": 10.0,
                    "quantity": 10.0,
                    "product_packaging_quantity": 3.0,
                }
            ],
        )
