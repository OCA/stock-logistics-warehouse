# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestStockOrderpointRoute(common.TransactionCase):
    def setUp(self):
        super(TestStockOrderpointRoute, self).setUp()

        # common models
        self.orderpoint_model = self.env[
            'stock.warehouse.orderpoint']
        self.procurement_group_model = self.env['procurement.group']
        # refs
        self.stock_manager_group = \
            self.env.ref('stock.group_stock_manager')
        self.stock_multi_locations_group_group = \
            self.env.ref('stock.group_stock_multi_locations')
        self.main_company = self.env.ref('base.main_company')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.categ_unit = self.env.ref('product.product_uom_categ_unit')
        self.virtual_loc = self.env.ref('stock.stock_location_customers')

        # common data
        self.stock_manager = self._create_user(
            'stock_manager',
            [self.stock_manager_group.id,
             self.stock_multi_locations_group_group.id],
            [self.main_company.id])
        self.product = self._create_product('SH', 'Shoes', False)

        self.ressuply_loc = self.env['stock.location'].create({
            'name': 'Ressuply',
            'location_id': self.warehouse.view_location_id.id,
        })

        self.ressuply_loc2 = self.env['stock.location'].create({
            'name': 'Ressuply2',
            'location_id': self.warehouse.view_location_id.id,
        })

        self.route = self.env['stock.location.route'].create({
            'name': 'Transfer',
            'product_categ_selectable': False,
            'product_selectable': True,
            'company_id': self.main_company.id,
            'sequence': 10,
        })
        self.route2 = self.env['stock.location.route'].create({
            'name': 'Transfer',
            'product_categ_selectable': False,
            'product_selectable': True,
            'company_id': self.main_company.id,
            'sequence': 10,
        })

        self.uom_dozen = self.env['product.uom'].create({
            'name': 'Test-DozenA',
            'category_id': self.categ_unit.id,
            'factor_inv': 12,
            'uom_type': 'bigger',
            'rounding': 0.001})

        self.env['procurement.rule'].create({
            'name': 'Transfer',
            'route_id': self.route.id,
            'location_src_id': self.ressuply_loc.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'action': 'move',
            'picking_type_id': self.warehouse.int_type_id.id,
            'procure_method': 'make_to_stock',
            'warehouse_id': self.warehouse.id,
            'company_id': self.main_company.id,
            'propagate': 'False',
        })

        self.env['procurement.rule'].create({
            'name': 'Transfer 2',
            'route_id': self.route2.id,
            'location_src_id': self.ressuply_loc2.id,
            'location_id': self.warehouse.lot_stock_id.id,
            'action': 'move',
            'picking_type_id': self.warehouse.int_type_id.id,
            'procure_method': 'make_to_stock',
            'warehouse_id': self.warehouse.id,
            'company_id': self.main_company.id,
            'propagate': 'False',
        })

    def _create_user(self, name, group_ids, company_ids):
        return self.env['res.users'].with_context(
            {'no_reset_password': True}).create(
            {'name': name,
             'password': 'demo',
             'login': name,
             'email': '@'.join([name, '@test.com']),
             'groups_id': [(6, 0, group_ids)],
             'company_ids': [(6, 0, company_ids)]
             })

    def _create_product(self, default_code, name, company_id, **vals):
        return self.env['product.product'].create(dict(
            name=name,
            default_code=default_code,
            uom_id=self.env.ref('product.product_uom_unit').id,
            company_id=company_id,
            type='product',
            **vals
        ))

    def test_orderpoint_route_01(self):
        self.product.route_ids = [(6, 0, [self.route.id, self.route2.id])]
        vals = {
            'product_id': self.product.id,
            'product_min_qty': 10.0,
            'product_max_qty': 100.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }

        orderpoint = self.orderpoint_model.sudo(
            self.stock_manager).create(vals)
        self.assertIn(self.route, orderpoint.route_ids)
        self.assertIn(self.route2, orderpoint.route_ids)
        orderpoint.route_id = self.route.id
        self.procurement_group_model.run_scheduler()
        move = self.env['stock.move'].search(
            [('product_id', '=', self.product.id),
             ('location_id', '=', self.ressuply_loc.id)], limit=1)
        self.assertEqual(len(move), 1)

    def test_orderpoint_route_02(self):
        self.product.route_ids = [(6, 0, [self.route.id, self.route2.id])]
        vals = {
            'product_id': self.product.id,
            'product_min_qty': 10.0,
            'product_max_qty': 100.0,
            'company_id': self.main_company.id,
            'warehouse_id': self.warehouse.id,
            'location_id': self.warehouse.lot_stock_id.id,
        }

        orderpoint = self.orderpoint_model.sudo(
            self.stock_manager).create(vals)
        self.assertIn(self.route, orderpoint.route_ids)
        self.assertIn(self.route2, orderpoint.route_ids)
        orderpoint.route_id = self.route2.id
        self.procurement_group_model.run_scheduler()
        move = self.env['stock.move'].search(
            [('product_id', '=', self.product.id),
             ('location_id', '=', self.ressuply_loc2.id)], limit=1)
        self.assertEqual(len(move), 1)
