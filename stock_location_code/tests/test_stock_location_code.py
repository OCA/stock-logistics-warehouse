# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestStockLocationCode(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_with_code = cls.env["stock.location"].create(
            {"name": "Shelf A", "usage": "internal", "code": "SHA"}
        )
        cls.location_no_code = cls.env["stock.location"].create(
            {"name": "Shelf B", "usage": "internal"}
        )

    def test_display_name_with_code(self):
        self.assertIn("[SHA]", self.location_with_code.display_name)
        self.assertIn("Shelf A", self.location_with_code.display_name)
        self.assertTrue(self.location_with_code.display_name.startswith("[SHA]"))

    def test_display_name_without_code(self):
        self.assertNotIn("[", self.location_no_code.display_name)
        self.assertIn("Shelf B", self.location_no_code.display_name)

    def test_name_search_by_code(self):
        results = self.env["stock.location"].name_search("SHA")
        result_ids = [r[0] for r in results]
        self.assertIn(self.location_with_code.id, result_ids)

    def test_code_not_copied_on_duplicate(self):
        copy = self.location_with_code.copy()
        self.assertFalse(copy.code)
