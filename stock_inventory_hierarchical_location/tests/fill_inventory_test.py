# -*- coding: utf-8 -*-
#
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import openerp.tests.common as common

DB = common.DB
ADMIN_USER_ID = common.ADMIN_USER_ID


class fill_inventory_test(common.TransactionCase):

    def setUp(self):
        super(fill_inventory_test, self).setUp()

    def test_missing_location(self):
        """
        Test that when confirm a parent inventory, the child location are not
        in the confirmation result
        """
        inventory_obj = self.registry('stock.inventory')
        un_loc_obj = self.registry('stock.inventory.uninventoried.locations')
        parent_inventory_id = self.ref(
            'stock_inventory_hierarchical_location.parent_inventory')
        inventory_obj.action_open(
            self.cr, self.uid, [parent_inventory_id])
        # confirm shelf 1 inventory
        inventory_id = self.ref(
            'stock_inventory_hierarchical_location.child_2_id')
        inventory_obj.action_open(
            self.cr, self.uid, [inventory_id])
        missing_location = inventory_obj.get_missing_locations(
            self.cr, self.uid, [inventory_id])
        self.assertEqual(
            len(missing_location), 1, "1 missing location should be find, "
            "because the inventory is empty")
        wizard_id = un_loc_obj.create(
            self.cr, self.uid, {}, context={'active_ids': [inventory_id]})
        un_loc_obj.confirm_uninventoried_locations(
            self.cr, self.uid, wizard_id,
            context={'active_ids': [inventory_id]})
        missing_location = inventory_obj.get_missing_locations(
            self.cr, self.uid, [inventory_id])
        self.assertEqual(
            len(missing_location), 0, "No missing location should be find, "
            "because the inventory is confirmed")
        # confirm shelf 2 inventory
        inventory_id = self.ref(
            'stock_inventory_hierarchical_location.child_1_id')
        inventory_obj.action_open(
            self.cr, self.uid, [inventory_id])
        missing_location = inventory_obj.get_missing_locations(
            self.cr, self.uid, [inventory_id])
        self.assertEqual(
            len(missing_location), 1, "1 missing location should be fine, "
            "because the inventory is empty")
        self.registry('stock.inventory.line').create(
            self.cr, self.uid,
            {'product_id': self.ref('product.product_product_7'),
             'product_uom': self.ref('product.product_uom_unit'),
             'company_id': self.ref('base.main_company'),
             'inventory_id': inventory_id,
             'product_qty': 18.0,
             'location_id': self.ref('stock.stock_location_14')})
        missing_location = inventory_obj.get_missing_locations(
            self.cr, self.uid, [inventory_id])
        self.assertEqual(
            len(missing_location), 0, "No missing location should be find, "
            "because the inventory is filled")
        wizard_id = un_loc_obj.create(self.cr, self.uid, {},
                                      context={'active_ids': [inventory_id]})
        wizard = un_loc_obj.browse(self.cr, self.uid, wizard_id,
                                   context={'active_ids': [inventory_id]})
        self.assertEqual(len(wizard.location_ids), 0,
                         "The wizard should not contain any "
                         "lines but contains %s." % wizard.location_ids)
        un_loc_obj.confirm_uninventoried_locations(
            self.cr, self.uid, wizard_id,
            context={'active_ids': [inventory_id]})
        # confirm parent inventory
        missing_location = inventory_obj.get_missing_locations(
            self.cr, self.uid, [parent_inventory_id])
        self.assertEqual(
            len(missing_location), 1, "Only 1 missing location should be "
            "find, because there is some location in child inventory")

    def test_fill_inventory(self):
        """
        Test that when fill a parent inventory, the child location are not
        in the result
        """
        inventory_obj = self.registry('stock.inventory')
        fill_obj = self.registry('stock.fill.inventory')
        parent_inventory_id = self.ref(
            'stock_inventory_hierarchical_location.parent_inventory')
        inventory_obj.action_open(
            self.cr, self.uid, [parent_inventory_id])
        # confirm shelf 1 inventory
        inventory_id = self.ref(
            'stock_inventory_hierarchical_location.child_2_id')
        inventory_obj.action_open(
            self.cr, self.uid, [inventory_id])
        wizard_id = fill_obj.create(
            self.cr, self.uid,
            {'location_id': self.ref('stock.stock_location_components'),
             'recursive': True,
             'exhaustive': True,
             'set_stock_zero': True}, context={'active_ids': [inventory_id]})
        fill_obj.fill_inventory(self.cr, self.uid, [wizard_id],
                                context={'active_ids': [inventory_id]})
        inventory_line_ids = self.registry('stock.inventory.line').search(
            self.cr, self.uid, [('inventory_id', '=', inventory_id)])
        self.assertEqual(len(inventory_line_ids), 12,
                         "12 inventory line is fount after filling inventory")
        # confirm shelf 2 inventory
        inventory_id = self.ref(
            'stock_inventory_hierarchical_location.child_1_id')
        inventory_obj.action_open(
            self.cr, self.uid, [inventory_id])
        wizard_id = fill_obj.create(
            self.cr, self.uid,
            {'location_id': self.ref('stock.stock_location_14'),
             'recursive': True,
             'exhaustive': True,
             'set_stock_zero': True}, context={'active_ids': [inventory_id]})
        fill_obj.fill_inventory(self.cr, self.uid, [wizard_id],
                                context={'active_ids': [inventory_id]})
        inventory_line_ids = self.registry('stock.inventory.line').search(
            self.cr, self.uid, [('inventory_id', '=', inventory_id)])
        self.assertEqual(
            len(inventory_line_ids), 4,
            "1 inventory line is fount after filling inventory")
        # confirm parent inventory
        wizard_id = fill_obj.create(
            self.cr, self.uid,
            {'location_id': self.ref('stock.stock_location_stock'),
             'recursive': True,
             'exhaustive': True,
             'set_stock_zero': True},
            context={'active_ids': [parent_inventory_id]})
        try:
            fill_obj.fill_inventory(
                self.cr, self.uid, [wizard_id],
                context={'active_ids': [parent_inventory_id]})
        except Exception, e:
            self.assertEqual(
                e.value,
                'No product in this location. Please select a location in '
                'the product form.',
                "The message should be ''No product in this location. Please "
                "select a location in the product form.''")
            exception_happened = True
            pass
        self.assertTrue(exception_happened)
        inventory_line_ids = self.registry('stock.inventory.line').search(
            self.cr, self.uid, [('inventory_id', '=', parent_inventory_id)])
        self.assertEqual(len(inventory_line_ids), 0,
                         "No inventory line is fount after filling inventory")
