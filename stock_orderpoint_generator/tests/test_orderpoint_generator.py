# Copyright 2016 Cyril Gaudin (Camptocamp)
# Copyright 2019 Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestOrderpointGenerator(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env['stock.warehouse.orderpoint.generator']
        cls.orderpoint_model = cls.env['stock.warehouse.orderpoint']
        cls.orderpoint_template_model = (
            cls.env['stock.warehouse.orderpoint.template'])
        cls.product_model = cls.env['product.product']
        cls.p1 = cls.product_model.create({
            'name': 'Unittest P1',
            'type': 'product',
        })
        cls.p2 = cls.product_model.create({
            'name': 'Unittest P2',
            'type': 'product',
        })
        cls.wh1 = cls.env['stock.warehouse'].create({
            'name': 'TEST WH1',
            'code': 'TST1',
        })
        location_obj = cls.env['stock.location']
        cls.supplier_loc = location_obj.create({
            'name': 'Test supplier location',
            'usage': 'supplier',
        })
        cls.customer_loc = location_obj.create({
            'name': 'Test customer location',
            'usage': 'customer',
        })
        cls.orderpoint_fields_dict = {
            'warehouse_id': cls.wh1.id,
            'location_id': cls.wh1.lot_stock_id.id,
            'name': 'TEST-ORDERPOINT-001',
            'product_max_qty': 15.0,
            'product_min_qty': 5.0,
            'qty_multiple': 1,
        }
        cls.template = cls.orderpoint_template_model.create(
            cls.orderpoint_fields_dict)
        # Create some moves for p1 and p2 so we can have a history to test
        # p1 [100, 50, 45, 55, 52]
        # t1 - p1 - stock.move location1 100 # 100
        cls.p1m1 = cls.env['stock.move'].create({
            'name': cls.p1.name,
            'product_id': cls.p1.id,
            'product_uom_qty': 100,
            'product_uom': cls.p1.uom_id.id,
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'state': 'done',
            'date': '2019-01-01 01:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p1m1.id,
            'product_id': cls.p1.id,
            'qty_done': 100,
            'product_uom_id': cls.p1.uom_id.id,
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'state': 'done',
            'date': '2019-01-01 01:00:00',
        })
        # t2 - p1 - stock.move location1 -50 # 50
        cls.p1m2 = cls.p1m1.copy({
            'product_uom_qty': 50,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 02:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p1m2.id,
            'product_id': cls.p1.id,
            'qty_done': 50,
            'product_uom_id': cls.p1.uom_id.id,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 02:00:00',
        })
        # t3 - p1 - stock.move location1 -5 # 45
        cls.p1m3 = cls.p1m1.copy({
            'name': cls.p1.name,
            'product_id': cls.p1.id,
            'product_uom_qty': 5,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 03:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p1m3.id,
            'product_id': cls.p1.id,
            'qty_done': 5,
            'product_uom_id': cls.p1.uom_id.id,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 03:00:00',
        })
        # t4 - p1 - stock.move location1 10 # 55
        cls.p1m4 = cls.p1m1.copy({
            'product_uom_qty': 10,
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'state': 'done',
            'date': '2019-01-01 04:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p1m4.id,
            'product_id': cls.p1.id,
            'qty_done': 10,
            'product_uom_id': cls.p1.uom_id.id,
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'state': 'done',
            'date': '2019-01-01 04:00:00',
        })
        # t5 - p1 - stock.move location1 -3 # 52
        cls.p1m5 = cls.p1m1.copy({
            'product_uom_qty': 3,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 05:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p1m5.id,
            'product_id': cls.p1.id,
            'qty_done': 3,
            'product_uom_id': cls.p1.uom_id.id,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 05:00:00',
        })
        # p2
        # t1 - p2 - stock.move location1 1000 # 1000
        cls.p2m1 = cls.env['stock.move'].create({
            'name': cls.p2.name,
            'product_id': cls.p2.id,
            'product_uom': cls.p2.uom_id.id,
            'product_uom_qty': 1000,
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'state': 'done',
            'date': '2019-01-01 01:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p2m1.id,
            'product_id': cls.p2.id,
            'qty_done': 1000,
            'product_uom_id': cls.p2.uom_id.id,
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'state': 'done',
            'date': '2019-01-01 01:00:00',
        })
        # t2 - p2 - stock.move location1 -50 # 950
        cls.p2m2 = cls.p2m1.copy({
            'product_uom_qty': 50,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 02:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p2m2.id,
            'product_id': cls.p2.id,
            'qty_done': 50,
            'product_uom_id': cls.p2.uom_id.id,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 02:00:00',
        })
        # t3 - p2 - stock.move location1 -7 # 943
        cls.p2m3 = cls.p2m1.copy({
            'product_uom_qty': 7,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 03:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p2m3.id,
            'product_id': cls.p2.id,
            'qty_done': 7,
            'product_uom_id': cls.p2.uom_id.id,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 03:00:00',
        })
        # t4 - p2 - stock.move location1 100 # 1043
        cls.p2m4 = cls.p2m1.copy({
            'product_uom_qty': 100,
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'state': 'done',
            'date': '2019-01-01 04:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p2m4.id,
            'product_id': cls.p2.id,
            'qty_done': 100,
            'product_uom_id': cls.p2.uom_id.id,
            'location_id': cls.supplier_loc.id,
            'location_dest_id': cls.wh1.lot_stock_id.id,
            'state': 'done',
            'date': '2019-01-01 04:00:00',
        })
        # t5 - p2 - stock.move location1 -3 # 1040
        cls.p2m5 = cls.p2m1.copy({
            'product_uom_qty': 3,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 05:00:00',
        })
        cls.env['stock.move.line'].create({
            'move_id': cls.p2m5.id,
            'product_id': cls.p2.id,
            'qty_done': 3,
            'product_uom_id': cls.p2.uom_id.id,
            'location_id': cls.wh1.lot_stock_id.id,
            'location_dest_id': cls.customer_loc.id,
            'state': 'done',
            'date': '2019-01-01 05:00:00',
        })

    def check_orderpoint(self, products, template, fields_dict):
        orderpoints = self.orderpoint_model.search([
            ('name', '=', template.name)
        ], order='product_id')
        self.assertEqual(len(products), len(orderpoints))
        for i, product in enumerate(products):
            self.assertEqual(product, orderpoints[i].product_id)
        for orderpoint in orderpoints:
            for field in fields_dict.keys():
                op_field_value = orderpoint[field]
                if isinstance(orderpoint[field], models.Model):
                    op_field_value = orderpoint[field].id
                self.assertEqual(op_field_value, fields_dict[field])
        return orderpoints

    def wizard_over_products(self, product, template):
        return self.wizard_model.with_context(
            active_model=product._name,
            active_ids=product.ids,
        ).create({
            'orderpoint_template_id': [(6, 0, template.ids)]
        })

    def test_product_orderpoint(self):
        products = self.p1 + self.p2
        wizard = self.wizard_over_products(products, self.template)
        wizard.action_configure()
        self.check_orderpoint(
            products, self.template, self.orderpoint_fields_dict)

    def test_template_orderpoint(self):
        prod_tmpl = self.p1.product_tmpl_id + self.p2.product_tmpl_id
        wizard = self.wizard_over_products(prod_tmpl, self.template)
        wizard.action_configure()
        products = self.p1 + self.p2
        self.check_orderpoint(
            products, self.template, self.orderpoint_fields_dict)

    def test_template_variants_orderpoint(self):
        self.product_model.create({
            'product_tmpl_id': self.p1.product_tmpl_id.id,
            'name': 'Unittest P1 variant'
        })
        wizard = self.wizard_over_products(
            self.p1.product_tmpl_id, self.template)
        with self.assertRaises(UserError):
            wizard.action_configure()

    def test_auto_qty(self):
        """Compute min and max qty  according to criteria"""
        # Max stock for p1: 100
        self.template.write({
            'auto_min_qty': True,
            'auto_min_date_start': '2019-01-01 00:00:00',
            'auto_min_date_end': '2019-02-01 00:00:00',
            'auto_min_qty_criteria': 'max',
        })
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict = self.orderpoint_fields_dict.copy()
        orderpoint_auto_dict.update({
            'product_min_qty': 100.0,
        })
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Min stock for p1: 45
        self.template.write({
            'auto_min_qty_criteria': 'min',
        })
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({
            'product_min_qty': 45.0,
        })
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Median of stock for p1: 52
        self.template.write({
            'auto_min_qty_criteria': 'median',
        })
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({
            'product_min_qty': 52.0,
        })
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Average of stock for p1: 60.4
        self.template.write({
            'auto_min_qty_criteria': 'avg',
        })
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({
            'product_min_qty': 60.4,
        })
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Set auto values for min and max: 60.4 (avg) 100 (max)
        self.template.write({
            'auto_max_qty': True,
            'auto_max_date_start': '2019-01-01 00:00:00',
            'auto_max_date_end': '2019-02-01 00:00:00',
            'auto_max_qty_criteria': 'max',
        })
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({
            'product_max_qty': 100,
        })
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # If they have the same values, only one is computed:
        self.template.write({
            'auto_min_qty_criteria': 'max',
        })
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({
            'product_min_qty': 100,
        })
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Auto min max over a shorter period
        self.template.write({
            'auto_max_date_start': '2019-01-01 02:00:00',
            'auto_max_date_end': '2019-01-01 03:00:00',
            'auto_min_date_start': '2019-01-01 04:00:00',
            'auto_min_date_end': '2019-01-01 06:00:00',
        })
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({
            'product_min_qty': 55,
            'product_max_qty': 50,
        })
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)

    def test_auto_qty_multi_products(self):
        """Each product has a different history"""
        products = self.p1 + self.p2
        self.template.write({
            'auto_min_qty': True,
            'auto_min_date_start': '2019-01-01 00:00:00',
            'auto_min_date_end': '2019-02-01 00:00:00',
            'auto_min_qty_criteria': 'max',
        })
        wizard = self.wizard_over_products(products, self.template)
        wizard.action_configure()
        orderpoint_auto_dict = self.orderpoint_fields_dict.copy()
        del orderpoint_auto_dict['product_min_qty']
        orderpoints = self.check_orderpoint(
            products, self.template, orderpoint_auto_dict)
        self.assertEqual(orderpoints[0].product_min_qty, 100)
        self.assertEqual(orderpoints[1].product_min_qty, 1043)
