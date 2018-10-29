# Copyright <2018> <Arturo Flores, Vauxoo>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from mock import patch


class SideEffectUserError(object):
    def __init__(self, **kwargs):
        raise UserError("There is no MTO route")


class TestMtoMtsRoute(TransactionCase):

    def test_standard_mto_mts_buy_and_mrp_routes(self):
        """In this test we added a product that depends on a material that has
        mts+mto and buy routes, the idea is that the product should be placed
        in manufacture and the material to the buy process"""
        self.group.run(self.product, 2.0, self.uom, self.customer_loc,
                       self.product.name, 'test', self.procurement_vals)
        moves = self.move_obj.search([('group_id', '=', self.group.id)])
        self.assertIn(self.bom_bom.name,
                      moves.mapped('product_id').mapped('name'))

    def test_without_mto_route(self):
        """Checking for the MTO route if there is none, it throws an UserError
        we need to catch that error and prove that this module works fine"""

        method_path = ("odoo.addons.stock.models.stock_warehouse.Warehouse."
                       "_get_mto_route")
        with patch(method_path, new=SideEffectUserError):
            self.group.run(self.product, 2.0, self.uom, self.customer_loc,
                           self.product.name, 'test', self.procurement_vals)
        moves = self.move_obj.search([('group_id', '=', self.group.id)])
        self.assertIn(self.bom_bom.name,
                      moves.mapped('product_id').mapped('name'))

    def setUp(self):
        super(TestMtoMtsRoute, self).setUp()
        self.move_obj = self.env['stock.move']
        self.uom = self.env['product.uom'].browse(1)
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse.mto_mts_management = True
        self.customer_loc = self.env.ref('stock.stock_location_customers')
        self.product = self.env.ref('product.product_product_4')
        self.group = self.env['procurement.group'].create({
            'name': 'test',
        })
        self.procurement_vals = {
            'warehouse_id': self.warehouse, 'group_id': self.group
        }
        self.product = self.product
        self.mts_mto_route = self.env['stock.location.route'].search([
            ('name', 'ilike', 'Make To Order + Make To Stock')])
        self.buy_route = self.env['stock.location.route'].search([
            ('name', 'ilike', 'Buy')], limit=1)
        self.mto_route = self.env.ref('stock.route_warehouse0_mto')
        self.manufacture_route = self.env['stock.location.route'].search([
            ('name', 'ilike', 'Manufacture')])
        self.vendor = self.env['res.partner'].search([], limit=1)

        self.product.write({'seller_ids': [(6, 0, [self.vendor.id])]})
        self.product.route_ids = [(6, 0, [self.mto_route.id,
                                          self.manufacture_route.id])]

        self.bom_bom = self.env.ref('product.product_product_3')
        bom_material = self.env['mrp.bom'].create({
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'product_qty': 1,
            'type': 'normal',
            'product_uom_id': self.uom.id,
            'bom_line_ids': [(0, 0, {'product_id': self.bom_bom.id,
                                     'product_qty': 1,
                                     'product_uom_id': self.uom.id})]})

        bom_material.route_ids = [(6, 0, [self.mts_mto_route.id,
                                          self.buy_route.id])]

        self.product.bom_material = bom_material
