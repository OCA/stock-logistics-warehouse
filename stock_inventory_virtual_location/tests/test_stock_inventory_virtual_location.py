# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import SavepointCase


class TestStockInventoryDestinationLocation(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockInventoryDestinationLocation, cls).setUpClass()

        # MODELS
        cls.stock_inventory = cls.env['stock.inventory']
        cls.stock_location = cls.env['stock.location']
        cls.stock_move = cls.env['stock.move']
        cls.product_product_model = cls.env['product.product']
        cls.product_category_model = cls.env['product.category']

        # INSTANCES
        cls.category = cls.product_category_model.create({
            'name': 'Physical (test)'})

    def _create_product(self, name):
        return self.product_product_model.create({
            'name': name,
            'categ_id': self.category.id,
            'type': 'product'})

    def test_1(self):
        """ Check case the virtual_location_id is empty.
        """
        product = self._create_product('product_1')
        # create inventory adjustment
        inventory = self.stock_inventory.create({
            'name': 'adjustment test',
            'filter': 'product',
            'product_id': product.id,
        })
        inventory._onchange_filter()
        inventory.action_start()
        line = fields.first(inventory.line_ids.filtered(
            lambda l: l.product_id.id == product.id))

        # check using empty virtual_location_id
        line.virtual_location_id = self.stock_location
        line.product_qty = 3
        inventory._action_done()

        move = self.stock_move.search([
            ('product_id', '=', product.id),
            ('inventory_id', '=', inventory.id),
        ], limit=1)

        self.assertEqual(move.location_id,
                         line.product_id.property_stock_inventory)

    def test_2(self):
        """ Check the virtual_location_id is filled correctly.
        """
        product = self._create_product('product_1')
        # create inventory adjustment
        inventory = self.stock_inventory.create({
            'name': 'adjustment test',
            'filter': 'product',
            'product_id': product.id,
        })
        inventory._onchange_filter()
        inventory.action_start()
        line = fields.first(inventory.line_ids.filtered(
            lambda l: l.product_id.id == product.id))

        # change: virtual_location_id
        new_location = self.stock_location.create({
            'name': 'new location',
            'usage': 'inventory',
        })
        line.virtual_location_id = new_location
        line.product_qty = 3
        inventory._action_done()

        move = self.stock_move.search([
            ('product_id', '=', product.id),
            ('inventory_id', '=', inventory.id),
        ], limit=1)

        self.assertEqual(move.location_id, line.virtual_location_id)
