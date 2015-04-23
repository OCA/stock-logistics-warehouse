# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase


class TestPartnerLocations(TransactionCase):

    def setUp(self):
        super(TestPartnerLocations, self).setUp()

        self.partner_model = self.env['res.partner']
        self.location_model = self.env['stock.location']

        self.customer_a = self.partner_model.create({
            'name': 'Customer A',
            'customer': True,
            'supplier': False,
        })

        self.supplier_b = self.partner_model.create({
            'name': 'Supplier B',
            'customer': False,
            'supplier': True,
        })

        self.partner_c = self.partner_model.create({
            'name': 'Partner C',
            'customer': True,
            'supplier': True,
        })

    def _create_locations(self):
        self.locations = [
            self.location_model.create({
                'partner_id': record[0].id,
                'name': record[1],
                'usage': record[2],
            }) for record in [
                (self.customer_a, 'Location A-1', 'customer'),
                (self.customer_a, 'Location A-2', 'supplier'),
                (self.supplier_b, 'Location B-1', 'customer'),
                (self.supplier_b, 'Location B-2', 'supplier'),
                (self.supplier_b, 'Location B-3', 'supplier'),
            ]
        ]

        self.customer_a.refresh()
        self.supplier_b.refresh()

    def test_count_locations(self):
        self._create_locations()
        self.assertEqual(len(self.customer_a.location_ids), 3)
        self.assertEqual(len(self.supplier_b.location_ids), 4)
        self.assertEqual(len(self.partner_c.location_ids), 2)

    def check_partner_c(self):
        self.assertEqual(len(self.partner_c.location_ids), 2)

        location_c1 = self.partner_c.property_stock_customer
        location_c2 = self.partner_c.property_stock_supplier
        locations = self.partner_c.location_ids

        self.assertIn(location_c1, locations)
        self.assertEqual(location_c1.usage, 'customer')
        self.assertIn(location_c2, locations)
        self.assertEqual(location_c2.usage, 'supplier')

    def test_partner_create(self):
        self.assertEqual(len(self.customer_a.location_ids), 1)
        location_a = self.customer_a.location_ids[0]
        self.assertEqual(self.customer_a.location_ids[0].usage, 'customer')
        self.assertEqual(self.customer_a.property_stock_customer, location_a)
        self.assertEqual(len(self.customer_a.property_stock_supplier), 0)

        self.assertEqual(len(self.supplier_b.location_ids), 1)
        location_b = self.supplier_b.location_ids[0]
        self.assertEqual(location_b.usage, 'supplier')
        self.assertEqual(len(self.supplier_b.property_stock_customer), 0)
        self.assertEqual(self.supplier_b.property_stock_supplier, location_b)

        self.check_partner_c()

    def check_customer_a_supplier_location(self):
        location_a = self.customer_a.property_stock_supplier
        self.assertIn(location_a, self.customer_a.location_ids)
        self.assertEqual(location_a.usage, 'supplier')

    def check_supplier_b_customer_location(self):
        location_b = self.supplier_b.property_stock_customer
        self.assertIn(location_b, self.supplier_b.location_ids)
        self.assertEqual(location_b.usage, 'customer')

    def test_partner_write(self):
        """
        Test write method when partner does not already have the required
        location
        """
        self.customer_a.write({'supplier': True})
        self.supplier_b.write({'customer': True})

        self.assertEqual(len(self.customer_a.location_ids), 2)
        self.check_customer_a_supplier_location()

        self.assertEqual(len(self.supplier_b.location_ids), 2)
        self.check_supplier_b_customer_location()

    def test_partner_write_existing_location(self):
        """
        Test write method when partner already has the required location
        """
        self._create_locations()

        self.customer_a.write({'supplier': True})
        self.assertEqual(len(self.customer_a.location_ids), 3)
        self.check_customer_a_supplier_location()

        self.supplier_b.write({'customer': True})
        self.assertEqual(len(self.supplier_b.location_ids), 4)
        self.check_supplier_b_customer_location()

        self.partner_c.write({'supplier': True, 'customer': True})
        self.check_partner_c()
