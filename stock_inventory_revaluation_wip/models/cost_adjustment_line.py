# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class CostAdjustmentLine(models.Model):
    _inherit = "stock.cost.adjustment.line"

    def _get_impacted_mos(self):
        """
        List MOs where Product is used as raw material
        """
        res = super()._get_impacted_mos()
        Production = self.env["mrp.production"]
        products = self.product_id
        # List MOs with a Work Center using Product as a Cost Type
        productions2_domain = [
            ("state", "in", ["draft", "confirmed", "progress"]),
            ("workorder_ids.workcenter_id.analytic_product_id", "in", products.ids),
        ]
        productions2 = Production.search(productions2_domain)
        # List MOs with a Work Center using Product as a Cost Type Driver
        productions3_domain = [
            ("state", "in", ["draft", "confirmed", "progress"]),
            (
                "workorder_ids.workcenter_id.analytic_product_id"
                ".activity_cost_ids.product_id",
                "in",
                products.ids,
            ),
        ]
        productions3 = Production.search(productions3_domain)
        return res | productions2 | productions3

    def _get_impacted_boms(self):
        """
        List BOMs where Product is used as a raw material
        """
        res = super()._get_impacted_boms()
        BOM = self.env["mrp.bom"]
        products = self.product_id
        # List BOMs with a Workcenter using the Product as a Cost Type
        boms2_domain = [
            (
                "operation_ids.workcenter_id.analytic_product_id",
                "in",
                products.ids,
            ),
        ]
        boms2 = BOM.search(boms2_domain)
        # List BOMs with a Workcenter using the Product as a Cost Type Driver
        boms3_domain = [
            (
                "operation_ids.workcenter_id.analytic_product_id.activity_cost_ids",
                "in",
                products.ids,
            ),
        ]
        boms3 = BOM.search(boms3_domain)
        return res | boms2 | boms3

    def _create_impacted_bom_lines(self):
        details = super()._create_impacted_bom_lines()
        self and self.ensure_one()
        product = self.product_id
        level = self.level
        ops_lines = self._get_impacted_bom_operations(product)
        vals = []
        for ops_line in ops_lines:
            impacted_products = ops_line.bom_id.get_produced_items()
            for impacted_product in impacted_products:
                add_cost = self.difference_cost * (ops_line.time_cycle / 60.0)
                vals.append(
                    {
                        "cost_adjustment_id": self.id,
                        "operation_id": ops_line.id,
                        "bom_id": ops_line.bom_id.id,
                        "product_id": impacted_product.id,
                        "quantity": ops_line.time_cycle,
                        "cost_increase": add_cost,
                        "parent_product_id": product.id,
                        "level": level,
                    }
                )
        if vals:
            add_details = self.env["stock.cost.adjustment.detail"].create(vals)
            details |= add_details
        return details

    @api.model
    def _get_impacted_bom_operations(self, products):
        impacted_cost_types = self.env["product.product"].search(
            [
                ("is_cost_type", "=", True),
                ("activity_cost_ids.product_id", "in", products.ids),
            ]
        )
        cost_types = products | impacted_cost_types
        return self.env["mrp.routing.workcenter"].search(
            [("workcenter_id.analytic_product_id", "in", cost_types.ids)]
        )
