from odoo.tests.common import TransactionCase


class TestStockLinkup(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env['stock.location'].create({
            'name': 'Test Location',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })
        cls.picking_type = cls.env.ref('stock.picking_type_out')

        cls.picking_1 = cls.env['stock.picking'].create({
            'name': 'Picking 1',
            'location_id': cls.location.id,
            'location_dest_id': cls.location.id,
            'picking_type_id': cls.picking_type.id,
            'partner_id': cls.partner.id,
        })
        cls.picking_2 = cls.env['stock.picking'].create({
            'location_id': cls.location.id,
            'location_dest_id': cls.location.id,
            'picking_type_id': cls.picking_type.id,
            'partner_id': cls.partner.id,
        })

        cls.template = cls.env['product.template'].create({'name': 'Template'})

        cls.product = cls.env['product.product'].create({
            'name': 'product',
            'type': 'product',
        })

    def test_get_action_link_single_picking(self):
        result = self.picking_1._get_action_link([self.picking_1.id])
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'stock.picking')
        self.assertEqual(result['view_id'], self.env.ref("stock.view_picking_form"))
        self.assertEqual(result['views'], [[False, "form"]])
        self.assertEqual(result['res_id'], self.picking_1.id)

    def test_get_action_link_multiple_pickings(self):
        result = self.picking_1._get_action_link([self.picking_1.id, self.picking_2.id])
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'stock.picking')
        self.assertEqual(result['name'], 'Transfers')
        self.assertEqual(result['view_id'], self.env.ref("stock.vpicktree"))
        self.assertEqual(result['views'], [[False, "tree"], [False, "form"]])
        self.assertEqual(result['domain'], [('id', 'in', [self.picking_1.id, self.picking_2.id])])

    def test_action_stock_picking_origin(self):
        move_1 = self.env['stock.move'].create({
            'name': 'Move 1',
            'product_id': self.product.id,
            'product_uom_qty': 10,
            'location_id': self.location.id,
            'location_dest_id': self.location.id,
            'picking_id': self.picking_1.id,
        })
        move_2 = self.env['stock.move'].create({
            'name': 'Move 2',
            'product_id': self.product.id,
            'product_uom_qty': 10,
            'location_id': self.location.id,
            'location_dest_id': self.location.id,
            'picking_id': self.picking_2.id,
            'move_orig_ids': [(4, move_1.id)],
        })

        result = self.picking_2.action_stock_picking_origin()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'stock.picking')
        self.assertEqual(result['view_id'], self.env.ref("stock.vpicktree").id)
        self.assertEqual(result['views'], [[False, "tree"], [False, "form"]])
        self.assertEqual(result['domain'], [('id', 'in', [self.picking_1.id])])

    def test_action_stock_picking_destination(self):
        move_1 = self.env['stock.move'].create({
            'name': 'Move 1',
            'product_id': self.product.id,
            'product_uom_qty': 10,
            'location_id': self.location.id,
            'location_dest_id': self.location.id,
            'picking_id': self.picking_1.id,
        })
        move_2 = self.env['stock.move'].create({
            'name': 'Move 2',
            'product_id': self.product.id,
            'product_uom_qty': 10,
            'location_id': self.location.id,
            'location_dest_id': self.location.id,
            'picking_id': self.picking_2.id,
            'move_dest_ids': [(4, move_1.id)],
        })

        result = self.picking_1.action_stock_picking_destination()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'stock.picking')
        self.assertEqual(result['view_id'], self.env.ref("stock.vpicktree").id)
        self.assertEqual(result['views'], [[False, "tree"], [False, "form"]])
        self.assertEqual(result['domain'], [('id', 'in', [self.picking_2.id])])
