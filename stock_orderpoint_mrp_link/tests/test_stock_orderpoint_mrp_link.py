# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast
from odoo.tests.common import SavepointCase


class TestStockOrderpointMRPLink(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.production_model = cls.env['mrp.production']
        cls.product_model = cls.env['product.product']
        cls.orderpoint_model = cls.env['stock.warehouse.orderpoint']
        cls.loc_model = cls.env['stock.location']
        cls.route_model = cls.env['stock.location.route']
        cls.bom_model = cls.env['mrp.bom']
        cls.boml_model = cls.env['mrp.bom.line']
        cls.group_obj = cls.env['procurement.group']

        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.stock_loc = cls.env.ref('stock.stock_location_stock')
        route_manuf = cls.env.ref('mrp.route_warehouse0_manufacture')

        # Create a new location and route:
        cls.secondary_loc = cls.loc_model.create({
            'name': 'Test location',
            'usage': 'internal',
            'location_id': cls.warehouse.view_location_id.id,
        })
        test_route = cls.route_model.create({
            'name': 'Stock -> Test',
            'product_selectable': True,
            'rule_ids': [(0, 0, {
                'name': 'stock to test',
                'action': 'pull',
                'location_id': cls.secondary_loc.id,
                'location_src_id': cls.stock_loc.id,
                'procure_method': 'make_to_order',
                'picking_type_id': cls.env.ref(
                    'stock.picking_type_internal').id,
                'propagate': True
            })]
        })

        # Prepare Products:
        routes = route_manuf + test_route
        cls.product = cls.product_model.create({
            'name': 'Test Product',
            'route_ids': [(6, 0, routes.ids)],
        })
        component = cls.product_model.create({
            'name': 'Test component',
        })

        # Create Bill of Materials:
        cls.bom_1 = cls.bom_model.create({
            'product_id': cls.product.id,
            'product_tmpl_id': cls.product.product_tmpl_id.id,
            'product_uom_id': cls.product.uom_id.id,
            'product_qty': 1.0,
        })
        cls.boml_model.create({
            'bom_id': cls.bom_1.id,
            'product_id': component.id,
            'product_qty': 1.0,
        })

        # Create Orderpoint:
        cls.orderpoint_stock = cls.orderpoint_model.create({
            'warehouse_id': cls.warehouse.id,
            'location_id': cls.warehouse.lot_stock_id.id,
            'product_id': cls.product.id,
            'product_min_qty': 10.0,
            'product_max_qty': 50.0,
            'product_uom': cls.product.uom_id.id,
        })
        cls.orderpoint_secondary_loc = cls.orderpoint_model.create({
            'warehouse_id': cls.warehouse.id,
            'location_id': cls.secondary_loc.id,
            'product_id': cls.product.id,
            'product_min_qty': 10.0,
            'product_max_qty': 20.0,
            'product_uom': cls.product.uom_id.id,
        })

        cls.group_obj.run_scheduler()

    def test_01_stock_orderpoint_mrp_link(self):
        """Tests manual procurement fills orderpoint_id field.
        Direct MO creation."""
        mo = self.production_model.search([
            ('orderpoint_id', '=', self.orderpoint_stock.id)])
        self.assertTrue(mo)
        self.assertEqual(mo.orderpoint_id, self.orderpoint_stock)
        self.assertEqual(mo.orderpoint_id, self.orderpoint_stock)

    def test_02_stock_orderpoint_mrp_link_indirect_routing(self):
        """Tests manual procurement fills requested_by field.
        Indirect MO creation (transfer -> MO)."""
        mo2 = self.production_model.search([
            ('orderpoint_id', '=', self.orderpoint_secondary_loc.id)])
        self.assertTrue(mo2)
        self.assertEqual(mo2.orderpoint_id, self.orderpoint_secondary_loc)
        self.assertEqual(mo2.orderpoint_id, self.orderpoint_secondary_loc)

    def test_03_stock_orderpoint_mrp_link_action_view(self):
        mo_orderpoint = self.production_model.search([
            ('orderpoint_id', '=', self.orderpoint_secondary_loc.id)])
        result = self.orderpoint_secondary_loc.action_view_mrp_productions()
        mo_action = self.production_model.search(
            ast.literal_eval(result['domain']))
        self.assertEquals(mo_orderpoint, mo_action)
