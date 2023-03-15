# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockStorageCategoryCapacity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
            }
        )

    def test_storage_capacity_display_package(self):
        package_type = self.env["stock.package.type"].create(
            {
                "name": "Super Pallet",
            }
        )
        stor_category = self.env["stock.storage.category"].create(
            {
                "name": "Super Storage Category",
                "max_weight": 100,
            }
        )
        stor_capacity = self.env["stock.storage.category.capacity"].create(
            {
                "storage_category_id": stor_category.id,
                "package_type_id": package_type.id,
                "quantity": 1,
            }
        )

        self.assertEqual(
            stor_capacity.display_name,
            "Super Storage Category x 1.0 (Package: Super Pallet)",
        )

    def test_storage_capacity_display_product(self):
        stor_category = self.env["stock.storage.category"].create(
            {
                "name": "Super Storage Category",
                "max_weight": 100,
            }
        )
        stor_capacity = self.env["stock.storage.category.capacity"].create(
            {
                "storage_category_id": stor_category.id,
                "product_id": self.product.id,
                "quantity": 1,
            }
        )

        self.assertEqual(
            stor_capacity.display_name,
            "Super Storage Category x 1.0 (Product: Product Test)",
        )

    def test_storage_capacity_display_both(self):
        package_type = self.env["stock.package.type"].create(
            {
                "name": "Super Pallet",
            }
        )
        stor_category = self.env["stock.storage.category"].create(
            {
                "name": "Super Storage Category",
                "max_weight": 100,
            }
        )
        stor_capacity = self.env["stock.storage.category.capacity"].create(
            {
                "storage_category_id": stor_category.id,
                "product_id": self.product.id,
                "package_type_id": package_type.id,
                "quantity": 1,
            }
        )

        self.assertEqual(
            stor_capacity.display_name,
            "Super Storage Category x 1.0 (Product: Product Test - Package: Super Pallet)",
        )
