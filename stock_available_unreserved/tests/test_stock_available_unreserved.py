# Copyright 2018 Camptocamp SA
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestStockLogisticsWarehouse(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pickingObj = cls.env['stock.picking']
        cls.productObj = cls.env['product.product']
        cls.templateObj = cls.env['product.template']
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.uom_unit = cls.env.ref('product.product_uom_unit')

        # Create product template
        cls.templateAB = cls.templateObj.create({
            'name': 'templAB',
            'uom_id': cls.uom_unit.id,
        })

        # Create product A and B
        cls.productA = cls.productObj.create({
            'name': 'product A',
            'standard_price': 1,
            'type': 'product',
            'uom_id': cls.uom_unit.id,
            'default_code': 'A',
            'product_tmpl_id': cls.templateAB.id,
        })

        cls.productB = cls.productObj.create({
            'name': 'product B',
            'standard_price': 1,
            'type': 'product',
            'uom_id': cls.uom_unit.id,
            'default_code': 'B',
            'product_tmpl_id': cls.templateAB.id,
        })

        # Create a picking move from INCOMING to STOCK
        cls.pickingInA = cls.pickingObj.create({
            'picking_type_id': cls.env.ref('stock.picking_type_in').id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.stock_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': cls.productA.id,
                    'product_uom': cls.productA.uom_id.id,
                    'product_uom_qty': 2,
                    'quantity_done': 2,
                    'location_id': cls.supplier_location.id,
                    'location_dest_id': cls.stock_location.id,
                })
            ]
        })

        cls.pickingInB = cls.pickingObj.create({
            'picking_type_id': cls.env.ref('stock.picking_type_in').id,
            'location_id': cls.supplier_location.id,
            'location_dest_id': cls.stock_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': cls.productB.id,
                    'product_uom': cls.productB.uom_id.id,
                    'product_uom_qty': 3,
                    'quantity_done': 3,
                    'location_id': cls.supplier_location.id,
                    'location_dest_id': cls.stock_location.id,
                })
            ]
        })
        cls.pickingOutA = cls.pickingObj.create({
            'picking_type_id': cls.env.ref('stock.picking_type_out').id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': cls.productB.id,
                    'product_uom': cls.productB.uom_id.id,
                    'product_uom_qty': 2,
                    'location_id': cls.stock_location.id,
                    'location_dest_id': cls.customer_location.id,
                })
            ]
        })

    def compare_qty_available_not_res(self, product, value):
        product.invalidate_cache()
        self.assertEqual(product.qty_available_not_res, value)

    def test_stock_levels(self):
        """checking that qty_available_not_res actually reflects \
        the variations in stock, both on product and template"""

        self.compare_qty_available_not_res(self.productA, 0)
        self.compare_qty_available_not_res(self.templateAB, 0)

        self.pickingInA.action_confirm()
        self.compare_qty_available_not_res(self.productA, 0)
        self.compare_qty_available_not_res(self.templateAB, 0)

        self.pickingInA.action_assign()
        self.compare_qty_available_not_res(self.productA, 0)
        self.compare_qty_available_not_res(self.templateAB, 0)

        self.pickingInA.button_validate()
        self.compare_qty_available_not_res(self.productA, 2)
        self.compare_qty_available_not_res(self.templateAB, 2)

        # will directly trigger action_done on self.productB
        self.pickingInB.action_done()
        self.compare_qty_available_not_res(self.productA, 2)
        self.compare_qty_available_not_res(self.productB, 3)
        self.compare_qty_available_not_res(self.templateAB, 5)

        self.compare_qty_available_not_res(self.productB, 3)
        self.compare_qty_available_not_res(self.templateAB, 5)

        self.pickingOutA.action_confirm()
        self.compare_qty_available_not_res(self.productB, 3)
        self.compare_qty_available_not_res(self.templateAB, 5)

        self.pickingOutA.action_assign()
        self.compare_qty_available_not_res(self.productB, 1)
        self.compare_qty_available_not_res(self.templateAB, 3)

        self.pickingOutA.action_done()
        self.compare_qty_available_not_res(self.productB, 1)
        self.compare_qty_available_not_res(self.templateAB, 3)

        self.templateAB.action_open_quants_unreserved()
