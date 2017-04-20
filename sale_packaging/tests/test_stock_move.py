# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common


class TestStockMove(common.TransactionCase):

    def setUp(self):
        """ Create a packagings with uom  product_uom_dozen on
                * product_product_3 (uom is product_uom_unit)
        """
        super(TestStockMove, self).setUp()
        self.product_packaging_dozen = self.env['product.packaging'].create(
            {'product_tmpl_id': self.env.ref('product.product_product_3'
                                             ).product_tmpl_id.id,
             'uom_id': self.env.ref('product.product_uom_dozen').id,
             'name': 'dozen'})
        self.product_packaging_dozen.product_tmpl_id.lst_price = 45

        vals = {'name': 'ROUTE 1',
                'sequence': 1,
                'product_selectable': True,
                }
        self.route = self.env['stock.location.route'].create(vals)

        vals = {'name': 'OUT => Customer',
                'action': 'move',
                'location_id': self.ref('stock.stock_location_customers'),
                'location_src_id': self.ref('stock.stock_location_output'),
                'procure_method': 'make_to_order',
                'route_id': self.route.id,
                'picking_type_id': self.ref('stock.picking_type_out'),
                'propagate_product_packaging': True}

        self.rule = self.env['procurement.rule'].create(vals)

        vals = {'name': 'Stock => OUT',
                'action': 'move',
                'location_id': self.ref('stock.stock_location_output'),
                'location_src_id': self.ref('stock.stock_location_stock'),
                'procure_method': 'make_to_stock',
                'route_id': self.route.id,
                'picking_type_id': self.ref('stock.picking_type_internal')}

        self.rule_pick = self.env['procurement.rule'].create(vals)

        self.env.ref('product.product_product_3').route_ids |= self.route

    def test_stock_move(self):
        """ Create a sale order line with product product_3
            Set product_packaging product_packaging_dozen
            Confirm sale order
            Check Procurement contains product packaging
            Run Procurement
            Check Stock Moves contain product packaging
        """
        so_line = self.env['sale.order.line'].create(
            {'order_id': self.env['sale.order'].create(
                {'partner_id': self.env.ref('base.res_partner_2').id}).id,
             'product_id': self.ref('product.product_product_3'),
             'product_uom_qty': 1.0})
        so_line.product_id_change()
        so_line.product_packaging = self.product_packaging_dozen
        so_line._onchange_product_packaging()
        # Confirm Sale Order
        so_line.order_id.action_confirm()
        procurement = self.env['procurement.order'].search(
            [('sale_line_id', '=', so_line.id)])
        self.assertEqual(
            1,
            len(procurement),
            "There is no procurement")
        self.assertEqual(
            self.product_packaging_dozen,
            procurement.product_packaging,
            "The Customer procurement does not contain the product packaging")
        # Run Procurement
        procurement.run()
        # Check Move OUT => Customer
        picking_out = so_line.order_id.picking_ids.filtered(
            lambda p: p.location_dest_id ==
            self.env.ref('stock.stock_location_customers'))
        self.assertEqual(
            1,
            len(picking_out),
            "There is no Picking OUT")
        move = picking_out.move_lines.filtered(
            lambda m: m.product_id ==
            self.env.ref('product.product_product_3'))
        self.assertEqual(
            self.product_packaging_dozen,
            move.product_packaging,
            "Stock Move OUT does not contains product packaging")
        # Check Move STOCK => OUT
        picking_stock = so_line.order_id.picking_ids.filtered(
            lambda p: p.location_dest_id ==
            self.env.ref('stock.stock_location_output'))
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
        so_line = self.env['sale.order.line'].create(
            {'order_id': self.env['sale.order'].create(
                {'partner_id': self.env.ref('base.res_partner_2').id}).id,
             'product_id': self.ref('product.product_product_3'),
             'product_uom_qty': 1.0})
        so_line.product_id_change()
        so_line.product_packaging = self.product_packaging_dozen
        so_line._onchange_product_packaging()
        # Confirm Sale Order
        so_line.order_id.action_confirm()
        procurement = self.env['procurement.order'].search(
            [('sale_line_id', '=', so_line.id)])
        self.assertEqual(
            1,
            len(procurement),
            "There is no procurement")
        self.assertEqual(
            self.product_packaging_dozen,
            procurement.product_packaging,
            "The Customer procurement does not contain the product packaging")
        # Run Procurement
        procurement.run()
        # Check Move OUT => Customer
        picking_out = so_line.order_id.picking_ids.filtered(
            lambda p: p.location_dest_id ==
            self.env.ref('stock.stock_location_customers'))
        self.assertEqual(
            1,
            len(picking_out),
            "There is no Picking OUT")
        move = picking_out.move_lines.filtered(
            lambda m: m.product_id ==
            self.env.ref('product.product_product_3'))
        self.assertEqual(
            self.product_packaging_dozen,
            move.product_packaging,
            "Stock Move OUT does not contains product packaging")
        # Check Move STOCK => OUT
        picking_stock = so_line.order_id.picking_ids.filtered(
            lambda p: p.location_dest_id ==
            self.env.ref('stock.stock_location_output'))
        self.assertEqual(
            1,
            len(picking_stock),
            "There is no Picking Stock")
        move = picking_stock.move_lines.filtered(
            lambda m: m.product_id ==
            self.env.ref('product.product_product_3'))
        self.assertEqual(
            self.env['product.packaging'],
            move.product_packaging,
            "Stock Move STOCK does contain product packaging")
