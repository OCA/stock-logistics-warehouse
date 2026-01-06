# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class TestProductSecondaryUnit(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Active multiple units of measure security group for user
        cls.env.user.groups_id = [(4, cls.env.ref("uom.group_uom").id)]
        cls.StockPicking = cls.env["stock.picking"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.location_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_out.show_operations = True

        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_ton = cls.env.ref("uom.product_uom_ton")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        ProductAttribute = cls.env["product.attribute"]
        ProductAttributeValue = cls.env["product.attribute.value"]
        cls.attribute_color = ProductAttribute.create({"name": "test_color"})
        cls.attribute_value_white = ProductAttributeValue.create(
            {"name": "test_white", "attribute_id": cls.attribute_color.id}
        )
        cls.attribute_value_black = ProductAttributeValue.create(
            {"name": "test_black", "attribute_id": cls.attribute_color.id}
        )
        cls.serial_product = cls.env["product.product"].create(
            {
                "name": "Serial Product",
                "uom_id": cls.product_uom_unit.id,
                "type": "consu",
                "is_storable": True,
                "tracking": "serial",
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "code": "A",
                            "name": "Double",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 2,
                        },
                    )
                ],
            }
        )
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "type": "consu",
                "is_storable": True,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "code": "A",
                            "name": "unit-500",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        },
                    ),
                    Command.create(
                        {
                            "code": "B",
                            "name": "unit-900",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.9,
                        },
                    ),
                    Command.create(
                        {
                            "code": "C",
                            "name": "box 10",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 10,
                        },
                    ),
                ],
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attribute_color.id,
                            "value_ids": [
                                (4, cls.attribute_value_white.id),
                                (4, cls.attribute_value_black.id),
                            ],
                        },
                    )
                ],
            }
        )
        secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product_template.id)], limit=1
        )
        cls.product_template.product_variant_ids.write(
            {"stock_secondary_uom_id": secondary_unit.id}
        )
        StockQuant = cls.env["stock.quant"]
        cls.quant_white = StockQuant.create(
            {
                "product_id": cls.product_template.product_variant_ids[0].id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )
        cls.quant_black = StockQuant.create(
            {
                "product_id": cls.product_template.product_variant_ids[1].id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )

    def test_01_stock_secondary_unit_template(self):
        self.assertEqual(self.product_template.secondary_unit_qty_available, 0)

    def test_02_stock_secondary_unit_variant(self):
        for variant in self.product_template.product_variant_ids.filtered(
            "product_template_attribute_value_ids"
        ):
            self.assertEqual(variant.secondary_unit_qty_available, 20)

    def test_03_stock_picking_secondary_unit(self):
        StockPicking = self.env["stock.picking"]
        product1 = self.product_template.product_variant_ids[0]
        move_vals = {
            "product_id": product1.id,
            "name": product1.display_name,
            "secondary_uom_id": product1.product_tmpl_id.secondary_uom_ids[0].id,
            "product_uom": product1.uom_id.id,
            "product_uom_qty": 10.0,
            "location_id": self.location_supplier.id,
            "location_dest_id": self.location_stock.id,
        }
        do_vals = {
            "location_id": self.location_supplier.id,
            "location_dest_id": self.location_stock.id,
            "picking_type_id": self.picking_type_in.id,
            "move_ids_without_package": [
                (0, None, move_vals),
                (0, None, move_vals),
            ],  # 2 moves
        }
        delivery_order = StockPicking.create(do_vals)
        delivery_order.action_confirm()
        # Move is merged into 1 line for both stock.move and stock.move.line
        self.assertEqual(len(delivery_order.move_ids), 1)
        self.assertEqual(len(delivery_order.move_line_ids), 1)
        # Qty merged to 20, and secondary unit qty is 40line
        uom_qty = sum(delivery_order.move_ids.mapped("product_uom_qty"))
        secondary_uom_qty = sum(
            delivery_order.move_line_ids.mapped("secondary_uom_qty")
        )
        self.assertEqual(uom_qty, 20.0)
        self.assertEqual(secondary_uom_qty, 40.0)

    def test_picking_secondary_unit(self):
        product = self.product_template.product_variant_ids[0]
        with Form(
            self.StockPicking.with_context(
                planned_picking=True,
                default_picking_type_id=self.picking_type_out.id,
            )
        ) as picking_form:
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
                self.assertEqual(move.product_uom_qty, 0.5)
                move.secondary_uom_qty = 2
                self.assertEqual(move.product_uom_qty, 1)
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[1]
                self.assertEqual(move.product_uom_qty, 1.8)
                move.product_uom_qty = 5
                self.assertAlmostEqual(move.secondary_uom_qty, 5.56, 2)
                # Change uom from stock move line
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[2]
                self.assertEqual(move.product_uom_qty, 10)
                move.product_uom = self.product_uom_ton
                self.assertAlmostEqual(move.secondary_uom_qty, 1000, 2)

        picking = picking_form.save()
        picking.action_confirm()
        stock_move_line = picking.move_line_ids_without_package
        stock_move_line.product_id = product
        stock_move_line.product_uom_id = stock_move_line.product_id.uom_id.id
        stock_move_line.secondary_uom_qty = 1
        stock_move_line.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
        self.assertEqual(stock_move_line.quantity, 0.5)
        stock_move_line.secondary_uom_qty = 2
        self.assertEqual(stock_move_line.quantity, 1)
        stock_move_line.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[1]
        self.assertEqual(stock_move_line.quantity, 1.8)
        stock_move_line.quantity = 5
        self.assertAlmostEqual(stock_move_line.secondary_uom_qty, 5.56, 2)

    def test_secondary_unit_merge_move_diff_uom(self):
        product = self.product_template.product_variant_ids[0]
        with Form(
            self.StockPicking.with_context(
                planned_picking=True,
                default_picking_type_id=self.picking_type_out.id,
            )
        ) as picking_form:
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[1]
        picking = picking_form.save()
        picking.action_confirm()
        self.assertEqual(len(picking.move_ids), 2)

    def test_secondary_unit_merge_move_same_uom(self):
        product = self.product_template.product_variant_ids[0]
        with Form(
            self.StockPicking.with_context(
                planned_picking=True,
                default_picking_type_id=self.picking_type_out.id,
            )
        ) as picking_form:
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.secondary_uom_qty = 1
                move.secondary_uom_id = product.product_tmpl_id.secondary_uom_ids[0]
        picking = picking_form.save()
        picking.action_confirm()
        self.assertEqual(len(picking.move_ids), 1)
        self.assertEqual(picking.move_ids.secondary_uom_qty, 2)

    def test_stock_quant_secondary_uom_qty(self):
        template = self.env["product.template"].create(
            {
                "name": "test",
                "uom_id": self.product_uom_unit.id,
                "is_storable": True,
                "secondary_uom_ids": [
                    Command.create(
                        {
                            "code": "T",
                            "name": "unit-2",
                            "uom_id": self.product_uom_unit.id,
                            "factor": 0.5,
                        },
                    ),
                    Command.create(
                        {
                            "code": "U",
                            "name": "unit-4",
                            "uom_id": self.product_uom_unit.id,
                            "factor": 0.25,
                        },
                    ),
                ],
            }
        )
        secondary_uom_1 = template.secondary_uom_ids[0]
        secondary_uom_2 = template.secondary_uom_ids[1]
        product = template.product_variant_ids[0]
        # Test variant's secondary UoM is applied to quant
        product.stock_secondary_uom_id = secondary_uom_1
        quant = self.env["stock.quant"].create(
            {
                "location_id": self.location_stock.id,
                "product_id": product.id,
                "inventory_quantity": 10,
            }
        )
        quant.action_apply_inventory()
        self.assertEqual(quant.secondary_uom_id, secondary_uom_1)
        self.assertEqual(quant.secondary_uom_qty, 20)
        # Test template's secondary UoM syncs to variant (single-variant product)
        template.stock_secondary_uom_id = secondary_uom_2
        self.assertEqual(product.stock_secondary_uom_id, secondary_uom_2)
        self.assertEqual(quant.secondary_uom_id, secondary_uom_2)
        self.assertEqual(quant.secondary_uom_qty, 40)

    def test_action_generate_lot_line_vals(self):
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.location_supplier.id,
                "location_dest_id": self.location_stock.id,
                "picking_type_id": self.picking_type_in.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.serial_product.id,
                "product_uom_qty": 2.0,
                "picking_id": picking.id,
                "location_id": self.location_supplier.id,
                "location_dest_id": self.location_stock.id,
                "secondary_uom_id": self.serial_product.secondary_uom_ids[0].id,
            }
        )
        # Import serials
        vals = self.env["stock.move"].action_generate_lot_line_vals(
            {
                "default_tracking": "serial",
                "default_product_id": move.product_id.id,
                "default_picking_id": picking.id,
                "default_location_dest_id": self.location_stock.id,
            },
            "import",
            "",
            0,
            "001\n002",
        )
        self.assertEqual(len(vals), 2)
        self.assertEqual(vals[0]["lot_name"], "001")
        self.assertEqual(
            vals[0]["secondary_uom_id"]["id"],
            self.serial_product.secondary_uom_ids[0].id,
        )
        self.assertEqual(vals[0]["quantity"], 1)
        self.assertEqual(vals[0]["secondary_uom_qty"], 0.5)
        self.assertEqual(vals[1]["lot_name"], "002")
        self.assertEqual(
            vals[1]["secondary_uom_id"]["id"],
            self.serial_product.secondary_uom_ids[0].id,
        )
        self.assertEqual(vals[1]["quantity"], 1)
        self.assertEqual(vals[1]["secondary_uom_qty"], 0.5)
        # Generate serials
        vals = self.env["stock.move"].action_generate_lot_line_vals(
            {
                "default_tracking": "serial",
                "default_product_id": move.product_id.id,
                "default_picking_id": picking.id,
                "default_location_dest_id": self.location_stock.id,
            },
            "generate",
            "001",
            2,
            False,
        )
        self.assertEqual(len(vals), 2)
        self.assertEqual(vals[0]["lot_name"], "001")
        self.assertEqual(
            vals[0]["secondary_uom_id"]["id"],
            self.serial_product.secondary_uom_ids[0].id,
        )
        self.assertEqual(vals[0]["quantity"], 1)
        self.assertEqual(vals[0]["secondary_uom_qty"], 0.5)
        self.assertEqual(vals[1]["lot_name"], "002")
        self.assertEqual(
            vals[1]["secondary_uom_id"]["id"],
            self.serial_product.secondary_uom_ids[0].id,
        )
        self.assertEqual(vals[1]["quantity"], 1)
        self.assertEqual(vals[1]["secondary_uom_qty"], 0.5)
