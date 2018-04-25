# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestStockInventoryExcludeSublocation(TransactionCase):

    def setUp(self):
        super(TestStockInventoryExcludeSublocation, self).setUp()
        self.inventory_model = self.env['stock.inventory']
        self.location_model = self.env['stock.location']
        self.lot_model = self.env['stock.production.lot']
        self.quant_model = self.env['stock.quant']
        self.package_model = self.env['stock.quant.package']
        self.res_users_model = self.env['res.users']

        self.company = self.env.ref('base.main_company')
        self.partner = self.ref('base.partner_root')
        self.grp_stock_manager = self.env.ref('stock.group_stock_manager')
        self.grp_tracking_owner = self.env.ref('stock.group_tracking_owner')
        self.grp_production_lot = self.env.ref('stock.group_production_lot')
        self.grp_tracking_lot = self.env.ref('stock.group_tracking_lot')

        self.user = self.res_users_model.create({
            'name': 'Test Account User',
            'login': 'user_1',
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
            'groups_id': [(6, 0, [
                self.grp_stock_manager.id,
                self.grp_tracking_owner.id,
                self.grp_production_lot.id,
                self.grp_tracking_lot.id
            ])]
        })

        self.product1 = self.env['product.product'].create({
            'name': 'Product for parent location',
            'type': 'product',
            'default_code': 'PROD1',
        })
        self.product2 = self.env['product.product'].create({
            'name': 'Product for child location',
            'type': 'product',
            'default_code': 'PROD2',
        })
        self.location = self.location_model.create({
            'name': 'Inventory tests',
            'usage': 'internal',
        })
        self.sublocation = self.location_model.create({
            'name': 'Inventory sublocation test',
            'usage': 'internal',
            'location_id': self.location.id
        })
        self.lot_a = self.lot_model.create({
            'name': 'Lot for product1',
            'product_id': self.product1.id
        })
        self.package = self.package_model.create({'name': 'PACK00TEST1'})

        # Add a product in each location
        starting_inv = self.inventory_model.create({
            'name': 'Starting inventory',
            'filter': 'product',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 2.0,
                    'location_id': self.location.id,
                    'prod_lot_id': self.lot_a.id
                }),
                (0, 0, {
                    'product_id': self.product2.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 4.0,
                    'location_id': self.sublocation.id,
                    'prod_lot_id': self.lot_a.id
                }),
            ],
        })
        starting_inv.action_done()

    def _create_inventory_all_products(self, name, location,
                                       exclude_sublocation):
        inventory = self.inventory_model.create({
            'name': name,
            'filter': 'none',
            'location_id': location.id,
            'exclude_sublocation': exclude_sublocation
        })
        return inventory

    def test_not_excluding_sublocations(self):
        """Check if products in sublocations are included into the inventory
        if the excluding sublocations option is disabled."""
        inventory_location = self._create_inventory_all_products(
            'location inventory', self.location, False)
        inventory_location.prepare_inventory()
        inventory_location.action_done()
        lines = inventory_location.line_ids
        self.assertEqual(len(lines), 2, 'Not all expected products are '
                                        'included')

    def test_excluding_sublocations(self):
        """Check if products in sublocations are not included if the exclude
        sublocations is enabled."""
        inventory_location = self._create_inventory_all_products(
            'location inventory', self.location, True)
        inventory_sublocation = self._create_inventory_all_products(
            'sublocation inventory', self.sublocation, True)
        inventory_location.prepare_inventory()
        inventory_location.action_done()
        inventory_sublocation.prepare_inventory()
        inventory_sublocation.action_done()
        lines_location = inventory_location.line_ids
        lines_sublocation = inventory_sublocation.line_ids
        self.assertEqual(len(lines_location), 1,
                         'The products in the sublocations are not excluded')
        self.assertEqual(len(lines_sublocation), 1,
                         'The products in the sublocations are not excluded')

    def test_lot_excluding_sublocation(self):
        """Check if the sublocations are excluded when using lots."""
        inventory = self.inventory_model.sudo(self.user.id).create({
            'name': 'Inventory lot',
            'filter': 'lot',
            'location_id': self.location.id,
            'lot_id': self.lot_a.id,
            'exclude_sublocation': True
        })
        inventory.prepare_inventory()
        inventory.action_done()
        lines = inventory.line_ids
        self.assertEqual(len(lines), 1, 'The products in the sublocations are '
                                        'not excluded with lots.')

    def test_product_and_owner_excluding_sublocation(self):
        """Check if sublocations are excluded when filtering by owner and
        product."""
        self.quant_model.create({
            'product_id': self.product1.id,
            'location_id': self.location.id,
            'qty': 1,
            'owner_id': self.partner,
        })
        inventory = self.inventory_model.sudo(self.user.id).create({
            'name': 'Inventory lot',
            'filter': 'product_owner',
            'location_id': self.location.id,
            'product_id': self.product1.id,
            'partner_id': self.partner,
            'exclude_sublocation': True
        })
        inventory.prepare_inventory()
        lines = inventory.line_ids
        self.assertEqual(len(lines), 1,
                         'The products in the sublocations are '
                         'not excluded with product and owner filter.')

    def test_pack_excluding_sublocation(self):
        """Check if sublocations are excluded when filtering by package."""
        self.quant_model.create({
            'product_id': self.product1.id,
            'location_id': self.location.id,
            'qty': 1,
            'package_id': self.package.id
        })
        inventory = self.inventory_model.sudo(self.user.id).create({
            'name': 'Inventory lot',
            'filter': 'pack',
            'location_id': self.location.id,
            'package_id': self.package.id,
            'exclude_sublocation': True
        })
        inventory.prepare_inventory()
        lines = inventory.line_ids
        self.assertEqual(len(lines), 1, 'The products in the sublocations are '
                                        'not excluded with package filter.')
