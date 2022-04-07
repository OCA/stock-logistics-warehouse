# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo import models


class StockCycleCount(models.Model):
    _inherit = "stock.cycle.count"

    def _prepare_inventory_adjustment(self):
        if self.cycle_count_rule_id.rule_type == "abc":
            inv_abc_groups = self.env["stock.abc"].search([])
            all_done_cycle = self.search(
                [
                    ("cycle_count_rule_id", "=", self.cycle_count_rule_id.id),
                    ("state", "=", "done"),
                ]
            )
            done_int_adj = []
            for product in all_done_cycle.stock_adjustment_ids:
                done_int_adj.append(product.id)
            today = datetime.today()
            all_product_list = []
            for group in inv_abc_groups:
                product_list = []
                week = round(52 / group.count)
                days = week * 7
                weeks_ago = today + timedelta(days=-days)
                # get all the products of specific count rule's inv. adj
                # which is done and in weeks range.
                all_done_products = (
                    self.env["stock.inventory"]
                    .search(
                        [
                            ("id", "in", done_int_adj),
                            ("state", "=", "done"),
                            ("date", "<=", datetime.now()),
                            ("date", ">=", weeks_ago),
                        ]
                    )
                    .product_ids
                )
                for product in group.product_ids:
                    if self.cycle_count_rule_id.frequency == "weekly":
                        y = round(len(group.product_ids.ids) * group.count / 52)
                    if product not in all_done_products and len(product_list) < y:
                        if (
                            not self.company_id.count_all_products
                            and product.with_context(
                                location=self.location_id.id
                            ).qty_available
                            > 0
                        ):
                            product_list.append(product.id)
                        elif self.company_id.count_all_products:
                            product_list.append(product.id)
                    else:
                        continue
                all_product_list.extend(product_list)
            abc_data = {
                "name": "{}-{}".format(self.location_id.name, self.date_deadline),
                "cycle_count_id": self.id,
                "location_ids": [(4, self.location_id.id)],
                "exclude_sublocation": True,
                "product_ids": [(6, 0, all_product_list)],
            }
            return abc_data
        return super()._prepare_inventory_adjustment()

    def action_create_inventory_adjustment(self):
        res = super().action_create_inventory_adjustment()
        if self.cycle_count_rule_id.rule_type == "abc":
            draft_inventory = self.env["stock.inventory"].search(
                [("state", "=", "draft")]
            )
            for inv in draft_inventory:
                inv.action_start()
        return res
