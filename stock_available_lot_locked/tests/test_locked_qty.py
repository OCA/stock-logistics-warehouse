# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestLockedQty(TransactionCase):
    def setUp(self):
        super(TestLockedQty, self).setUp()
        self.warehouse = self.env.ref('stock.warehouse0')
        uom_unit = self.env.ref('product.product_uom_unit')
        self.location = self.env['stock.location'].create(
            {'location_id': self.warehouse.lot_stock_id.id,
             'name': 'test location',
             'usage': 'internal'})
        self.env['stock.location']._parent_store_compute()
        self.owner = self.env['res.partner'].create(
            {'name': 'test owner'})
        self.package = self.env['stock.quant.package'].create(
            {'name': 'test package',
             'owner_id': self.owner.id})

        # Create product template
        self.templateL = self.env['product.template'].create(
            {'name': 'template_product_L',
             'uom_id': uom_unit.id})
        # Create product
        self.productL = self.env['product.product'].create(
            {'name': 'product L',
             'standard_price': 1,
             'type': 'product',
             'uom_id': uom_unit.id,
             'default_code': 'L',
             'product_tmpl_id': self.templateL.id})
        #  Create a lot
        self.lot = self.env['stock.production.lot'].create(
            {'name': 'Test locked lot',
             'product_id': self.productL.id})

        # Make sure we have this lot in stock
        inventory = self.env['stock.inventory'].create(
            {'name': 'Test locked lot',
             'filter': 'partial',
             'location_id': self.location.id})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.productL.id,
             'product_uom_id': self.productL.uom_id.id,
             'product_qty': 15.0,
             'location_id': self.location.id,
             'prod_lot_id': self.lot.id,
             'package_id': self.package.id,
             'partner_id': self.owner.id})
        # Add a second line without lots, packages, owners
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': self.productL.id,
             'product_uom_id': self.productL.uom_id.id,
             'product_qty': 10.0,
             'location_id': self.location.id})
        inventory.action_done()
        self.assertTrue(inventory.move_ids)
        self.productL.refresh()
        self.assertTrue(self.productL.qty_available,
                        "The lot is not in stock")

        #  Record the initial quantity available for sale
        self.initial_usable_qty = self.productL.immediately_usable_qty
        self.assertLockedQty(self.productL, 0.0)

    def assertLockedQty(self, product, qty):
        """Assert locked_qty and immediately_usable_qty equal the parameters"""
        product.refresh()
        self.assertEqual(
            self.initial_usable_qty - product.immediately_usable_qty, qty,
            "The variation of the qty available for sale is incorrect.")
        #  Check the locked q in various contexts
        for recordset in [
                product,
                product.with_context(location=self.location.id),
                product.with_context(lot_id=self.lot.id),
                product.with_context(owner_id=self.owner.id),
                product.with_context(package_id=self.package.id)]:
            self.assertEqual(
                recordset.locked_qty, qty,
                "The locked quantity is incorrect "
                "with context %s" % recordset.env.context)

    def test_lot_locked_qty(self):
        # check quantity locked before lock
        self.assertEqual(self.productL.qty_available, 25.0)
        self.assertLockedQty(self.productL, 0.0)
        self.assertLockedQty(self.templateL, 0.0)

        # lock lot
        self.lot.button_lock()
        self.assertTrue(
            self.lot.locked, "The lot should be locked to start the test")

        # check quantity locked after lock
        self.assertEqual(self.productL.qty_available, 25.0)
        self.assertLockedQty(self.productL, 15.0)
        self.assertLockedQty(self.templateL, 15.0)
