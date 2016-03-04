# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase
from openerp.osv.orm import except_orm


class test_stock_location(TransactionCase):

    def setUp(self):
        super(test_stock_location, self).setUp()
        # Clean up registries
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        # Get registries
        self.user_model = self.registry("res.users")
        self.stock_location = self.registry("stock.location")
        self.stock_move = self.registry("stock.move")
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)
        self.vals_location = {
            'name': 'Location A',
        }

        self.location_id = self.stock_location.create(
            self.cr, self.uid, self.vals_location, context=self.context)

    def test_write_location_error(self):
        """Test write method in stock location model"""
        cr, uid, vals = self.cr, self.uid, self.vals_location
        context = self.context
        vals['active'] = False
        self.stock_location.create(
            self.cr, self.uid,
            {'name': 'Location B', 'location_id': self.location_id},
            context=self.context)
        self.assertRaises(
            except_orm,
            self.stock_location.write,
            cr, uid, self.location_id, vals, context=context
        )

    def test_onchange_active_field(self):
        """Test onchange_active_field method in stock location model"""
        cr, uid, context = self.cr, self.uid, self.context
        result = self.stock_location.onchange_active_field(
            cr, uid, self.location_id, active=True, context=context)
        self.assertEqual(result, {})


class test_stock_move(TransactionCase):

    def setUp(self):
        super(test_stock_move, self).setUp()
        # Clean up registries
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        # Get registries
        self.user_model = self.registry("res.users")
        self.stock_location = self.registry("stock.location")
        self.stock_move = self.registry("stock.move")
        self.product = self.registry("product.product")
        self.ir_model_data = self.registry('ir.model.data')
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)

        self.location_orig_id = self.stock_location.create(
            self.cr, self.uid, {'name': 'Location A'}, context=self.context)

        self.location_dest_id = self.stock_location.create(
            self.cr, self.uid, {'name': 'Location B'}, context=self.context)

        self.usb_adapter_id = self.ir_model_data.get_object_reference(
            self.cr, self.uid, 'product', 'product_product_48')[1]

        self.unit_id = self.ir_model_data.get_object_reference(
            self.cr, self.uid, 'product', 'product_uom_unit')[1]

        self.vals = {
            'name': 'a move',
            'product_id': self.usb_adapter_id,
            'product_qty': 1.0,
            'product_uom': self.unit_id,
            'location_id': self.location_orig_id,
            'location_dest_id': self.location_dest_id}

        self.move_id = self.stock_move.create(
            self.cr, self.uid, self.vals, context=self.context)

    def test_action_done(self):
        """Test action_done method in stock move model"""
        cr, uid, context = self.cr, self.uid, self.context
        self.stock_location.write(
            cr, uid, self.location_dest_id, {'active': False}, context=context)
        self.assertRaises(
            except_orm,
            self.stock_move.action_done,
            cr, uid, self.move_id, context=context
        )
