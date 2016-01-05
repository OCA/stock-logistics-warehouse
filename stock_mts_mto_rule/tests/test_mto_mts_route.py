#    Author: Florian da Costa
#    Copyright 2015 Akretion
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from openerp.tests.common import TransactionCase
from datetime import datetime


class TestMtoMtsRoute(TransactionCase):

    def test_standard_mto_route(self):
        mto_route = self.env.ref('stock.route_warehouse0_mto')
        self.product.route_ids = [(6, 0, [mto_route.id])]
        self.procurement.run()
        self.assertEqual(self.warehouse.mto_pull_id,
                         self.procurement.rule_id)
        self.assertEqual('make_to_order',
                         self.procurement.move_ids[0].procure_method)
        self.assertEqual(self.procurement.product_qty,
                         self.procurement.move_ids[0].product_uom_qty)
        self.assertEqual('waiting',
                         self.procurement.move_ids[0].state)

    def test_standard_mts_route(self):
        self.procurement.run()
        procurement_id = self.procurement_obj.search([
            ('group_id', '=', self.procurement.group_id.id),
            ('move_ids', '!=', False)], limit=1)
        self.assertEqual('make_to_stock',
                         procurement_id.move_ids[0].procure_method)
        self.assertEqual(self.procurement.product_qty,
                         procurement_id.move_ids[0].product_uom_qty)
        self.assertEqual('confirmed',
                         procurement_id.move_ids[0].state)

    def test_mts_mto_route_split(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        self.product.route_ids = [(6, 0, [mto_mts_route.id])]
        self.quant.qty = 1.0
        self.procurement.run()
        moves = self.env['stock.move'].search(
            [('group_id', '=', self.group.id)])
        self.assertEqual(2, len(moves))
        self.assertEqual(1.0, moves[0].product_uom_qty)

    def test_mts_mto_route_mts_only(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        self.product.route_ids = [(6, 0, [mto_mts_route.id])]
        self.quant.qty = 0.0
        self.procurement.run()
        moves = self.env['stock.move'].search(
            [('group_id', '=', self.group.id)])
        self.assertEqual(1, len(moves))
        self.assertEqual(2.0, moves[0].product_uom_qty)
        self.assertEqual('make_to_order',
                         moves[0].procure_method)

    def test_mts_mto_route_mto_only(self):
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        self.product.route_ids = [(6, 0, [mto_mts_route.id])]
        self.quant.qty = 3.0
        self.procurement.run()
        moves = self.env['stock.move'].search(
            [('group_id', '=', self.group.id)])
        self.assertEqual(1, len(moves))
        self.assertEqual(2.0, moves[0].product_uom_qty)
        self.assertEqual('make_to_stock',
                         moves[0].procure_method)

    def setUp(self):
        super(TestMtoMtsRoute, self).setUp()
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse.mto_mts_management = True
        self.product = self.env.ref('product.product_product_4')
        self.company_partner = self.env.ref('base.main_partner')
        self.procurement_obj = self.env['procurement.order']
        self.group = self.env['procurement.group'].create({
            'name': 'test',
        })
        self.procurement = self.env['procurement.order'].create({
            'location_id': self.env.ref('stock.stock_location_customers').id,
            'product_id': self.product.id,
            'product_qty': 2.0,
            'product_uom': 1,
            'warehouse_id': self.warehouse.id,
            'priority': '1',
            'date_planned': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': self.product.name,
            'origin': 'test',
            'group_id': self.group.id,
        })
        self.quant = self.env['stock.quant'].create({
            'owner_id': self.company_partner.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
            'qty': 0.0,
        })
