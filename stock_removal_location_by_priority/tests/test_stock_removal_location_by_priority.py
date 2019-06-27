# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date
from odoo.tests.common import TransactionCase


class TestStockRemovalLocationByPriority(TransactionCase):

    def setUp(self):
        super(TestStockRemovalLocationByPriority, self).setUp()
        self.res_users_model = self.env['res.users']
        self.stock_location_model = self.env['stock.location']
        self.stock_warehouse_model = self.env['stock.warehouse']
        self.stock_picking_model = self.env['stock.picking']
        self.stock_change_model = self.env['stock.change.product.qty']
        self.product_model = self.env['product.product']
        self.quant_model = self.env['stock.quant']

        self.picking_internal = self.env.ref('stock.picking_type_internal')
        self.picking_out = self.env.ref('stock.picking_type_out')
        self.location_supplier = self.env.ref('stock.stock_location_suppliers')

        self.company = self.env.ref('base.main_company')
        grp_rem_priority = self.env.ref(
            'stock_removal_location_by_priority.group_removal_priority')

        # We assign the group to admin, as the _get_removal_strategy_order
        # method is going to be always executed as sudo.
        user_admin = self.env.ref('base.user_root')
        user_admin.groups_id = [(4, grp_rem_priority.id, 0)]

        self.wh1 = self.stock_warehouse_model.create({
            'name': 'WH1',
            'code': 'WH1',
        })

        # Removal strategies:
        self.fifo = self.env.ref('stock.removal_fifo')
        self.lifo = self.env.ref('stock.removal_lifo')

        # Create locations:
        self.stock = self.stock_location_model.create({
            'name': 'Stock Base',
            'usage': 'internal',
        })
        self.shelf_A = self.stock_location_model.create({
            'name': 'Shelf_A',
            'usage': 'internal',
            'location_id': self.stock.id,
            'removal_priority': 10,
        })
        self.shelf_B = self.stock_location_model.create({
            'name': 'Shelf_B',
            'usage': 'internal',
            'location_id': self.stock.id,
            'removal_priority': 5,
        })
        self.stock_2 = self.stock_location_model.create({
            'name': 'Another Stock Location',
            'usage': 'internal',
        })

        # Create a product:
        self.product_1 = self.product_model.create({
            'name': 'Test Product 1',
            'type': 'product',
        })

        # Create quants:
        today = date.today()
        q1 = self.quant_model.create({
            'product_id': self.product_1.id,
            'location_id': self.shelf_A.id,
            'quantity': 5.0,
            'in_date': today,
        })
        q2 = self.quant_model.create({
            'product_id': self.product_1.id,
            'location_id': self.shelf_B.id,
            'quantity': 5.0,
            'in_date': today,
        })
        self.quants = q1 + q2

    def _create_picking(self, picking_type, location, location_dest, qty):
        picking = self.stock_picking_model.create({
            'picking_type_id': picking_type.id,
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': self.product_1.id,
                    'product_uom': self.product_1.uom_id.id,
                    'product_uom_qty': qty,
                    'location_id': location.id,
                    'location_dest_id': location_dest.id,
                    'price_unit': 2,
                })]
        })
        return picking

    def test_01_stock_removal_location_by_priority_fifo(self):
        """Tests removal priority with FIFO strategy."""
        self.stock.removal_strategy_id = self.fifo
        # quants must start unreserved
        for q in self.quants:
            self.assertEqual(q.reserved_quantity, 0.0)
            if q.location_id == self.shelf_A:
                self.assertEqual(q.removal_priority, 10)
            if q.location_id == self.shelf_B:
                self.assertEqual(q.removal_priority, 5)
        self.assertEqual(self.quants[0].in_date, self.quants[1].in_date)
        picking_1 = self._create_picking(
            self.picking_internal, self.stock, self.stock_2, 5)
        picking_1.action_confirm()
        picking_1.action_assign()

        # quants must be reserved in Shelf B (lower removal_priority value).
        for q in self.quants:
            if q.location_id == self.shelf_A:
                self.assertEqual(q.reserved_quantity, 0.0)
            if q.location_id == self.shelf_B:
                self.assertEqual(q.reserved_quantity, 5.0)

    def test_02_stock_removal_location_by_priority_lifo(self):
        """Tests removal priority with LIFO strategy."""
        self.stock.removal_strategy_id = self.lifo
        # quants must start unreserved
        for q in self.quants:
            self.assertEqual(q.reserved_quantity, 0.0)
            if q.location_id == self.shelf_A:
                self.assertEqual(q.removal_priority, 10)
            if q.location_id == self.shelf_B:
                self.assertEqual(q.removal_priority, 5)
        self.assertEqual(self.quants[0].in_date, self.quants[1].in_date)
        picking_1 = self._create_picking(
            self.picking_internal, self.stock, self.stock_2, 5)
        picking_1.action_confirm()
        picking_1.action_assign()

        # quants must be reserved in Shelf B (lower removal_priority value).
        for q in self.quants:
            if q.location_id == self.shelf_A:
                self.assertEqual(q.reserved_quantity, 0.0)
            if q.location_id == self.shelf_B:
                self.assertEqual(q.reserved_quantity, 5.0)
