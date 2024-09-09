# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestExcludeLocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestExcludeLocation, cls).setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)]
        )
        cls.location_1 = cls.env["stock.location"].create(
            {
                "company_id": cls.company.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "name": "Location 1",
            }
        )
        cls.location_2 = cls.env["stock.location"].create(
            {
                "company_id": cls.company.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "name": "Location 2",
            }
        )
        cls.sub_location_1 = cls.env["stock.location"].create(
            {
                "company_id": cls.company.id,
                "location_id": cls.location_1.id,
                "name": "Sub Location 1",
            }
        )
        cls.sub_location_2 = cls.env["stock.location"].create(
            {
                "company_id": cls.company.id,
                "location_id": cls.location_2.id,
                "name": "Sub Location 2",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
            }
        )

    def _add_stock_to_product(self, product, location, qty):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param location: stock.location recordset
        :param qty: float
        """
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "inventory_quantity": qty,
            }
        )

    def test_exclude_location(self):
        # Add stock for the product and query product stock availability normally.
        self.company.stock_excluded_location_ids = False
        self._add_stock_to_product(self.product, self.location_1, 50.0)
        self._add_stock_to_product(self.product, self.sub_location_1, 20.0)
        self._add_stock_to_product(self.product, self.location_2, 20.0)
        self._add_stock_to_product(self.product, self.sub_location_2, 10.0)
        self.assertEqual(self.product.qty_available, 100)

        # Add location_2 as an excluded location in the company, so location_2
        # and his child sub_location_2 are excluded from product availability.
        self.company.stock_excluded_location_ids = self.location_2
        self.product._compute_excluded_location_ids()
        self.product._compute_quantities()
        self.assertEqual(self.product.qty_available, 70)
