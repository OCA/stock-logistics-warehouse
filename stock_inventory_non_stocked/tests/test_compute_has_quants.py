# Copyright 2024 Ivan Perez <iperez@coninpe.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestComputeHasQuants(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )

    def test_compute_has_quants(self):
        self.product_template.product_variant_id._compute_has_quants()
        self.assertFalse(self.product_template.product_variant_id.has_quants)
        self.env["stock.quant"].create(
            {
                "product_id": self.product_template.product_variant_id.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 1,
            }
        )
        self.product_template.product_variant_id._compute_has_quants()
        self.assertTrue(self.product_template.product_variant_id.has_quants)
        self.env["stock.quant"].search(
            [("product_id", "=", self.product_template.product_variant_id.id)]
        ).unlink()
        self.product_template.product_variant_id._compute_has_quants()
        self.assertFalse(self.product_template.product_variant_id.has_quants)
