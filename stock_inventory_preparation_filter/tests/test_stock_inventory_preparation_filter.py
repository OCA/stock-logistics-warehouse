##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp.tests.common as common


class TestStockInventoryPreparationFilterCategories(common.TransactionCase):

    def setUp(self):
        super(TestStockInventoryPreparationFilterCategories, self).setUp()
        self.inventory_model = self.env['stock.inventory']
        # Create a category
        self.category = self.env['product.category'].create(
            {
                'name': 'Category for inventory',
                'type': 'normal',
            })
        # Create some products in the category
        self.product1 = self.env['product.product'].create(
            {
                'name': 'Product for inventory 1',
                'type': 'product',
                'categ_id': self.category.id,
                'default_code': 'PROD1',
            }
        )
        self.product2 = self.env['product.product'].create(
            {
                'name': 'Product for inventory 2',
                'type': 'product',
                'categ_id': self.category.id,
                'default_code': 'PROD2',
            }
        )
        # And have some stock in a location
        self.location = self.env['stock.location'].create(
            {
                'name': 'Inventory tests',
                'usage': 'internal',
            }
        )
        inventory = self.inventory_model.create(
            {
                'name': 'Product1 inventory',
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
                        'location_id': self.location.id,
                    }),
                ],
            })
        inventory.action_done()

    def test_inventory_none_filter_only_with_stock(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Only with stock inventory',
                'filter': 'none',
                'location_id': self.location.id,
                'import_products': 'only_with_stock',
            }
        )
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.location_id, self.location)

    def test_inventory_none_filter_all(self):
        inventory = self.inventory_model.create(
            {
                'name': 'All inventory',
                'filter': 'none',
                'location_id': self.location.id,
                'import_products': 'only_with_stock',
            }
        )
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.location_id, self.location)

    def test_inventory_category_filter_only_with_stock(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Category inventory Only with Stock',
                'filter': 'categories',
                'location_id': self.location.id,
                'import_products': 'only_with_stock',
                'categ_ids': [(6, 0, [self.category.id])],
            }
        )
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.location_id, self.location)

    def test_inventory_category_filter_all(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Category inventory All',
                'filter': 'categories',
                'location_id': self.location.id,
                'import_products': 'only_with_stock',
                'categ_ids': [(6, 0, [self.category.id])],
            }
        )
        inventory.prepare_inventory()
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
        inventory = self.inventory_model.create(
            {
                'name': 'Products inventory',
                'filter': 'products',
                'location_id': self.location.id,
                'product_ids': [(6, 0, [self.product1.id, self.product2.id])],
            }
        )
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.location_id, self.location)

    def test_inventory_empty_filter(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Products inventory',
                'filter': 'empty',
                'location_id': self.location.id,
                'empty_line_ids': [
                    (0, 0, {
                        'product_code': 'PROD1',
                        'product_qty': 3.0,
                    }),
                    (0, 0, {
                        'product_code': 'PROD2',
                        'product_qty': 7.0,
                    }),
                ],
            }
        )
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
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
