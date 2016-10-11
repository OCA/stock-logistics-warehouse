# -*- coding: utf-8 -*-

from openerp.addons.stock.tests.common import TestStockCommon
from openerp.tools import mute_logger


class TestLotQuantity(TestStockCommon):

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.models')
    def test_00_picking_create_and_verify_lot_quantity(self):
        """  Verify stock pro production lot.
             Make inventories to add stock with the same production lot
             on different locations."""
        LotObj = self.env['stock.production.lot']
        stock_location_shelf_1 = self.ref('stock.stock_location_components')
        stock_location_shelf_2 = self.ref('stock.stock_location_14')

        # --------------------------------------------------------------
        # Create first inventory to add lot with quantity on location 1.
        # --------------------------------------------------------------
        lot1_productB = LotObj.create({'name': 'Lot 1B',
                                       'product_id': self.productB.id})
        inventory = self.InvObj.create({'name': 'Test Lot Quantity',
                                        'filter': 'none'})
        inventory.prepare_inventory()
        self.InvLineObj.create({'inventory_id': inventory.id,
                                'product_id': self.productB.id,
                                'product_uom_id': self.productB.uom_id.id,
                                'product_qty': 10,
                                'location_id': stock_location_shelf_1,
                                'prod_lot_id': lot1_productB.id})
        inventory.action_done()
        self.assertEqual(lot1_productB.qty_available, 10,
                         "Wrong qty available for lot")

        # ---------------------------------------------------------------
        # Create second inventory to add lot with quantity on location 1.
        # ---------------------------------------------------------------
        inventory = self.InvObj.create({'name': 'Test Lot Quantity 2',
                                        'filter': 'none'})
        inventory.prepare_inventory()
        self.InvLineObj.create({'inventory_id': inventory.id,
                                'product_id': self.productB.id,
                                'product_uom_id': self.productB.uom_id.id,
                                'product_qty': 20,
                                'location_id': stock_location_shelf_2,
                                'prod_lot_id': lot1_productB.id})
        inventory.action_done()
        self.assertEqual(lot1_productB.qty_available, 30,
                         "Wrong qty available for lot")
