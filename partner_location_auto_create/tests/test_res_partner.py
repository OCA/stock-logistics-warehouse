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

        self.partner_model = self.env["res.partner"]
        self.location_model = self.env["stock.location"]
        self.company_model = self.env["res.company"]

        self.company_2 = self.company_model.create({"name": "Test Company"})

        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")

        self.customer_location_2 = self.location_model.create(
            {
                "usage": "customer",
                "name": "Default Customer Location 2",
                "company_id": self.company_2.id,
            }
        )

        self.supplier_location_2 = self.location_model.create(
            {
                "usage": "supplier",
                "name": "Default Supplier Location 2",
                "company_id": self.company_2.id,
            }
        )

        self.company_2.write(
            {
                "default_customer_location": self.customer_location_2.id,
                "default_supplier_location": self.supplier_location_2.id,
            }
        )

        self.customer_a = self.partner_model.create(
            {
                "name": "Customer A",
                "customer": True,
                "supplier": False,
                "is_company": True,
                "company_id": self.company_2.id,
            }
        )

        self.supplier_b = self.partner_model.create(
            {
                "name": "Supplier B",
                "customer": False,
                "supplier": True,
                "is_company": True,
                "company_id": self.company_2.id,
            }
        )

        self.partner_c = self.partner_model.create(
            {
                "name": "Partner C",
                "customer": True,
                "supplier": True,
                "is_company": True,
            }
        )

    def _create_locations(self):
        self.locations = [
            self.location_model.create(
                {
                    "partner_id": record[0].id,
                    "name": record[1],
                    "usage": record[2],
                    "company_id": record[0].company_id.id,
                }
            )
            for record in [
                (self.customer_a, "Location A-1", "customer"),
                (self.customer_a, "Location A-2", "supplier"),
                (self.supplier_b, "Location B-1", "customer"),
                (self.supplier_b, "Location B-2", "supplier"),
                (self.supplier_b, "Location B-3", "supplier"),
            ]
        ]

        self.customer_a.refresh()
        self.supplier_b.refresh()

    def test_partner_inactive(self):
        self._create_locations()

        self.assertEqual(len(self.customer_a.location_ids), 3)

        self.customer_a.write({"active": False})
        self.customer_a.refresh()
        self.assertEqual(len(self.customer_a.location_ids), 0)

        for location in self.customer_a.location_ids:
            self.assertFalse(location.active)

    def test_partner_change_name(self):
        # Test with customer A
        self.assertEqual(self.customer_a.property_stock_customer.name, "Customer A")

        self.customer_a.property_stock_customer.write(
            {"name": "Location A-1",}
        )

        self.customer_a.write({"name": "Customer AA"})

        self.customer_a.refresh()
        self.assertEqual(self.customer_a.property_stock_customer.name, "Location A-1")

        # Test with partner C
        self.assertEqual(self.partner_c.property_stock_customer.name, "Partner C")

        self.partner_c.write({"name": "Partner CC"})
        self.partner_c.refresh()
        self.assertEqual(self.partner_c.property_stock_customer.name, "Partner CC")

        self.assertEqual(self.partner_c.property_stock_supplier.name, "Partner CC")

    def test_partner_location_parent(self):
        self.assertEqual(
            self.customer_a.property_stock_customer.location_id,
            self.customer_location_2,
        )

        self.assertEqual(
            self.supplier_b.property_stock_supplier.location_id,
            self.supplier_location_2,
        )

        self.assertEqual(
            self.partner_c.property_stock_customer.location_id, self.customer_location
        )

        self.assertEqual(
            self.partner_c.property_stock_supplier.location_id, self.supplier_location
        )

    def test_partner_not_company(self):
        """
        Partners that are not companies must not generate locations
        """
        self.partner_d = self.partner_model.create(
            {
                "name": "Partner D",
                "customer": True,
                "supplier": True,
                "is_company": False,
                "company_id": self.company_2.id,
            }
        )

        self.assertEqual(len(self.partner_d.location_ids), 0)

        # If the partner becomes a company, the locations must
        # be created
        self.partner_d.write({"is_company": True})
        self.partner_d.refresh()
        self.assertEqual(len(self.partner_d.location_ids), 2)

    def test_location_parent(self):
        self.assertEqual(len(self.partner_c.location_ids), 2)
        for location in self.partner_c.location_ids:
            self.assertEqual(location.location_id.usage, location.usage)

    def test_count_locations(self):
        self._create_locations()
        self.assertEqual(len(self.customer_a.location_ids), 3)
        self.assertEqual(len(self.supplier_b.location_ids), 4)
        self.assertEqual(len(self.partner_c.location_ids), 2)

    def test_multi_company(self):
        self._create_locations()

        self.assertEqual(len(self.customer_a.location_ids), 3)
        for location in self.customer_a.location_ids:
            self.assertEqual(location.company_id, self.company_2)

    def check_partner_c(self):
        self.assertEqual(len(self.partner_c.location_ids), 2)

        location_c1 = self.partner_c.property_stock_customer
        location_c2 = self.partner_c.property_stock_supplier
        locations = self.partner_c.location_ids

        self.assertIn(location_c1, locations)
        self.assertEqual(location_c1.usage, "customer")
        self.assertIn(location_c2, locations)
        self.assertEqual(location_c2.usage, "supplier")

    def test_partner_create(self):
        self.assertEqual(len(self.customer_a.location_ids), 1)
        location_a = self.customer_a.location_ids[0]
        self.assertEqual(self.customer_a.location_ids[0].usage, "customer")
        self.assertEqual(self.customer_a.property_stock_customer, location_a)

        self.assertEqual(len(self.supplier_b.location_ids), 1)
        location_b = self.supplier_b.location_ids[0]
        self.assertEqual(location_b.usage, "supplier")
        self.assertEqual(self.supplier_b.property_stock_supplier, location_b)

        self.check_partner_c()

    def check_customer_a_supplier_location(self):
        location_a = self.customer_a.property_stock_supplier
        self.assertIn(location_a, self.customer_a.location_ids)
        self.assertEqual(location_a.usage, "supplier")

    def check_supplier_b_customer_location(self):
        location_b = self.supplier_b.property_stock_customer
        self.assertIn(location_b, self.supplier_b.location_ids)
        self.assertEqual(location_b.usage, "customer")

    def test_partner_write(self):
        """
        Test write method when partner does not already have the required
        location
        """
        self.customer_a.write({"supplier": True})
        self.supplier_b.write({"customer": True})

        self.assertEqual(len(self.customer_a.location_ids), 2)
        self.check_customer_a_supplier_location()

        self.assertEqual(len(self.supplier_b.location_ids), 2)
        self.check_supplier_b_customer_location()

    def test_partner_write_existing_location(self):
        """
        Test write method when partner already has the required location
        """
        self._create_locations()

        self.customer_a.write({"supplier": True})
        self.customer_a.refresh()
        self.assertEqual(len(self.customer_a.location_ids), 4)
        self.check_customer_a_supplier_location()

        self.supplier_b.write({"customer": True})
        self.supplier_b.refresh()
        self.assertEqual(len(self.supplier_b.location_ids), 5)
        self.check_supplier_b_customer_location()

        self.partner_c.write({"supplier": True, "customer": True})
        self.check_partner_c()

    def test_partner_write_is_company_false(self):
        """
        Test that locations related to a partner are unlinked
        when a is_company is set to False
        """
        self._create_locations()

        self.assertEqual(len(self.customer_a.location_ids), 3)
        self.customer_a.write(
            {"supplier": True, "is_company": False,}
        )
        self.customer_a.refresh()
        self.assertEqual(len(self.customer_a.location_ids), 0)
