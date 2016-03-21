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


class stock_inventory_location_test(common.TransactionCase):

    def setUp(self):
        super(stock_inventory_location_test, self).setUp()

    def test_update_parent_location(self):
        """
        Test the update of the parent of a location (no inventory in progress
        """
        self.registry('stock.location').write(
            self.cr, self.uid,
            self.ref('stock.stock_location_5'),
            {'location_id': self.ref('stock.stock_location_4')})
