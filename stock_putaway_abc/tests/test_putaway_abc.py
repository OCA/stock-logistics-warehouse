# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


class TestStockMovePutawayABC(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_flipover = cls.env.ref('product.product_product_20')
        cls.product_sofa = cls.env.ref('product.consu_delivery_01')
        cls.product_category_office = cls.env.ref('product.product_category_5')

        cls.warehouse = cls.env.ref('stock.warehouse0')

        cls.vendors_location = cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')

        cls.stock_putaway = cls.env.ref(
            'stock_putaway_abc.product_putaway_wh_stock'
        )
        cls.stock_location.write({'putaway_strategy_id': cls.stock_putaway.id})

        cls.bin_a_location = cls.env.ref('stock_putaway_abc.location_bin_a')
        cls.bin_b_location = cls.env.ref('stock_putaway_abc.location_bin_b')
        cls.bin_c_location = cls.env.ref('stock_putaway_abc.location_bin_c')

        cls.picking_type_receipts = cls.env.ref('stock.picking_type_in')

        cls.reception_route = cls.env['stock.location.route'].search([
            ('warehouse_ids', '=', cls.warehouse.id),
            ('name', 'ilike', 'Receive'),
        ])

        # Add reception route to product category
        cls.product_category_office.write({
            'route_ids': [(4, cls.reception_route.id)]
        })

        # Create route to pull from suppliers location
        cls.suppliers_to_stock_rule = cls.env['stock.rule'].create({
            'route_id': cls.reception_route.id,
            'name': 'WH: Suppliers → Stock',
            'action': 'pull',
            'picking_type_id': cls.picking_type_receipts.id,
            'location_src_id': cls.vendors_location.id,
            'location_id': cls.stock_location.id,
            'procure_method': 'make_to_stock',
        })

    def test_reception_into_product_abc_bin(self):
        # Flipover product has an ABC putaway strategy to A
        replenish_wiz = self.env['product.replenish'].create({
            'product_id': self.product_flipover.id,
            'product_tmpl_id': self.product_flipover.product_tmpl_id.id,
            'product_uom_id': self.product_flipover.uom_id.id,
            'quantity': 10.0,
        })
        replenish_wiz.launch_replenishment()
        generated_move = self.env['stock.move'].search(
            [
                ('product_id', '=', self.product_flipover.id),
                ('location_id', '=', self.vendors_location.id),
                ('location_dest_id', '=', self.stock_location.id),
            ]
        )
        self.assertEqual(generated_move.state, 'confirmed')
        generated_move.picking_id.action_assign()
        self.assertEqual(generated_move.state, 'assigned')
        self.assertEqual(
            generated_move.move_line_ids.location_dest_id,
            self.bin_a_location
        )

    def test_reception_into_product_next_abc_bin(self):
        # Flipover product has an ABC putaway strategy to A
        # Bin A is set as inactive so it must go into Bin B
        self.bin_a_location.active = False
        replenish_wiz = self.env['product.replenish'].create({
            'product_id': self.product_flipover.id,
            'product_tmpl_id': self.product_flipover.product_tmpl_id.id,
            'product_uom_id': self.product_flipover.uom_id.id,
            'quantity': 10.0,
        })
        replenish_wiz.launch_replenishment()
        generated_move = self.env['stock.move'].search(
            [
                ('product_id', '=', self.product_flipover.id),
                ('location_id', '=', self.vendors_location.id),
                ('location_dest_id', '=', self.stock_location.id),
            ]
        )
        self.assertEqual(generated_move.state, 'confirmed')
        generated_move.picking_id.action_assign()
        self.assertEqual(generated_move.state, 'assigned')
        self.assertEqual(
            generated_move.move_line_ids.location_dest_id,
            self.bin_b_location
        )

    def test_reception_into_product_category_abc_bin(self):
        # Sofa product is office category
        # office category has an ABC putaway strategy to B
        replenish_wiz = self.env['product.replenish'].create({
            'product_id': self.product_sofa.id,
            'product_tmpl_id': self.product_sofa.product_tmpl_id.id,
            'product_uom_id': self.product_sofa.uom_id.id,
            'quantity': 10.0,
        })
        replenish_wiz.launch_replenishment()
        generated_move = self.env['stock.move'].search(
            [
                ('product_id', '=', self.product_sofa.id),
                ('location_id', '=', self.vendors_location.id),
                ('location_dest_id', '=', self.stock_location.id),
            ]
        )
        self.assertEqual(generated_move.state, 'confirmed')
        generated_move.picking_id.action_assign()
        self.assertEqual(generated_move.state, 'assigned')
        self.assertEqual(
            generated_move.move_line_ids.location_dest_id,
            self.bin_b_location
        )

    def test_reception_into_product_category_next_abc_bin(self):
        # Sofa product is office category
        # office category has an ABC putaway strategy to B
        # Bin B is set as inactive so it must go into Bin C
        # Bin C is set as inactive so it must go into Bin A
        self.bin_b_location.active = False
        self.bin_c_location.active = False
        replenish_wiz = self.env['product.replenish'].create({
            'product_id': self.product_sofa.id,
            'product_tmpl_id': self.product_sofa.product_tmpl_id.id,
            'product_uom_id': self.product_sofa.uom_id.id,
            'quantity': 10.0,
        })
        replenish_wiz.launch_replenishment()
        generated_move = self.env['stock.move'].search(
            [
                ('product_id', '=', self.product_sofa.id),
                ('location_id', '=', self.vendors_location.id),
                ('location_dest_id', '=', self.stock_location.id),
            ]
        )
        self.assertEqual(generated_move.state, 'confirmed')
        generated_move.picking_id.action_assign()
        self.assertEqual(generated_move.state, 'assigned')
        self.assertEqual(
            generated_move.move_line_ids.location_dest_id,
            self.bin_a_location
        )
