# -*- coding: utf-8 -*-
# © 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from freezegun import freeze_time
from datetime import datetime
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


TIME = "2022-07-01 08:00:00"
PARTNER = "base.res_partner_11"


class Test(TransactionCase):
    def setUp(self):
        super(Test, self).setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.partner = self.env.ref(PARTNER)

    @freeze_time(TIME)
    def test_1_purchase(self):
        """"""
        po = self.env["purchase.order"].create(self.get_purchase_order_vals())
        self.get_confirmed_order()
        day = 23
        assert len(po.picking_ids) == 1
        self.make_backorder(po.picking_ids[0], TIME[:7], day)
        assert len(po.picking_ids) == 2
        assert po.picking_ids[0].state == "done"
        assert po.picking_ids[0].date_done[:10] == "%s-%s" % (TIME[:7], day)
        assert po.picking_ids[1].state == "assigned"
        date = "%s-%s" % (TIME[:7], day)
        wiz = self.env["reception.checkpoint.selection.wizard"].create(
            {
                "partner_id": self.partner.id,
                "date": "%s-%s" % (TIME[:7], day),
            }
        )
        moves = wiz._get_moves(wiz._get_purchases()[0])
        assert len(moves) == 2
        lines = wiz._get_checkpoint_lines(moves, date)
        assert len(lines) == 2
        l_prd7 = lines.filtered(
            lambda s: s.product_id == self.env.ref("product.product_product_7")
        )
        assert l_prd7.ordered_qty == 3.0
        assert l_prd7.diff_qty == 1.0
        assert l_prd7.received_qty == 2.0
        l_prd8 = lines.filtered(
            lambda s: s.product_id == self.env.ref("product.product_product_8")
        )
        assert l_prd8.ordered_qty == 7.0
        assert l_prd8.diff_qty == 1.0
        assert l_prd8.received_qty == 6.0

    @freeze_time(TIME)
    def test_2_purchases(self):
        """include received stock moves and the one should be received"""
        # create first purchase and receive a first picking
        vals1 = self.get_purchase_order_vals()
        del vals1["order_line"][0]
        po1 = self.env["purchase.order"].create(vals1)
        self.get_confirmed_order(po1)
        self.make_backorder(po1.picking_ids[0], TIME[:7], 23)
        # create second purchase without reception
        vals2 = self.get_purchase_order_vals()
        del vals2["order_line"][1]
        po2 = self.env["purchase.order"].create(vals2)
        self.get_confirmed_order(po2)
        # checkpoint result
        wiz = self.env["reception.checkpoint.selection.wizard"].create(
            {
                "partner_id": self.partner.id,
                "date": "%s-%s" % (TIME[:7], 23),
            }
        )
        moves = wiz._get_moves(wiz._get_purchases()[0])
        lines = wiz._get_checkpoint_lines(moves, "%s-%s" % (TIME[:7], 23))
        assert len(lines) == 2
        l_prd7 = lines.filtered(
            lambda s: s.product_id == self.env.ref("product.product_product_7")
        )
        assert l_prd7.ordered_qty == 3.0
        assert l_prd7.diff_qty == 3.0
        assert l_prd7.received_qty == 0
        l_prd8 = lines.filtered(
            lambda s: s.product_id == self.env.ref("product.product_product_8")
        )
        assert l_prd8.ordered_qty == 7.0
        assert l_prd8.diff_qty == 1.0
        assert l_prd8.received_qty == 6.0

    def make_backorder(self, picking, month, day, qty=1):
        date = "%s-%s 10:00:00" % (month, day)
        with freeze_time(datetime.strptime(date, DTF)):
            wiz = (
                self.env["stock.transfer_details"]
                .with_context(active_model=picking._name, active_ids=[picking.id])
                .create({"picking_id": picking.id})
            )
            for item in wiz.item_ids:
                item.quantity = item.quantity - qty
            wiz.do_detailed_transfer()

    @freeze_time(TIME)
    def get_confirmed_order(self, po=None):
        if not po:
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
            "partner_id": self.env.ref(PARTNER).id,
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
