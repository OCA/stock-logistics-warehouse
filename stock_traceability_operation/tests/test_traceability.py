# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.stock.tests.common import TestStockCommon


class TestTraceability(TestStockCommon):
    def setUp(self):
        super(TestTraceability, self).setUp()

        # Get the children of the main location
        self.children_locations = self.env['stock.location'].search(
            [('location_id', '=', self.stock_location),
             ('usage', '=', 'internal')])

        # Clean up the product from the inventory
        self.productA.type = 'product'
        inventory = self.InvObj.create({'name': 'Reset product for test',
                                        'filter': 'product',
                                        'product_id': self.productA.id})
        inventory.prepare_inventory()
        inventory.reset_real_qty()
        inventory.action_done()
        # Put the product in 2 locations
        self.lot = self.env['stock.production.lot'].create(
            {'name': 'Test lot', 'product_id': self.productA.id})
        inventory = self.InvObj.create({'name': 'Put product for test',
                                        'filter': 'none'})
        inventory.prepare_inventory()
        self.InvLineObj.create(
            {'inventory_id': inventory.id,
             'product_id': self.productA.id,
             'product_uom_id': self.productA.uom_id.id,
             'product_qty': 7.0,
             'location_id': self.children_locations[0].id,
             'prod_lot_id': self.lot.id})
        self.InvLineObj.create(
            {'inventory_id': inventory.id,
             'product_id': self.productA.id,
             'product_uom_id': self.productA.uom_id.id,
             'product_qty': 3.0,
             'location_id': self.children_locations[1].id,
             'prod_lot_id': self.lot.id})
        inventory.action_done()

        # Deactivate all the other variants
        other_variants = (self.productA.product_tmpl_id.product_variant_ids -
                          self.productA)
        other_variants.write({'active': False})

        self.assertEqual(
            self.env['stock.quant'].search(
                [('product_id', '=', self.productA.id)], count=True), 2,
            'There should be 2 quants for the product')

    def _get_actions_to_test(self):
        """Return a list of actions of which we want to test the results

        Actions to test are:
        - "moves" button from product form
        - "moves" button from product variant form
        - "traceability" button from lot form
        - "history" button from quant form
        """
        product = self.productA
        template = self.productA.product_tmpl_id
        lot = self.lot
        quants = self.env['stock.quant'].search(
            [('product_id', '=', self.productA.id)])
        return [record.action_traceability_operation()
                for record in [product, template, lot, quants]]

    def test_with_inventory_only(self):
        """Test that report is correct when only the inventory is done."""
        # Check all the actions yield correct results
        for action in self._get_actions_to_test():
            history = self.env[action['res_model']].search(action['domain'])
            self.assertEqual(len(history), 2,
                             "There should be 2 lines reported")
            self.assertEqual(
                history.mapped('location_dest_id'),
                self.children_locations[:2],
                "The history should show moves to children locations")
            for h in history:
                self.assertEqual(
                    h.location_id.usage, 'inventory',
                    "The history should show moves from inventory locations")

    def test_with_stock_moves(self):
        """Test that moves without operations are reflected."""
        move = self.MoveObj.create(
            {'name': 'Move without operations',
             'product_id': self.productA.id,
             'product_uom_qty': 5.0,
             'product_uom': self.productA.uom_id.id,
             'location_id': self.supplier_location,
             'location_dest_id': self.children_locations[0].id,
             'restrict_lot_id': self.lot.id})
        move.action_assign()
        move.action_done()

        self.assertEqual(len(move.quant_ids), 1,
                         "One quant should be created")
        # Check all the actions yield correct results
        for action in self._get_actions_to_test():
            history = self.env[action['res_model']].search(action['domain'])
            self.assertEqual(
                len(history), 3,
                "There should be 3 line reported")

            history_supplier = history.filtered(
                lambda h: h.location_id.usage != 'inventory')
            self.assertEqual(
                len(history_supplier), 1,
                "There should be 1 line reported to internal loc")
            self.assertEqual(
                history_supplier[0].location_id.id, self.supplier_location,
                "The source location is wrong")
            self.assertEqual(
                history_supplier[0].location_dest_id.id,
                self.children_locations[0].id,
                "The destination location is wrong")

    def test_with_pack_operations(self):
        """Test that operations are reflected.

        In this test we create a stock move going to the main location, and
        use operations to put it away in two children locations
        """
        # Create a delivery from the main stock location
        picking = self.PickingObj.create(
            {'picking_type_id': self.picking_type_out})
        move = self.MoveObj.create(
            {'name': 'Move with operations',
             'product_id': self.productA.id,
             'product_uom_qty': 10.0,
             'product_uom': self.productA.uom_id.id,
             'picking_id': picking.id,
             'location_id': self.stock_location,
             'location_dest_id': self.customer_location,
             'restrict_lot_id': self.lot.id})
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(
            len(move.reserved_quant_ids), 2,
            "The wrong quants were reserved: %s" % (
                ["%s: %f" %
                 (q.location_id.name, q.qty)
                 for q in move.reserved_quant_ids]))
        picking.do_prepare_partial()
        self.assertEqual(len(picking.pack_operation_ids), 2,
                         "Two operations should be generated")
        for p in picking.pack_operation_ids:
            p.qty_done = p.product_qty
        self.PickingObj.action_done_from_ui(picking.id)
        picking.refresh()
        self.assertEqual(
            len(move.quant_ids), 2,
            "The wrong quants were moved: %s" % (
                ["%d:%s/%f" %
                 (q.id, q.location_id.name, q.qty)
                 for q in move.quant_ids]))
        # In some versions of Odoo, in this situation the quants may be split
        # instead of being moved, so all we can assert is the total quantity
        # More on that at https://github.com/odoo/odoo/pull/10178
        self.assertEqual(sum([q.qty for q in move.quant_ids]), 10.0,
                         "The moved quants have the wrong quantity")

        # Check all the actions yield correct results
        for action in self._get_actions_to_test():
            history = self.env[action['res_model']].search(action['domain'])
            self.assertGreaterEqual(
                len(history), 3,
                "There should be 3 lines or more reported:"
                "1 for the inventory + 2 for the pack ops")
            self.assertEqual(
                sum(history.mapped('product_uom_qty')), 20.0,
                "The history should reflect the quantities of the operation:"
                "10.0 for the inventory + 10.0 for the pack ops")
            self.assertEqual(
                history.mapped('location_id').filtered(
                    lambda l: l.usage == 'internal'),
                self.children_locations[:2],
                "The locations should reflect the operation")
