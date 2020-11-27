# Copyright 2020 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase, Form
from odoo.exceptions import ValidationError


class TestLocationArchiveConstraint(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls._create_product(cls, 'Product 1')
        cls.product_2 = cls._create_product(cls, 'Product 2')
        stock_location_stock = cls.env.ref('stock.stock_location_stock')
        cls.stock_location = cls._create_stock_location(
            cls, "%s (Copy)" % (stock_location_stock.name)
        )
        cls.stock_location_child = cls._create_stock_location(
            cls, "%s (Child)" % (cls.stock_location.name)
        )
        cls.stock_location_child.location_id = cls.stock_location

    def _create_product(self, name):
        product_form = Form(self.env['product.product'])
        product_form.name = name
        product_form.type = 'product'
        return product_form.save()

    def _create_stock_location(self, name):
        stock_location_form = Form(self.env['stock.location'])
        stock_location_form.name = name
        stock_location_form.usage = self.env.ref('stock.stock_location_stock').usage
        return stock_location_form.save()

    def _create_stock_inventory(self, location_id, product_id, qty):
        stock_inventory_form = Form(self.env['stock.inventory'])
        stock_inventory_form.name = 'INV: %s' % product_id.display_name
        stock_inventory_form.filter = 'product'
        stock_inventory_form.product_id = product_id
        stock_inventory_form.location_id = location_id
        stock_inventory = stock_inventory_form.save()
        stock_inventory.action_start()
        for line_id in stock_inventory.line_ids:
            line_id.product_qty = qty
        stock_inventory.action_validate()

    def _create_stock_move(self, location_id, location_dest_id, product_id, qty):
        stock_move_form = Form(self.env['stock.move'])
        stock_move_form.name = product_id.display_name
        stock_move_form.location_id = location_id
        stock_move_form.location_dest_id = location_dest_id
        stock_move_form.product_id = product_id
        stock_move_form.product_uom_qty = qty
        stock_move = stock_move_form.save()
        stock_move._action_done()

    def _create_stock_move_line(self, location_id, location_dest_id, product_id, qty):
        stock_move_line_form = Form(self.env['stock.move.line'])
        stock_move_line_form.location_id = location_id
        stock_move_line_form.location_dest_id = location_dest_id
        stock_move_line_form.product_id = product_id
        stock_move_line_form.product_uom_qty = qty
        stock_move_line_form.qty_done = qty
        stock_move_line_form.state = 'done'
        stock_move_line_form.save()

    def _create_stock_picking(self, location_id, location_dest_id, product_id, qty):
        stock_picking_form = Form(self.env['stock.picking'])
        stock_picking_form.picking_type_id = self.env.ref('stock.picking_type_in')
        with stock_picking_form.move_ids_without_package.new() as line:
            line.product_id = product_id
            line.product_uom_qty = qty
        stock_picking = stock_picking_form.save()
        stock_picking.write({
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
        })
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
            self.env.ref('stock.stock_location_suppliers'),
            self.stock_location, self.product_2, 20.00
        )
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_product_with_stock_move_line_in(self):
        self._create_stock_move_line(
            self.env.ref('stock.stock_location_suppliers'),
            self.stock_location, self.product_2, 20.00
        )
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_product_with_stock_picking_in(self):
        self._create_stock_picking(
            self.env.ref('stock.stock_location_suppliers'),
            self.stock_location, self.product_2, 20.00
        )
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_product_with_stock_picking_in_out(self):
        self._create_stock_picking(
            self.env.ref('stock.stock_location_suppliers'),
            self.stock_location, self.product_2, 20.00
        )
        self._create_stock_picking(
            self.stock_location,
            self.env.ref('stock.stock_location_customers'), self.product_2, 20.00
        )
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        self.product_2.active = False
        self.assertFalse(self.product_2.active)

    def test_archive_product_stock_location(self):
        self._create_stock_inventory(self.stock_location, self.product_2, 20.00)
        self.product_1.active = False
        self.assertFalse(self.product_1.active)
        with self.assertRaises(ValidationError):
            self.product_2.active = False

    def test_archive_product_stock_location_child(self):
        self._create_stock_inventory(self.stock_location_child, self.product_2, 20.00)
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
        self._create_stock_inventory(self.stock_location, self.product_2, 20.00)
        with self.assertRaises(ValidationError):
            self.stock_location.active = False

    def test_archive_unarchive_stock_location_child(self):
        self.stock_location_child.active = False
        self.assertFalse(self.stock_location_child.active)
        self.stock_location_child.active = True
        self.assertTrue(self.stock_location_child.active)

    def test_archive_stock_location_child(self):
        self._create_stock_inventory(self.stock_location_child, self.product_2, 20.00)
        with self.assertRaises(ValidationError):
            self.stock_location.active = False
