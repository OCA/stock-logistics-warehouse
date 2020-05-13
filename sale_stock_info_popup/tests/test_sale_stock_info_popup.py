# Copyright 2020 Tecnativa - Ernesto Tejeda
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo.tests.common import SavepointCase


class SaleStockInfoPopup(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(SaleStockInfoPopup, cls).setUpClass()
        user_group_stock_user = cls.env.ref('stock.group_stock_user')
        cls.user_stock_user = cls.env['res.users'].create({
            'name': 'Pauline Poivraisselle',
            'login': 'pauline',
            'email': 'p.p@example.com',
            'notification_type': 'inbox',
            'groups_id': [(6, 0, [user_group_stock_user.id])]})
        cls.product = cls.env['product.product'].create({
            'name': 'Storable product',
            'type': 'product',
        })
        cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'quantity': 30.0})
        cls.env['stock.quant'].create({
            'product_id': cls.product.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'quantity': 10.0,
            'owner_id': cls.user_stock_user.partner_id.id})

        cls.picking_out = cls.env['stock.picking'].create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'location_dest_id': cls.env.ref('stock.stock_location_customers').id})
        cls.env['stock.move'].create({
            'name': 'a move',
            'product_id': cls.product.id,
            'product_uom_qty': 3.0,
            'product_uom': cls.product.uom_id.id,
            'picking_id': cls.picking_out.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'location_dest_id': cls.env.ref('stock.stock_location_customers').id})

        cls.picking_out_2 = cls.env['stock.picking'].create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'location_dest_id': cls.env.ref('stock.stock_location_customers').id})
        cls.env['stock.move'].create({
            'restrict_partner_id': cls.user_stock_user.partner_id.id,
            'name': 'another move',
            'product_id': cls.product.id,
            'product_uom_qty': 5.0,
            'product_uom': cls.product.uom_id.id,
            'picking_id': cls.picking_out_2.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'location_dest_id': cls.env.ref('stock.stock_location_customers').id})

    def test_free_quantity(self):
        """ Test the value of product.free_qty. Free_qty = qty_on_hand - qty_reserved"""
        self.assertAlmostEqual(40.0, self.product.free_qty)
        self.picking_out.action_confirm()
        self.picking_out_2.action_confirm()
        # No reservation so free_qty is unchanged
        self.assertAlmostEqual(40.0, self.product.free_qty)
        self.picking_out.action_assign()
        self.picking_out_2.action_assign()
        # 8 units are now reserved
        self.assertAlmostEqual(32.0, self.product.free_qty)
        self.picking_out.do_unreserve()
        self.picking_out_2.do_unreserve()
        # 8 units are available again
        self.assertAlmostEqual(40.0, self.product.free_qty)

    def test_qty_available_info_popup(self):
        """ create a sale order and check the available quantities
        on sale order lines needed for QtyAtDateWidget.
        """
        self.picking_out.action_confirm()
        self.picking_out_2.action_assign()
        so = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': self.product.list_price
                }),
            ],
        })
        line = so.order_line[0]
        self.assertAlmostEqual(line.scheduled_date, datetime.now(),
                               delta=timedelta(seconds=10))
        self.assertAlmostEqual(line.virtual_available_at_date, 32)
        self.assertAlmostEqual(line.free_qty_today, 35)
        self.assertAlmostEqual(line.qty_available_today, 40)
        self.assertAlmostEqual(line.qty_to_deliver, 1)

    def test_10_qty_available(self):
        """Create a sale order containing three times the same product. The
        quantity available should be different for the 3 lines.
        """
        so = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 5,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': self.product.list_price
                }),
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 5,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': self.product.list_price
                }),
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 5,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': self.product.list_price
                }),
            ],
        })
        for qty in so.order_line.mapped('free_qty_today'):
            self.assertIn(qty, [40, 35, 30])
