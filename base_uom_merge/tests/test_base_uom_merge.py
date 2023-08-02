# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestMergeUOM(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestMergeUOM, cls).setUpClass()
        cls.product_model = cls.env["product.product"]
        cls.uom_uom_model = cls.env["uom.uom"]
        cls.uom_category_model = cls.env["uom.category"]
        cls.base_uom_merge_model = cls.env["base.uom.merge"]

    def test_uom_merge(self):
        # create uom category
        test_uom_categ = self.uom_category_model.create({"name": "Test UOM Category"})
        test_uom_categ_2 = self.uom_category_model.create(
            {"name": "Test UOM Category 2"}
        )
        test_categ2_uom = self.uom_uom_model.create(
            {"name": "Test Categ2 UOM", "category_id": test_uom_categ_2.id}
        )
        test_uom_1 = self.uom_uom_model.create(
            {"name": "Test UOM 1", "category_id": test_uom_categ.id}
        )
        test_uom_2 = self.uom_uom_model.create(
            {
                "name": "Test UOM 2",
                "category_id": test_uom_categ.id,
                "uom_type": "smaller",
                "ratio": 0.1,
            }
        )
        test_uom_3 = self.uom_uom_model.create(
            {
                "name": "Test UOM 3",
                "category_id": test_uom_categ.id,
                "uom_type": "bigger",
                "ratio": 2.5,
            }
        )
        uom_merge = self.base_uom_merge_model.with_context(
            active_ids=[test_uom_1.id, test_categ2_uom.id],
            active_model="uom.uom",
        ).create({})
        uom_merge.dst_uom_id = test_uom_1

        with self.assertRaises(UserError):
            uom_merge.action_merge()

        # create products
        self.product_model.create(
            {
                "name": "test product 1",
                "uom_id": test_uom_1.id,
                "uom_po_id": test_uom_1.id,
            }
        )
        product_2 = self.product_model.create(
            {
                "name": "test product 2",
                "uom_id": test_uom_2.id,
                "uom_po_id": test_uom_2.id,
            }
        )
        product_3 = self.product_model.create(
            {
                "name": "test product 3",
                "uom_id": test_uom_2.id,
                "uom_po_id": test_uom_3.id,
            }
        )

        # check uom count before merge
        self.assertEqual(len(test_uom_categ.uom_ids), 3)

        # merge uom_2 to uom_1
        uom_merge = self.base_uom_merge_model.with_context(
            active_ids=[test_uom_1.id, test_uom_2.id],
            active_model="uom.uom",
        ).create({})
        uom_merge.dst_uom_id = test_uom_1
        uom_merge.action_merge()

        # inavlidate cache to reload data
        test_uom_categ.invalidate_cache()

        # check uom count before merge
        self.assertEqual(len(test_uom_categ.uom_ids), 2)

        # check UOM updated in product
        self.assertEqual(product_2.uom_id, test_uom_1)
        self.assertEqual(product_3.uom_id, test_uom_1)
