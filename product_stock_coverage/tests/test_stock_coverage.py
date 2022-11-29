# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tools import float_compare


class TestModule(TransactionCase):
    def setUp(self):
        super(TestModule, self).setUp()

        # Get Registry
        self.PosOrder = self.env["pos.order"]
        self.AccountPayment = self.env["account.payment"]

        # Get Object
        self.pos_product = self.env.ref("product.product_product_25")
        self.pos_template = self.pos_product.product_tmpl_id
        self.pricelist = self.env.ref("product.list0")
        self.partner = self.env.ref("base.res_partner_12")

        # Create a new pos config and open it
        self.pos_config = self.env.ref("point_of_sale.pos_config_main").copy()
        self.pos_config.open_session_cb()

    # Test Section
    def test_compute_stock_coverage(self):
        self._create_order()
        self.pos_template._compute_stock_coverage()
        self.assertEquals(1.0, self.pos_template.range_sales)
        self.assertEqual(
            float_compare(0.0714, self.pos_template.daily_sales, precision_digits=2),
            0,
        )
        self.assertEquals(210.0, self.pos_template.stock_coverage)

    def _create_order(self):
        date = fields.Date.today() - timedelta(days=1)
        date_str = fields.Date.to_string(date)
        account = self.env.user.partner_id.property_account_receivable_id
        statement = self.pos_config.current_session_id.statement_ids[0]
        order_data = {
            "id": u"0006-001-0010",
            "to_invoice": True,
            "data": {
                "pricelist_id": self.pricelist.id,
                "user_id": 1,
                "name": "Order 0006-001-0010",
                "partner_id": self.partner.id,
                "amount_paid": 0.9,
                "pos_session_id": self.pos_config.current_session_id.id,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "product_id": self.pos_product.id,
                            "price_unit": 0.9,
                            "qty": 1,
                            "price_subtotal": 0.9,
                            "price_subtotal_incl": 0.9,
                        },
                    ]
                ],
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "journal_id": self.pos_config.journal_ids[0].id,
                            "amount": 0.9,
                            "name": fields.Datetime.now(),
                            "account_id": account.id,
                            "statement_id": statement.id,
                        },
                    ]
                ],
                "creation_date": date_str,
                "amount_tax": 0,
                "fiscal_position_id": False,
                "uid": u"00001-001-0001",
                "amount_return": 0,
                "sequence_number": 1,
                "amount_total": 0.9,
            },
        }

        result = self.PosOrder.create_from_ui([order_data])
        order = self.PosOrder.browse(result[0])
        return order
