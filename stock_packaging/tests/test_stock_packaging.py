# Copyright 2015-2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common


class TestStockMove(common.TransactionCase):

    def setUp(self):
        """ Create a packaging with uom  product_uom_dozen on
                * product_product_3 (uom is product_uom_unit)
        """
        super(TestStockMove, self).setUp()
        self.location_customers = self.env.ref(
            'stock.stock_location_customers')
        self.location_out = self.env.ref('stock.stock_location_output')
        self.product = self.env.ref('product.product_product_3')
        self.product_packaging_dozen = self.env['product.packaging'].create({
            'product_id': self.product.id,
            'uom_id': self.env.ref('uom.product_uom_dozen').id,
            'name': 'dozen',
        })
        self.product_packaging_dozen.product_id.lst_price = 45

        vals = {
            'name': 'ROUTE 1',
            'sequence': 1,
            'product_selectable': True,
        }
        self.route = self.env['stock.location.route'].create(vals)

        vals = {
            'name': 'OUT => Customer',
            'action': 'pull',
            'location_id': self.location_customers.id,
            'location_src_id': self.location_out.id,
            'procure_method': 'make_to_order',
            'route_id': self.route.id,
            'picking_type_id': self.ref('stock.picking_type_out'),
            'propagate_product_packaging': True,
        }

        self.rule = self.env['stock.rule'].create(vals)

        vals = {
            'name': 'Stock => OUT',
            'action': 'pull',
            'location_id': self.location_out.id,
            'location_src_id': self.ref('stock.stock_location_stock'),
            'procure_method': 'make_to_stock',
            'route_id': self.route.id,
            'picking_type_id': self.ref('stock.picking_type_internal'),
        }

        self.rule_pick = self.env['stock.rule'].create(vals)

        self.env.ref('product.product_product_3').route_ids |= self.route

        vals = {
            'name': 'PROC 1',
        }
        self.group = self.env['procurement.group'].create(vals)

    def test_stock_move(self):
        """
            Set product_packaging product_packaging_dozen
            Run a procurement group with product product_3
            Check Procurement contains product packaging
            Run Procurement
            Check Stock Moves contain product packaging
        """
        self.env['procurement.group'].run(
            self.product,
            1.0,
            self.product_packaging_dozen.uom_id,
            self.env.ref('stock.stock_location_customers'),
            'TEST',
            'TEST',
            {
                'product_packaging': self.product_packaging_dozen.id,
                'group_id': self.group,
            },
        )
        move = self.env['stock.move'].search([
            ('group_id', '=', self.group.id),
            ('location_dest_id', '=', self.location_out.id)
        ])

        self.assertEqual(
            1,
            len(move),
            "There is no move")
        self.assertEqual(
            self.product_packaging_dozen,
            move.product_packaging,
            "The Customer procurement does not contain the product packaging")
        # Run Procurement
        move._action_done()
        # Check Move OUT => Customer
        move = self.env['stock.move'].search([
            ('group_id', '=', self.group.id),
            ('location_dest_id', '=', self.location_customers.id)
        ])
        self.assertEqual(
            1,
            len(move),
            "There is no Move OUT")
        move = move.picking_id.move_lines.filtered(
            lambda m: m.product_id ==
            self.env.ref('product.product_product_3'))
        self.assertEqual(
            self.product_packaging_dozen,
            move.product_packaging,
            "Stock Move OUT does not contains product packaging")
        # Check Move STOCK => OUT
        picking_stock = self.env['stock.move'].search([
            ('group_id', '=', self.group.id),
            ('location_dest_id', '=', self.location_out.id)
        ]).picking_id
        self.assertEqual(
            1,
            len(picking_stock),
            "There is no Picking Stock")
        move = picking_stock.move_lines.filtered(
            lambda m: m.product_id ==
            self.env.ref('product.product_product_3'))
        self.assertEqual(
            self.product_packaging_dozen,
            move.product_packaging,
            "Stock Move STOCK does not contains product packaging")

    def test_stock_move_no_propagate(self):
        """ Change Procurement Rule to no propagate product packaging
            Create a sale order line with product product_3
            Set product_packaging product_packaging_dozen
            Confirm sale order
            Check Procurement contains product packaging
            Run Procurement
            Check Stock Moves contain product packaging
        """
        self.rule.propagate_product_packaging = False
        self.env['procurement.group'].run(
            self.product,
            1.0,
            self.product_packaging_dozen.uom_id,
            self.env.ref('stock.stock_location_customers'),
            'TEST',
            'TEST',
            {
                'product_packaging': self.product_packaging_dozen.id,
                'group_id': self.group,
            },
        )
        move = self.env['stock.move'].search([
            ('group_id', '=', self.group.id),
            ('location_dest_id', '=', self.location_out.id)
        ])

        self.assertEqual(
            1,
            len(move),
            "There is no move")
        self.assertFalse(
            move.product_packaging,
            "The Customer procurement does not contain the product packaging")
        # Run Procurement
        move._action_done()
        # Check Move OUT => Customer
        move = self.env['stock.move'].search([
            ('group_id', '=', self.group.id),
            ('location_dest_id', '=', self.location_customers.id)
        ])
        self.assertEqual(
            1,
            len(move),
            "There is no Move OUT")
        move = move.picking_id.move_lines.filtered(
            lambda m: m.product_id ==
            self.env.ref('product.product_product_3'))
        self.assertEqual(
            self.product_packaging_dozen,
            move.product_packaging,
            "Stock Move OUT does not contains product packaging")
        # Check Move STOCK => OUT
        picking_stock = self.env['stock.move'].search([
            ('group_id', '=', self.group.id),
            ('location_dest_id', '=', self.location_out.id)
        ]).picking_id
        self.assertEqual(
            1,
            len(picking_stock),
            "There is no Picking Stock")
        move = picking_stock.move_lines.filtered(
            lambda m: m.product_id ==
            self.env.ref('product.product_product_3'))
        self.assertFalse(
            move.product_packaging,
            "Stock Move STOCK does not contains product packaging")
