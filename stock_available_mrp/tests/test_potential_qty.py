# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.osv.expression import TRUE_LEAF


class TestPotentialQty(TransactionCase):
    """Test the potential quantity on a product with a multi-line BoM"""

    def setUp(self):
        super(TestPotentialQty, self).setUp()

        #  An interesting product (multi-line BoM, variants)
        self.tmpl = self.browse_ref(
            'product.product_product_4_product_template')
        #  First variant
        self.var1 = self.browse_ref('product.product_product_4c')
        #  Second variant
        self.var2 = self.browse_ref('product.product_product_4')
        # Components that can be used to make the product
        component_ids = [
            # CPUa8
            self.ref('product.product_product_23'),
            # RAM-SR2
            self.ref('product.product_product_14'),
            # HDD SH-2 replaces RAM-SR2 through our demo phantom BoM
            self.ref('product.product_product_18'),
            # RAM-SR3
            self.ref('product.product_product_15')]

        # Zero-out the inventory of all variants and components
        for component_id in (
                component_ids + [v.id
                                 for v in self.tmpl.product_variant_ids]):
            inventory = self.env['stock.inventory'].create(
                {'name': 'no components: %s' % component_id,
                 'location_id': self.ref('stock.stock_location_locations'),
                 'filter': 'product',
                 'product_id': component_id})
            inventory.prepare_inventory()
            inventory.reset_real_qty()
            inventory.action_done()

        #  A product without a BoM
        self.product_wo_bom = self.browse_ref('product.product_product_23')

        #  Record the initial quantity available for sale
        self.initial_usable_qties = {i.id: i.immediately_usable_qty
                                     for i in [self.tmpl,
                                               self.var1,
                                               self.var2,
                                               self.product_wo_bom]}

        # Get the warehouses
        self.wh_main = self.browse_ref('stock.warehouse0')
        self.wh_ch = self.browse_ref('stock.stock_warehouse_shop0')

    def assertPotentialQty(self, record, qty, msg):
        record.refresh()
        #  Check the potential
        self.assertEqual(record.potential_qty, qty, msg)
        # Check the variation of quantity available for sale
        self.assertEqual(
            (record.immediately_usable_qty -
             self.initial_usable_qties[record.id]), qty, msg)

    def test_potential_qty_no_bom(self):
        #  Check the potential when there's no BoM
        self.assertPotentialQty(
            self.product_wo_bom, 0.0,
            "The potential without a BoM should be 0")

    def test_potential_qty_no_bom_for_company(self):
        chicago_id = self.ref('stock.res_company_1')

        # Receive 1000x CPUa8s owned by Chicago
        inventory = self.env['stock.inventory'].create(
            {'name': 'Receive CPUa8',
             'company_id': chicago_id,
             'location_id': self.wh_ch.lot_stock_id.id,
             'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'company_id': chicago_id,
             'product_id': self.ref('product.product_product_23'),
             'location_id': self.wh_ch.lot_stock_id.id,
             'product_qty': 1000.0})
        inventory.action_done()

        # Put RAM-SR3 owned by Chicago for 1000x the 1st variant in main WH
        inventory = self.env['stock.inventory'].create(
            {'name': 'components for 1st variant',
             'company_id': chicago_id,
             'location_id': self.wh_ch.lot_stock_id.id,
             'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'company_id': chicago_id,
             'product_id': self.ref('product.product_product_15'),
             'location_id': self.wh_ch.lot_stock_id.id,
             'product_qty': 1000.0})
        inventory.action_done()
        self.assertPotentialQty(
            self.tmpl, 1000.0,
            "Wrong template potential after receiving components")

        test_user = self.env['res.users'].create(
            {'name': 'test_demo',
             'login': 'test_demo',
             'company_id': self.ref('base.main_company'),
             'company_ids': [(4, self.ref('base.main_company'))],
             'groups_id': [(4, self.ref('stock.group_stock_user'))]})

        bom = self.env['mrp.bom'].search(
            [('product_tmpl_id', '=', self.tmpl.id)])

        test_user_tmpl = self.tmpl.sudo(test_user)
        self.assertPotentialQty(
            test_user_tmpl, 1000.0,
            "Simple user can access to the potential_qty")

        # Set the bom on the main company (visible to members of main company)
        # and all products without company (visible to all)
        # and the demo user on Chicago (child of main company)
        self.env['product.product'].search([
            TRUE_LEAF]).write({'company_id': False})
        test_user.write({'company_id': chicago_id,
                         'company_ids': [(4, chicago_id)]})
        bom.company_id = self.ref('base.main_company')
        self.assertPotentialQty(
            test_user_tmpl, 0,
            "The bom should not be visible to non members of the bom's "
            "company or company child of the bom's company")
        bom.company_id = chicago_id
        self.assertPotentialQty(
            test_user_tmpl, 1000.0, '')

    def test_potential_qty(self):
        for i in [self.tmpl, self.var1, self.var2]:
            self.assertPotentialQty(
                i, 0.0,
                "The potential quantity should start at 0")

        # Receive 1000x CPUa8s
        inventory = self.env['stock.inventory'].create(
            {'name': 'Receive CPUa8',
             'location_id': self.wh_main.lot_stock_id.id,
             'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.ref('product.product_product_23'),
             'location_id': self.wh_main.lot_stock_id.id,
             'product_qty': 1000.0})
        inventory.action_done()
        for i in [self.tmpl, self.var1, self.var2]:
            self.assertPotentialQty(
                i, 0.0,
                "Receiving a single component should not change the "
                "potential of %s" % i)

        # Receive enough RAM-SR3 to make 1000x the 1st variant in main WH
        inventory = self.env['stock.inventory'].create(
            {'name': 'components for 1st variant',
             'location_id': self.wh_main.lot_stock_id.id,
             'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.ref('product.product_product_15'),
             'location_id': self.wh_main.lot_stock_id.id,
             'product_qty': 1000.0})
        inventory.action_done()
        self.assertPotentialQty(
            self.tmpl, 1000.0,
            "Wrong template potential after receiving components")
        self.assertPotentialQty(
            self.var1, 1000.0,
            "Wrong variant 1 potential after receiving components")
        self.assertPotentialQty(
            self.var2, 0.0,
            "Receiving variant 1's component should not change "
            "variant 2's potential")

        # Receive enough components to make 500x the 2nd variant at Chicago
        inventory = self.env['stock.inventory'].create(
            {'name': 'components for 2nd variant',
             'location_id': self.wh_ch.lot_stock_id.id,
             'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.ref('product.product_product_23'),
             'location_id': self.wh_ch.lot_stock_id.id,
             'product_qty': 1000.0})
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.ref('product.product_product_18'),
             'location_id': self.wh_ch.lot_stock_id.id,
             'product_qty': 310.0})
        inventory.action_done()
        self.assertPotentialQty(
            self.tmpl, 1000.0,
            "Wrong template potential after receiving components")
        self.assertPotentialQty(
            self.var1, 1000.0,
            "Receiving variant 2's component should not change "
            "variant 1's potential")
        self.assertPotentialQty(
            self.var2, 500.0,
            "Wrong variant 2 potential after receiving components")
        # Check by warehouse
        self.assertPotentialQty(
            self.tmpl.with_context(warehouse=self.wh_main.id), 1000.0,
            "Wrong potential quantity in main WH")
        self.assertPotentialQty(
            self.tmpl.with_context(warehouse=self.wh_ch.id), 500.0,
            "Wrong potential quantity in Chicago WH")
        # Check by location
        self.assertPotentialQty(
            self.tmpl.with_context(
                location=self.wh_main.lot_stock_id.id), 1000.0,
            "Wrong potential quantity in main WH location")
        self.assertPotentialQty(
            self.tmpl.with_context(
                location=self.wh_ch.lot_stock_id.id),
            500.0,
            "Wrong potential quantity in Chicago WH location")
