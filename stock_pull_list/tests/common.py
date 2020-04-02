# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo import fields

from datetime import timedelta as td


class TestPullListCommon(TransactionCase):

    def setUp(self):
        super().setUp()
        self.wh_obj = self.env["stock.warehouse"]
        self.move_obj = self.env["stock.move"]
        self.picking_obj = self.env["stock.picking"]
        self.wiz_obj = self.env["stock.pull.list.wizard"]

        self.company = self.env.ref("base.main_company")
        self.warehouse = self.env.ref("stock.warehouse0")
        self.customer_loc = self.env.ref("stock.stock_location_customers")

        self.warehouse_2 = self.wh_obj.create({
            "code": "WH-T",
            "name": "Warehouse Test",
        })
        self.product_a = self.env["product.product"].create({
            "name": "test product A",
            "default_code": "TEST-A",
            "type": "product",
        })

        route_vals = {
            "name": "WH2 -> WH",
        }
        self.transfer_route = self.env["stock.location.route"].create(
            route_vals)
        rule_vals = {
            "location_id": self.warehouse.lot_stock_id.id,
            "location_src_id": self.warehouse_2.lot_stock_id.id,
            "action": "pull_push",
            "warehouse_id": self.warehouse.id,
            "propagate_warehouse_id": self.warehouse_2.id,
            "picking_type_id": self.env.ref("stock.picking_type_internal").id,
            "name": "WH2->WH",
            "route_id": self.transfer_route.id,
            "delay": 1,
        }
        self.transfer_rule = self.env["stock.rule"].create(rule_vals)
        self.product_a.route_ids = [(6, 0, self.transfer_route.ids)]

        # Dates:
        self.today = fields.Datetime.today()
        self.yesterday = self.today - td(days=1)
        self.date_3 = self.today + td(days=3)

    def _generate_moves(self):
        self.create_picking_out_a(self.yesterday, 50)
        self.create_picking_out_a(self.date_3, 70)

    def create_picking_out_a(self, date_move, qty):
        picking = self.picking_obj.create({
            "picking_type_id": self.ref("stock.picking_type_out"),
            "location_id": self.warehouse.lot_stock_id.id,
            "location_dest_id": self.customer_loc.id,
            "move_lines": [
                (0, 0, {
                    "name": "Test move",
                    "product_id": self.product_a.id,
                    "date_expected": date_move,
                    "date": date_move,
                    "product_uom": self.product_a.uom_id.id,
                    "product_uom_qty": qty,
                    "location_id": self.warehouse.lot_stock_id.id,
                    "location_dest_id": self.customer_loc.id,
                })]
        })
        picking.action_confirm()
        return picking
