# Copyright 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.osv.expression import TRUE_LEAF


class TestPotentialQty(TransactionCase):
    """Test the potential quantity on a product with a multi-line BoM"""

    def setUp(self):
        super(TestPotentialQty, self).setUp()

        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]
        self.bom_line_model = self.env["mrp.bom.line"]
        self.stock_quant_model = self.env["stock.quant"]
        self.config = self.env['ir.config_parameter']
        self.location = self.env['stock.location']
        # Get the warehouses
        self.wh_main = self.browse_ref('stock.warehouse0')
        self.wh_ch = self.browse_ref('stock.stock_warehouse_shop0')

        # We need to compute parent_left and parent_right of the locations as
        # they are used to compute qty_available of the product.
        self.location._parent_store_compute()
        self.setup_demo_data()

    def setup_demo_data(self):
        #  An interesting product (multi-line BoM, variants)
        self.tmpl = self.browse_ref(
            'mrp.product_product_build_kit_product_template')
        #  First variant
        self.var1 = self.browse_ref('mrp.product_product_build_kit')
        self.var1.type = 'product'
        #  Second variant
        self.var2 = self.browse_ref(
            'stock_available_mrp.product_kit_1a')
        self.var2.type = 'product'
        # Components that can be used to make the product
        component_ids = [
            # KeyBoard
            self.ref('product.product_product_9'),
            # Mouse
            self.ref('product.product_product_12'),
        ]

        # Zero-out the inventory of all variants and components
        for component_id in (
                component_ids + [v.id
                                 for v in self.tmpl.product_variant_ids]):
            prod = self.product_model.browse(component_id)
            self.env['stock.quant'].search([
                ('product_id', '=', prod.id)
            ]).unlink()

        self.product_model.invalidate_cache()
        #  A product without a BoM
        self.product_wo_bom = self.browse_ref('product.product_product_11')

        #  Record the initial quantity available for sale
        self.initial_usable_qties = {i.id: i.immediately_usable_qty
                                     for i in [self.tmpl,
                                               self.var1,
                                               self.var2,
                                               self.product_wo_bom]}

    def create_inventory(self, product_id, qty, location_id=None):
        if location_id is None:
            location_id = self.wh_main.lot_stock_id.id

        inventory = self.env['stock.inventory'].create({
            'name': 'Test inventory',
            'location_id': location_id,
            'filter': 'partial'
        })
        inventory.action_start()
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': product_id,
            'location_id': location_id,
            'product_qty': qty
        })
        inventory.action_done()

    def create_simple_bom(self, product, sub_product,
                          product_qty=1, sub_product_qty=1,
                          routing_id=False):
        bom = self.bom_model.create({
            'product_tmpl_id': product.product_tmpl_id.id,
            'product_id': product.id,
            'product_qty': product_qty,
            'routing_id': routing_id,
        })
        self.bom_line_model.create({
            'bom_id': bom.id,
            'product_id': sub_product.id,
            'product_qty': sub_product_qty,
        })

        return bom

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

        # Receive 1000x CPUI5s owned by Chicago
        inventory = self.env['stock.inventory'].create(
            {'name': 'Receive CPUa8',
             'company_id': chicago_id,
             'location_id': self.wh_ch.lot_stock_id.id,
             'filter': 'partial'})
        inventory.action_start()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'company_id': chicago_id,
             'product_id': self.ref('product.product_product_9'),
             'location_id': self.wh_ch.lot_stock_id.id,
             'product_qty': 1000.0})
        inventory.action_done()

        # Put RAM-SR5 owned by Chicago for 1000x the 1st variant in main WH
        inventory = self.env['stock.inventory'].create(
            {'name': 'components for 1st variant',
             'company_id': chicago_id,
             'location_id': self.wh_ch.lot_stock_id.id,
             'filter': 'partial'})
        inventory.action_start()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'company_id': chicago_id,
             'product_id': self.ref('product.product_product_12'),
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
             'groups_id': [(4, self.ref('stock.group_stock_user')),
                           (4, self.ref('mrp.group_mrp_user'))]})

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

        # Receive 1000x Mouses
        inventory = self.env['stock.inventory'].create(
            {'name': 'Receive Mouses',
             'location_id': self.wh_main.lot_stock_id.id,
             'filter': 'partial'})
        inventory.action_start()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.ref('product.product_product_12'),
             'location_id': self.wh_main.lot_stock_id.id,
             'product_qty': 1000.0})
        inventory.action_done()
        for i in [self.tmpl, self.var1, self.var2]:
            self.assertPotentialQty(
                i, 0.0,
                "Receiving a single component should not change the "
                "potential of %s" % i)

        # Receive enough keyboard to make 1000x the 1st variant in main WH
        inventory = self.env['stock.inventory'].create(
            {'name': 'components for 1st variant',
             'location_id': self.wh_main.lot_stock_id.id,
             'filter': 'partial'})
        inventory.action_start()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.ref(
                 'product.product_product_9'),
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

        # Receive enough components to make 313 the 2nd variant at Chicago
        inventory = self.env['stock.inventory'].create(
            {'name': 'components for 2nd variant',
             'location_id': self.wh_ch.lot_stock_id.id,
             'filter': 'partial'})
        inventory.action_start()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.ref('product.product_product_12'),
             'location_id': self.wh_ch.lot_stock_id.id,
             'product_qty': 1000.0})
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.ref(
                 'stock_available_mrp.product_product_9_white'),
             'location_id': self.wh_ch.lot_stock_id.id,
             'product_qty': 313.0})
        inventory.action_done()
        self.assertPotentialQty(
            self.tmpl, 1000.0,
            "Wrong template potential after receiving components")
        self.assertPotentialQty(
            self.var1, 1000.0,
            "Receiving variant 2's component should not change "
            "variant 1's potential")
        self.assertPotentialQty(
            self.var2, 313.0,
            "Wrong variant 2 potential after receiving components")
        # Check by warehouse
        self.assertPotentialQty(
            self.tmpl.with_context(warehouse=self.wh_main.id), 1000.0,
            "Wrong potential quantity in main WH")
        self.assertPotentialQty(
            self.tmpl.with_context(warehouse=self.wh_ch.id), 313.0,
            "Wrong potential quantity in Chicago WH")
        # Check by location
        self.assertPotentialQty(
            self.tmpl.with_context(
                location=self.wh_main.lot_stock_id.id), 1000.0,
            "Wrong potential quantity in main WH location")
        self.assertPotentialQty(
            self.tmpl.with_context(
                location=self.wh_ch.lot_stock_id.id),
            313.0,
            "Wrong potential quantity in Chicago WH location")

    def test_multi_unit_recursive_bom(self):
        # Test multi-level and multi-units BOM
        uom_unit = self.env.ref('product.product_uom_unit')
        uom_unit.rounding = 1.0
        p1 = self.product_model.create({
            'name': 'Test product with BOM',
            'type': 'product',
            'uom_id': self.env.ref('product.product_uom_unit').id,
        })

        p2 = self.product_model.create({
            'name': 'Test sub product with BOM',
            'type': 'product',
            'uom_id': self.env.ref('product.product_uom_unit').id,
        })

        p3 = self.product_model.create({
            'name': 'Test component',
            'type': 'product',
            'uom_id': self.env.ref('product.product_uom_unit').id,
        })

        bom_p1 = self.bom_model.create({
            'product_tmpl_id': p1.product_tmpl_id.id,
            'product_id': p1.id,
        })

        self.bom_line_model.create({
            'bom_id': bom_p1.id,
            'product_id': p3.id,
            'product_qty': 1,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,

        })

        # Two p2 which have a bom
        self.bom_line_model.create({
            'bom_id': bom_p1.id,
            'product_id': p2.id,
            'product_qty': 2,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,

        })

        bom_p2 = self.bom_model.create({
            'product_tmpl_id': p2.product_tmpl_id.id,
            'product_id': p2.id,
            'type': 'phantom',
        })

        # p2 need 2 unit of component
        self.bom_line_model.create({
            'bom_id': bom_p2.id,
            'product_id': p3.id,
            'product_qty': 2,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,

        })

        p1.refresh()

        # Need a least 5 units for one P1
        self.assertEqual(0, p1.potential_qty)

        self.create_inventory(p3.id, 1)
        p1.refresh()
        self.assertEqual(0, p1.potential_qty)

        self.create_inventory(p3.id, 3)
        p1.refresh()
        self.assertEqual(0, p1.potential_qty)

        self.create_inventory(p3.id, 5)
        p1.refresh()
        self.assertEqual(1.0, p1.potential_qty)

        self.create_inventory(p3.id, 6)
        p1.refresh()
        self.assertEqual(1.0, p1.potential_qty)

        self.create_inventory(p3.id, 10)
        p1.refresh()
        self.assertEqual(2.0, p1.potential_qty)

    def test_component_stock_choice(self):
        # Test to change component stock for compute BOM stock

        # Get a demo product with outgoing move (qty: 3)
        prod = self.browse_ref('product.product_product_20')

        # Set on hand qty
        self.create_inventory(prod.id, 3)

        # Create a product with BOM
        p1 = self.product_model.create({
            'name': 'Test product with BOM',
        })
        bom_p1 = self.bom_model.create({
            'product_tmpl_id': p1.product_tmpl_id.id,
            'product_id': p1.id,
            'product_qty': 1,
        })

        # Need 1 prod for that
        self.bom_line_model.create({
            'bom_id': bom_p1.id,
            'product_id': prod.id,
            'product_qty': 1,
        })

        # Default component is qty_available
        p1.refresh()
        self.assertEqual(3.0, p1.potential_qty)

        # Change to immediately usable
        self.config.set_param('stock_available_mrp_based_on',
                              'immediately_usable_qty')

        p1.refresh()
        self.assertEqual(0.0, p1.potential_qty)

        # If iMac has a Bom and can be manufactured
        component = self.product_model.create({
            'name': 'component',
            'type': 'product'
        })
        self.create_inventory(component.id, 5)

        imac_bom = self.bom_model.create({
            'product_tmpl_id': prod.product_tmpl_id.id,
            'product_id': prod.id,
            'product_qty': 1,
            'type': 'phantom',
        })

        # Need 1 component for prod
        self.bom_line_model.create({
            'bom_id': imac_bom.id,
            'product_id': component.id,
            'product_qty': 1,
        })

        p1.refresh()
        self.assertEqual(5.0, p1.potential_qty)

        # Changing to virtual (same as immediately in current config)
        self.config.set_param('stock_available_mrp_based_on',
                              'virtual_available')
        p1.refresh()
        self.assertEqual(5.0, p1.potential_qty)

    def test_potential_qty_list(self):
        # Try to highlight a bug when _get_potential_qty is called on
        # a recordset with multiple products
        # Recursive compute is not working

        p1 = self.product_model.create({'name': 'Test P1'})
        p2 = self.product_model.create({'name': 'Test P2'})
        p3 = self.product_model.create({'name': 'Test P3', 'type': 'product'})

        self.config.set_param('stock_available_mrp_based_on',
                              'immediately_usable_qty')

        # P1 need one P2
        self.create_simple_bom(p1, p2)
        # P2 need one P3
        self.create_simple_bom(p2, p3)

        self.create_inventory(p3.id, 3)

        self.product_model.invalidate_cache()

        products = self.product_model.search(
            [('id', 'in', [p1.id, p2.id, p3.id])]
        )

        self.assertEqual(
            {p1.id: -1.0, p2.id: 3.0, p3.id: 0.0},
            {p.id: p.potential_qty for p in products}
        )

    def test_potential_quantity_service_and_stockable(self):
        stockable_product = self.product_model.create(
            {'name': 'Test Product', 'type': 'product'}
        )
        service_product = self.product_model.create(
            {'name': 'Test PService', 'type': 'service'}
        )

        # stockable_product need one service_product
        self.create_simple_bom(stockable_product, service_product)

        self.assertEqual(stockable_product.potential_qty, -1.0)

    def test_potential_quantity_consumable_and_stockable(self):
        stockable_product = self.product_model.create(
            {'name': 'Test Product', 'type': 'product'}
        )
        consumable_product = self.product_model.create(
            {'name': 'Test PService', 'type': 'consu'}
        )

        # stockable_product need one consumable_product
        self.create_simple_bom(stockable_product, consumable_product)

        self.assertEqual(stockable_product.potential_qty, -1.0)
