# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestStockInventoryExcludeSublocation(common.TransactionCase):

    def setUp(self):
        super(TestStockInventoryExcludeSublocation, self).setUp()
        self.inventory_model = self.env['stock.inventory']
        self.location_model = self.env['stock.location']

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
                }),
                (0, 0, {
                    'product_id': self.product2.id,
                    'product_uom_id': self.env.ref(
                        "product.product_uom_unit").id,
                    'product_qty': 4.0,
                    'location_id': self.sublocation.id,
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
        '''Check if products in sublocations are included into the inventory
        if the excluding sublocations option is disabled.'''
        inventory_location = self._create_inventory_all_products(
            'location inventory', self.location, False)
        inventory_location.prepare_inventory()
        inventory_location.action_done()
        lines = inventory_location.line_ids
        self.assertEqual(len(lines), 2, 'nope')

    def test_excluding_sublocations(self):
        '''Check if products in sublocations are not included if the exclude
        sublocations is enabled.'''
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
        self.assertEqual(len(lines_location), 1, 'no')
        self.assertEqual(len(lines_sublocation), 1, 'nope')
