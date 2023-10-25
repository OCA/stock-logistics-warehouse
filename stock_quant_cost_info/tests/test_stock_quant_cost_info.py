# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockQuantCostInfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        product_obj = cls.env["product.product"]
        cls.product_1 = product_obj.create(
            {"name": "product test 1", "type": "product", "standard_price": 1000}
        )
        cls.product_2 = product_obj.create(
            {"name": "product test 2", "type": "product", "standard_price": 2000}
        )

    def test_compute_adjustment_cost(self):
        """Tests if the adjustment_cost is correctly computed."""
        quant_prod_1 = self.env["stock.quant"].create(
            {
                "product_id": self.product_1.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "inventory_quantity": 10.0,
            }
        )
        self.assertEqual(quant_prod_1.adjustment_cost, 10000)
        quant_prod_2 = self.env["stock.quant"].create(
            {
                "product_id": self.product_2.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "inventory_quantity": 20.0,
            }
        )
        self.assertEqual(quant_prod_2.adjustment_cost, 40000)
