# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase


class TestLocationArchiveConstraint(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.product_1 = cls._create_product(cls, "Product 1")
        cls.product_2 = cls._create_product(cls, "Product 2")
        stock_location_stock = cls.env.ref("stock.stock_location_stock")
        cls.stock_location = cls._create_stock_location(
            cls, "%s (Copy)" % (stock_location_stock.name)
        )
        cls.stock_location_child = cls._create_stock_location(
            cls, "%s (Child)" % (cls.stock_location.name)
        )
        cls.stock_location_child.location_id = cls.stock_location

    def _create_product(self, name):
        product_form = Form(self.env["product.product"])
        product_form.name = name
        product_form.type = "product"
        return product_form.save()

    def _create_stock_location(self, name):
        stock_location_form = Form(self.env["stock.location"])
        stock_location_form.name = name
        stock_location_form.usage = self.env.ref("stock.stock_location_stock").usage
        return stock_location_form.save()

    def _create_stock_quant(self, location_id, product_id, qty):
        self.env["stock.quant"].create(
            {
                "company_id": self.company.id,
                "location_id": location_id.id,
                "product_id": product_id.id,
                "quantity": qty,
            }
        )

    def _create_stock_move(self, location_id, location_dest_id, product_id, qty):
        stock_move_form = Form(self.env["stock.move"])
        stock_move_form.name = product_id.display_name
        stock_move_form.location_id = location_id
        stock_move_form.location_dest_id = location_dest_id
        stock_move_form.product_id = product_id
        stock_move_form.product_uom_qty = qty
        stock_move = stock_move_form.save()
        stock_move._action_done()

    def _create_stock_move_line(self, location_id, location_dest_id, product_id, qty):
        self.env["stock.move.line"].create(
            {
                "company_id": self.company.id,
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
                "product_id": product_id.id,
                "product_uom_qty": qty,
                "product_uom_id": product_id.uom_id.id,
                "qty_done": qty,
                "state": "done",
            }
        )

    def _create_stock_picking(self, location_id, location_dest_id, product_id, qty):
        stock_picking_form = Form(self.env["stock.picking"])
        stock_picking_form.picking_type_id = self.env.ref("stock.picking_type_in")
        with stock_picking_form.move_ids_without_package.new() as line:
            line.product_id = product_id
            line.product_uom_qty = qty
        stock_picking = stock_picking_form.save()
        stock_picking.write(
            {"location_id": location_id.id, "location_dest_id": location_dest_id.id}
        )
        stock_picking.action_confirm()
        for line in stock_picking.move_ids_without_package:
            line.quantity_done = line.product_uom_qty
        stock_picking.button_validate()

    def test_archive_product_ok(self):
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        self.product_2.active = False
        self.assertFalse(self.product_2.active)

    def test_archive_unarchive_product(self):
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        self.product_1.active = True
        self.assertTrue(self.product_1.active)

    def test_archive_product_with_stock_move_in(self):
        self._create_stock_move(
            self.env.ref("stock.stock_location_suppliers"),
            self.stock_location,
            self.product_2,
            20.00,
        )
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_product_with_stock_move_line_in(self):
        self._create_stock_move_line(
            self.env.ref("stock.stock_location_suppliers"),
            self.stock_location,
            self.product_2,
            20.00,
        )
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_product_with_stock_picking_in(self):
        self._create_stock_picking(
            self.env.ref("stock.stock_location_suppliers"),
            self.stock_location,
            self.product_2,
            20.00,
        )
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_product_with_stock_picking_in_out(self):
        self._create_stock_picking(
            self.env.ref("stock.stock_location_suppliers"),
            self.stock_location,
            self.product_2,
            20.00,
        )
        self._create_stock_picking(
            self.stock_location,
            self.env.ref("stock.stock_location_customers"),
            self.product_2,
            20.00,
        )
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        self.product_2.active = False
        self.assertFalse(self.product_2.active)

    def test_archive_product_stock_location(self):
        self._create_stock_quant(self.stock_location, self.product_2, 20.00)
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_product_stock_location_child(self):
        self._create_stock_quant(self.stock_location_child, self.product_2, 20.00)
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_unarchive_stock_location(self):
        self.stock_location.active = False
        self.assertFalse(self.stock_location.active)
        self.stock_location.active = True
        self.assertTrue(self.stock_location.active)

    def test_archive_stock_location_ok(self):
        self.stock_location.active = False
        self.assertFalse(self.stock_location.active)

    def test_archive_stock_location(self):
        self._create_stock_quant(self.stock_location, self.product_2, 20.00)
        with self.assertRaises(ValidationError):
            self.stock_location.with_context(do_not_check_quant=True).active = False

    def test_archive_unarchive_stock_location_child(self):
        self.stock_location_child.active = False
        self.assertFalse(self.stock_location_child.active)
        self.stock_location_child.active = True
        self.assertTrue(self.stock_location_child.active)

    def test_archive_stock_location_child(self):
        self._create_stock_quant(self.stock_location_child, self.product_2, 20.00)
        with self.assertRaises(ValidationError):
            self.stock_location.with_context(do_not_check_quant=True).active = False
