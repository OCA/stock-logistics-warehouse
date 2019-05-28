# Copyright 2015 AvanzOSC - Oihane Crucelaegi
# Copyright 2015 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestStockInventoryPreparationFilterCategories(common.TransactionCase):
    def setUp(self):
        super(TestStockInventoryPreparationFilterCategories, self).setUp()
        self.inventory_model = self.env['stock.inventory']
        # Create some categories
        self.category = self.env['product.category'].create({
            'name': 'Category for inventory',
        })
        self.category2 = self.env['product.category'].create({
            'name': 'Category for inventory 2',
        })
        # Create some products in the category
        self.product1 = self.env['product.product'].create({
            'name': 'Product for inventory 1',
            'type': 'product',
            'categ_id': self.category.id,
            'default_code': 'PROD1-TEST',
        })
        self.product2 = self.env['product.product'].create({
            'name': 'Product for inventory 2',
            'type': 'product',
            'categ_id': self.category.id,
            'default_code': 'PROD2-TEST',
        })
        self.product3 = self.env['product.product'].create({
            'name': 'Product for inventory 3',
            'type': 'product',
            'categ_id': self.category.id,
            'default_code': 'PROD3-TEST',
        })
        self.product_lot = self.env['product.product'].create({
            'name': 'Product for inventory with lots',
            'type': 'product',
            'categ_id': self.category2.id,
        })
        self.lot = self.env['stock.production.lot'].create({
            'name': 'Lot test',
            'product_id': self.product_lot.id,
        })
        # Add user to lot tracking group
        self.env.user.groups_id = [
            (4, self.env.ref('stock.group_production_lot').id),
        ]
        # And have some stock in a location
        self.location = self.env['stock.location'].create({
            'name': 'Inventory tests',
            'usage': 'internal',
        })
        inventory = self.inventory_model.create({
            'name': 'Product1 inventory',
            'filter': 'product',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 2.0,
                    'location_id': self.location.id,
                }),
                (0, 0, {
                    'product_id': self.product2.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 4.0,
                    'location_id': self.location.id,
                }),
                (0, 0, {
                    'product_id': self.product_lot.id,
                    'product_uom_id': self.env.ref(
                        "uom.product_uom_unit").id,
                    'product_qty': 6.0,
                    'location_id': self.location.id,
                    'prod_lot_id': self.lot.id,
                }),
            ],
        })
        inventory._action_done()

    def test_inventory_category_filter(self):
        inventory = self.inventory_model.create({
            'name': 'Category inventory',
            'filter': 'categories',
            'location_id': self.location.id,
            'categ_ids': [(6, 0, [self.category.id])],
        })
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.location_id, self.location)

    def test_inventory_products_filter(self):
        inventory = self.inventory_model.create({
            'name': 'Products inventory',
            'filter': 'products',
            'location_id': self.location.id,
            'product_ids': [(6, 0, [self.product1.id, self.product2.id])],
        })
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.location_id, self.location)

    def test_inventory_lots_filter(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Products inventory',
                'filter': 'lots',
                'location_id': self.location.id,
                'lot_ids': [(6, 0, [self.lot.id, ])],
            }
        )
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 1)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product_lot)
        self.assertEqual(line1.prod_lot_id, self.lot)
        self.assertEqual(line1.theoretical_qty, 6.0)
        self.assertEqual(line1.location_id, self.location)

    def test_inventory_empty_filter(self):
        inventory = self.inventory_model.create({
            'name': 'Products inventory',
            'filter': 'empty',
            'location_id': self.location.id,
            'empty_line_ids': [
                (0, 0, {
                    'product_code': 'PROD1-TEST',
                    'product_qty': 3.0,
                }),
                (0, 0, {
                    'product_code': 'PROD2-TEST',
                    'product_qty': 7.0,
                }),
                (0, 0, {
                    'product_code': 'PROD3-TEST',
                    'product_qty': 5.0,
                }),
                (0, 0, {
                    'product_code': 'UNEXISTING-CODE',
                    'product_qty': 0.0,
                }),
            ],
        })
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 3)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.product_qty, 3.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.product_qty, 7.0)
        self.assertEqual(line2.location_id, self.location)
        line3 = inventory.line_ids[2]
        self.assertEqual(line3.product_id, self.product3)
        self.assertEqual(line3.theoretical_qty, 0.0)
        self.assertEqual(line3.product_qty, 5.0)
        self.assertEqual(line3.location_id, self.location)
