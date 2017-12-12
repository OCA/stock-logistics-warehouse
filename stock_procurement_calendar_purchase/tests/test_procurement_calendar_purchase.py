# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import patch
from odoo import fields
from odoo.tests import common


class TestProcurementCalendar(common.TransactionCase):

    def setUp(self):
        res = super(TestProcurementCalendar, self).setUp()
        supplierinfo_obj = self.env['product.supplierinfo']

        # Ipod
        self.product_11 = self.env.ref('product.product_product_11')
        # Mouse Wireless
        self.product_12 = self.env.ref('product.product_product_12')
        # RAM SR5
        self.product_13 = self.env.ref('product.product_product_13')
        # Apple Wireless Keyboard
        self.product_9 = self.env.ref('product.product_product_9')

        self.supplier_1 = self.env.ref('base.res_partner_1')
        self.supplier_2 = self.env.ref('base.res_partner_2')

        self.product_11.seller_ids = self.env['product.supplierinfo']
        self.product_12.seller_ids = self.env['product.supplierinfo']
        self.product_13.seller_ids = self.env['product.supplierinfo']
        self.product_9.seller_ids = self.env['product.supplierinfo']

        vals = {
            'name': self.supplier_1.id,
            'price': 2,
            'product_tmpl_id': self.product_11.product_tmpl_id.id,
            'delay': 2,
        }
        self.supplierinfo_11 = supplierinfo_obj.create(vals)

        vals = {
            'name': self.supplier_2.id,
            'price': 2,
            'min_qty': 22.0,
            'product_tmpl_id': self.product_11.product_tmpl_id.id,
            'delay': 2,
        }
        self.supplierinfo_11_2 = supplierinfo_obj.create(vals)

        vals = {
            'name': self.supplier_1.id,
            'price': 10,
            'product_tmpl_id': self.product_12.product_tmpl_id.id,
            'delay': 2,
        }
        self.supplierinfo_12 = supplierinfo_obj.create(vals)

        vals = {
            'name': self.supplier_1.id,
            'price': 14,
            'product_tmpl_id': self.product_13.product_tmpl_id.id,
            'delay': 2,
        }
        self.supplierinfo_13 = supplierinfo_obj.create(vals)

        vals = {
            'product_max_qty': 12.0,
            'product_min_qty': 5.0,
            'product_uom': self.ref('product.product_uom_unit'),
            'product_id': self.product_11.id,
            'location_id': self.ref('stock.stock_location_stock')
        }
        self.orderpoint_11 = self.env['stock.warehouse.orderpoint'].create(
            vals)

        vals = {
            'product_max_qty': 10.0,
            'product_min_qty': 3.0,
            'product_uom': self.ref('product.product_uom_unit'),
            'product_id': self.product_12.id,
            'location_id': self.ref('stock.stock_location_stock')
        }
        self.orderpoint_12 = self.env['stock.warehouse.orderpoint'].create(
            vals)
        vals = {
            'product_max_qty': 16.0,
            'product_min_qty': 3.0,
            'product_uom': self.ref('product.product_uom_unit'),
            'product_id': self.product_13.id,
            'location_id': self.ref('stock.stock_location_stock')
        }
        self.orderpoint_13 = self.env['stock.warehouse.orderpoint'].create(
            vals)
        vals = {
            'product_max_qty': 20.0,
            'product_min_qty': 3.0,
            'product_uom': self.ref('product.product_uom_unit'),
            'product_id': self.product_9.id,
            'location_id': self.ref('stock.stock_location_stock')
        }
        self.orderpoint_9 = self.env['stock.warehouse.orderpoint'].create(
            vals)

        self.product_11.route_ids += self.env.ref(
            'purchase.route_warehouse0_buy')
        self.product_12.route_ids += self.env.ref(
            'purchase.route_warehouse0_buy')
        self.product_13.route_ids += self.env.ref(
            'purchase.route_warehouse0_buy')
        return res

    def _reset_inventory(self, product):
        quants = self.env['stock.quant'].search(
            [('product_id', '=', product.id)])
        for quant in quants:
            inventory = self.env['stock.inventory'].create({
                'name': 'Reset inventory',
                'filter': 'partial',
                'line_ids': [(0, 0, {
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'product_qty': 0.0,
                    'location_id': quant.location_id.id
                })]
            })
            inventory.action_done()

    @patch.object(fields.Datetime, 'now', return_value='2017-11-20 08:00:00')
    def test_00_run_orderpoint(self, fields_now):
        self.env['procurement.order']._fields['date_planned'].default = \
            fields.Datetime.now
        supp_calendar_1 = self.env.ref(
            'stock_procurement_calendar.procurement_calendar_supplier_1')
        wednesday_p11_13 = self.env.ref(
            'stock_procurement_calendar_purchase.'
            'procurement_calendar_supplier_1_attendance_p11_w'
        )
        thursday_p12 = self.env.ref(
            'stock_procurement_calendar_purchase.'
            'procurement_calendar_supplier_1_attendance_p11_th'
        )
        thursday_p11 = self.env.ref(
            'stock_procurement_calendar_purchase.'
            'procurement_calendar_supplier_1_attendance_p11_w'
        )
        self._reset_inventory(self.product_11)
        self._reset_inventory(self.product_12)
        self._reset_inventory(self.product_13)
        self._reset_inventory(self.product_9)

        self.assertEquals(
            thursday_p11,
            self.orderpoint_11.procurement_attendance_id
        )

        self.assertEquals(
            supp_calendar_1,
            self.orderpoint_11.procurement_calendar_id
        )

        # Monday
        self.env['procurement.order']._procure_orderpoint_confirm()
        procurement_11 = self.env['procurement.order'].search([
            ('product_id', '=', self.product_11.id),
            ('state', '=', 'running'),
            ('orderpoint_id', '=', self.orderpoint_11.id)
        ])
        procurement_12 = self.env['procurement.order'].search([
            ('product_id', '=', self.product_12.id),
            ('state', '=', 'running'),
            ('orderpoint_id', '=', self.orderpoint_12.id)
        ])
        procurement_13 = self.env['procurement.order'].search([
            ('product_id', '=', self.product_13.id),
            ('state', '=', 'running'),
            ('orderpoint_id', '=', self.orderpoint_13.id)
        ])
        po_1 = self.env['purchase.order'].search([
            ('procurement_attendance_id', '=', wednesday_p11_13.id)
        ])
        po_2 = self.env['purchase.order'].search([
            ('procurement_attendance_id', '=', thursday_p12.id)
        ])
        self.assertEquals(
            1,
            len(procurement_11)
        )
        self.assertEquals(
            1,
            len(procurement_12)
        )
        self.assertEquals(
            1,
            len(procurement_13)
        )
        self.assertEquals(
            supp_calendar_1,
            procurement_12.procurement_calendar_id
        )
        self.assertEquals(
            wednesday_p11_13,
            procurement_11.procurement_attendance_id
        )
        self.assertEquals(
            1,
            len(po_1)
        )
        self.assertEquals(
            self.product_11 + self.product_13,
            po_1.order_line.mapped('product_id')
        )
        self.assertEquals(
            thursday_p12,
            procurement_12.procurement_attendance_id
        )
        self.assertEquals(
            1,
            len(po_2)
        )
        self.assertEquals(
            self.product_12,
            po_2.order_line.mapped('product_id')
        )

    @patch.object(fields.Datetime, 'now', return_value='2017-11-20 08:00:00')
    def test_01_run_orderpoint_with_date(self, fields_now):
        self.env['procurement.order']._fields['date_planned'].default = \
            fields.Datetime.now
        supp_calendar_1 = self.env.ref(
            'stock_procurement_calendar.procurement_calendar_supplier_1')
        wednesday_p11 = self.env.ref(
            'stock_procurement_calendar_purchase.'
            'procurement_calendar_supplier_1_attendance_p11_w'
        )
        self._reset_inventory(self.product_11)
        self._reset_inventory(self.product_12)
        self._reset_inventory(self.product_13)

        vals = {
            'name': 'Move OUT 20/11/2017',
            'date': '2017-11-20 09:00:00',
            'location_id': self.ref('stock.stock_location_stock'),
            'location_dest_id': self.ref('stock.stock_location_customers'),
            'product_id': self.product_11.id,
            'product_uom_qty': 11.0,
            'product_uom': self.product_11.uom_id.id
        }
        move = self.env['stock.move'].create(vals)
        move.action_confirm()
        self.assertEquals(
            12.0,
            self.orderpoint_11.procure_recommended_qty
        )
        self.assertEquals(
            supp_calendar_1,
            self.orderpoint_11.procurement_calendar_id
        )
        self.env['procurement.order']._procure_orderpoint_confirm()
        procurement_11 = self.env['procurement.order'].search([
            ('product_id', '=', self.product_11.id),
            ('state', '=', 'running'),
            ('orderpoint_id', '=', self.orderpoint_11.id)
        ])
        self.assertEquals(
            23.0,
            procurement_11.product_qty
        )
        self.assertEquals(
            supp_calendar_1,
            procurement_11.procurement_calendar_id
        )
        self.assertEquals(
            wednesday_p11,
            procurement_11.procurement_attendance_id
        )
        po_1 = self.env['purchase.order'].search([
            ('procurement_attendance_id', '=', wednesday_p11.id)
        ])
        self.assertEquals(
            1,
            len(po_1)
        )
        line_p11 = po_1.order_line.filtered(
            lambda l: l.product_id == self.product_11)
        self.assertEquals(
            23.0,
            line_p11.product_qty
        )
        all_pos = self.env['purchase.order.line'].search([
            ('product_id', '=', self.product_11.id),
            ('order_id.state', '=', 'draft')
        ])
        self.assertEquals(
            1,
            len(all_pos)
        )

    @patch.object(fields.Datetime, 'now', return_value='2017-11-20 09:00:00')
    def test_02_run_orderpoint_with_delivery_date(self, fields_now):
        self.env['procurement.order']._fields['date_planned'].default = \
            fields.Datetime.now
        supp_calendar_1 = self.env.ref(
            'stock_procurement_calendar.procurement_calendar_supplier_1')
        wednesday_p11 = self.env.ref(
            'stock_procurement_calendar_purchase.'
            'procurement_calendar_supplier_1_attendance_p11_w'
        )
        thursday_p12 = self.env.ref(
            'stock_procurement_calendar_purchase.'
            'procurement_calendar_supplier_1_attendance_p11_th'
        )
        stock_attendance_monday = self.env.ref(
            'stock_procurement_calendar.'
            'procurement_calendar_1_attendance_mm'
        )
        wednesday_p11.procurement_attendance_id = stock_attendance_monday
        self._reset_inventory(self.product_11)
        self._reset_inventory(self.product_12)
        self._reset_inventory(self.product_13)

        vals = {
            'name': 'Move OUT 20/11/2017',
            'date': '2017-11-20 09:00:00',
            'location_id': self.ref('stock.stock_location_stock'),
            'location_dest_id': self.ref('stock.stock_location_customers'),
            'product_id': self.product_11.id,
            'product_uom_qty': 11.0,
            'product_uom': self.product_11.uom_id.id
        }
        move = self.env['stock.move'].create(vals)
        move.action_confirm()
        self.assertEquals(
            12.0,
            self.orderpoint_11.procure_recommended_qty
        )
        self.assertEquals(
            supp_calendar_1,
            self.orderpoint_11.procurement_calendar_id
        )
        self.env['procurement.order']._procure_orderpoint_confirm()
        procurement_11 = self.env['procurement.order'].search([
            ('product_id', '=', self.product_11.id),
            ('state', '=', 'running'),
            ('orderpoint_id', '=', self.orderpoint_11.id)
        ])
        self.assertEquals(
            23.0,
            procurement_11.product_qty
        )
        self.assertEquals(
            supp_calendar_1,
            procurement_11.procurement_calendar_id
        )
        self.assertEquals(
            wednesday_p11,
            procurement_11.procurement_attendance_id
        )
        po_1 = self.env['purchase.order'].search([
            ('procurement_attendance_id', '=', wednesday_p11.id)
        ])
        po_2 = self.env['purchase.order'].search([
            ('procurement_attendance_id', '=', thursday_p12.id)
        ])
        self.assertEquals(
            1,
            len(po_1)
        )
        self.assertEquals(
            1,
            len(po_2)
        )
        line_p11 = po_1.order_line.filtered(
            lambda l: l.product_id == self.product_11)
        self.assertEquals(
            23.0,
            line_p11.product_qty
        )
        all_pos = self.env['purchase.order.line'].search([
            ('product_id', '=', self.product_11.id),
            ('order_id.state', '=', 'draft')
        ])
        self.assertEquals(
            1,
            len(all_pos)
        )
        self.assertEquals(
            '2017-11-22 07:00:00',
            po_1.date_order
        )
        self.assertEquals(
            '2017-11-27 07:00:00',
            po_1.date_planned
        )
        self.assertEquals(
            '2017-11-23 07:00:00',
            po_2.date_order
        )
        self.assertEquals(
            '2017-11-23 07:00:00',
            po_2.date_planned
        )

    def test_02_expected_seller(self):
        self.assertEquals(
            self.supplier_1,
            self.orderpoint_11.expected_seller_id.name,
            'The expected seller is incorrect'
        )

    def test_03_procure_recommended(self):
        self._reset_inventory(self.product_9)
        self.assertEquals(
            20.0,
            self.orderpoint_9.procure_recommended_qty
        )

    def test_04_procure_recommended_multiple(self):
        self.orderpoint_9.qty_multiple = 3.0
        self._reset_inventory(self.product_9)
        self.assertEquals(
            21.0,
            self.orderpoint_9.procure_recommended_qty
        )
