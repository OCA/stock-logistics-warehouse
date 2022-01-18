# -*- coding: utf-8 -*-
# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from freezegun import freeze_time
from datetime import datetime
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


TIME = "2022-07-01 08:00:00"


class Test(TransactionCase):
    @freeze_time(TIME)
    def setUp(self):
        super(Test, self).setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.order = self.env["purchase.order"].create(self.get_purchase_order_vals())

    @freeze_time(TIME)
    def test_one(self):
        """"""
        po = self.get_confirmed_order()
        day = 23
        assert len(po.picking_ids) == 1
        self.make_backorder(po.picking_ids[0], month=TIME[:7], day=day)
        assert len(po.picking_ids) == 2
        assert po.picking_ids[0].state == "done"
        assert po.picking_ids[0].date_done[:10] == "%s-%s" % (TIME[:7], day)
        assert po.picking_ids[1].state == "assigned"
        wiz = self.env["reception.checkpoint.selection.wizard"].create(
            {
                "partner_id": self.env.ref("base.res_partner_12").id,
                "date": "%s-%s" % (TIME[:7], day),
            }
        )
        purchases, name = wiz._get_purchases()
        moves = wiz._get_moves(purchases)
        assert len(moves) == 2
        assert moves[0].timing == "inlate"
        assert moves[0].diff_qty == "1.0"

    def make_backorder(self, picking, month, day):
        date = "%s-%s 10:00:00" % (month, day)
        with freeze_time(datetime.strptime(date, DTF)):
            wiz = (
                self.env["stock.transfer_details"]
                .with_context(active_model=picking._name, active_ids=[picking.id])
                .create({"picking_id": picking.id})
            )
            for item in wiz.item_ids:
                item.quantity = item.quantity - 1
            wiz.do_detailed_transfer()

    @freeze_time(TIME)
    def get_confirmed_order(self):
        po = self.order
        po.name = "%s%s" % (po.name, po.id)
        po.signal_workflow("purchase_confirm")
        return po

    @freeze_time(TIME)
    def get_purchase_order_vals(self):
        def ref(id_string):
            return self.env.ref(id_string).id

        return {
            "name": "Test",
            "pricelist_id": ref("product.list0"),
            "location_id": ref("stock.stock_location_stock"),
            "partner_id": ref("base.res_partner_12"),
            "validator": ref("base.user_demo"),
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": "any",
                        "product_id": ref("product.product_product_7"),
                        "product_qty": 3,
                        "product_uom": ref("product.product_uom_unit"),
                        "price_unit": 400.00,
                        "date_planned": "%s-21" % TIME[:7],
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "any",
                        "product_id": ref("product.product_product_8"),
                        "product_qty": 7,
                        "product_uom": ref("product.product_uom_unit"),
                        "price_unit": 300.00,
                        "date_planned": "%s-21" % TIME[:7],
                    },
                ),
            ],
        }
