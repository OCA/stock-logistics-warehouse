# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta as td

from odoo.exceptions import UserError
from odoo.tests import Form

from .common import TestPullListCommon


class TestStockPullList(TestPullListCommon):
    def test_01_default_options(self):
        self._generate_moves()
        wiz = self.wiz_obj.create({})
        wiz.action_prepare()
        lines = wiz.line_ids.filtered(lambda line: line.product_id == self.product_a)
        self.assertEqual(len(lines), 2)
        line_1 = lines.filtered(lambda line: line.date == self.yesterday.date())
        self.assertEqual(line_1.raw_demand_qty, 50)
        self.assertEqual(line_1.needed_qty, 50)
        self.assertEqual(line_1.stock_rule_id, self.transfer_rule)

        line_2 = lines.filtered(lambda line: line.date == self.date_3.date())
        self.assertEqual(line_2.raw_demand_qty, 70)
        self.assertEqual(line_2.needed_qty, 70)

    def test_02_consolidate(self):
        self._generate_moves()
        wiz = self.wiz_obj.create({"consolidate_by_product": True})
        wiz.action_prepare()
        line = wiz.line_ids.filtered(lambda line: line.product_id == self.product_a)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.date, self.today.date())
        expected = 50 + 70
        self.assertEqual(line.raw_demand_qty, expected)
        self.assertEqual(line.needed_qty, expected)

    def test_03_no_needed_qty(self):
        """Tests that no line is created in the wizard if there's no
        quantity needed."""
        quantity = 120.00
        self._update_product_qty(self.product_a, quantity)
        self._generate_moves()
        wiz = self.wiz_obj.create({"consolidate_by_product": True})
        wiz.action_prepare()
        line = wiz.line_ids.filtered(lambda line: line.product_id == self.product_a)
        self.assertEqual(len(line), 0)

    def test_04_server_action(self):
        """Tests work of generate pull list server action
        first without allow_pull_list_server_action flag,
        after this check Raise of UserError when 2 different locations"""
        self._generate_moves()
        picking = self.picking_obj.search(
            [("location_id", "=", self.warehouse.lot_stock_id.id)]
        )
        self.assertRaises(UserError, picking.action_create_pull_list)
        picking.picking_type_id.update({"allow_pull_list_server_action": True})
        picking.action_create_pull_list()
        wizard = self.env["stock.pull.list.wizard"].search([])
        lines = wizard.line_ids.filtered(lambda line: line.product_id == self.product_a)
        self.assertEqual(len(lines), 2)
        line_1 = lines.filtered(lambda line: line.date == self.yesterday.date())
        self.assertEqual(line_1.raw_demand_qty, 50)
        self.assertEqual(line_1.needed_qty, 50)
        self.assertEqual(line_1.stock_rule_id, self.transfer_rule)
        picking[0].update({"location_id": self.customer_loc.id})
        self.assertRaises(UserError, picking.action_create_pull_list)

    def test_05_move_uom(self):
        """Demand is computed in the product UoM."""
        self.create_picking_out_a(
            self.yesterday, 2, self.env.ref("uom.product_uom_dozen")
        )
        wiz = self.wiz_obj.create({})
        wiz.action_prepare()
        line = wiz.line_ids.filtered(lambda line: line.product_id == self.product_a)
        self.assertEqual(line.raw_demand_qty, 24)
        self.assertEqual(line.needed_qty, 24)

    def test_06_procure_max_lines(self):
        """Each stock reference gets at most max_lines procurements."""
        for days in range(5):
            self.create_picking_out_a(self.today + td(days=days), 10)
        wiz = self.wiz_obj.create({})
        wiz.action_prepare()
        self.assertEqual(len(wiz.line_ids), 5)
        wiz.max_lines = 2
        res = wiz.action_procure()
        references = self.env["stock.reference"].search(res["domain"])
        self.assertEqual(
            sorted(sum(ref.move_ids.mapped("product_uom_qty")) for ref in references),
            [10, 20, 20],
        )
        moves = references.move_ids
        self.assertEqual(moves.rule_id, self.transfer_rule)
        self.assertEqual(sum(moves.mapped("product_uom_qty")), 50)

    def test_07_server_action_warehouse(self):
        """The wizard uses the warehouse of the transfers source location."""
        picking = self.picking_obj.create(
            {
                "picking_type_id": self.warehouse_2.out_type_id.id,
                "location_id": self.warehouse_2.lot_stock_id.id,
                "location_dest_id": self.customer_loc.id,
            }
        )
        picking.picking_type_id.allow_pull_list_server_action = True
        res = picking.action_create_pull_list()
        wizard = self.wiz_obj.browse(res["res_id"])
        self.assertEqual(wizard.location_id, self.warehouse_2.lot_stock_id)
        self.assertEqual(wizard.warehouse_id, self.warehouse_2)

    def test_08_warehouse_follows_location(self):
        """Warehouse and location of the wizard stay consistent."""
        with Form(self.wiz_obj) as wizard:
            wizard.location_id = self.warehouse_2.lot_stock_id
            self.assertEqual(wizard.warehouse_id, self.warehouse_2)
            wizard.warehouse_id = self.warehouse
            self.assertEqual(wizard.location_id, self.warehouse.lot_stock_id)
