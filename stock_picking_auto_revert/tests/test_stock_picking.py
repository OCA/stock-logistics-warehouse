# -*- coding: utf-8 -*-
# Copyright 2019 ForgeFlow
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
    def setUp(self):
        super(TestStockPicking, self).setUp()

    def test_return_and_recreate(self):

        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")
        so_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 5.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
        }
        so = self.env["sale.order"].create(so_vals)

        # confirm our standard so, check the picking
        so.action_confirm()

        # deliver completely
        picking = so.picking_ids

        picking.action_confirm()
        picking.do_transfer()
        picking.action_revert_recreate()

        # we have the original shipment and the return and the duplicated
        self.assertEqual(len(so.picking_ids), 3)

        # All pickings same quantity
        self.assertEqual(
            so.mapped("picking_ids.move_lines.product_uom_qty"),
            [5.0, 5.0, 5.0],
        )

        # check return destination location
        self.assertEqual(
            so.picking_ids[1].mapped("move_lines.location_dest_id.name"),
            ["Stock"],
        )

        # check duplicate destination location
        self.assertEqual(
            so.picking_ids[0].mapped("move_lines.location_dest_id.name"),
            ["Customers"],
        )
        self.assertEqual(so.picking_ids[0].state, "assigned")
