# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from psycopg2.errors import IntegrityError

from odoo.addons.base.tests.common import BaseCommon


class TestPackageCategory(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_obj = cls.env["stock.package.type.category"]

    def test_category_unique(self):
        """
        Categories with same code should not exist.
        """
        with self.assertRaises(IntegrityError):
            self.category_obj.create(
                {
                    "name": "Desk 2",
                    "code": "DESK",
                }
            )

    def test_category_search(self):
        self.categ = self.category_obj.create(
            {
                "name": "Test Category",
                "code": "TEST",
            }
        )
        package_type = self.env["stock.package.type"].create(
            {
                "name": "Little Box",
                "category_id": self.categ.id,
            }
        )

        self.assertEqual("Little Box (TEST)", package_type.display_name)

        package_search = self.env["stock.package.type"].name_search("TEST")

        self.assertEqual([(package_type.id, package_type.name)], package_search)
