# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class CostAdjustmentLine(models.Model):
    _inherit = "stock.cost.adjustment.line"

    def _populate_bom_impact_details(self, products, level=1):
        super()._populate_bom_impact_details(products, level=level)
        for product in products:
            # Impact from bOM operation/work center usage
            cost_details_add = self._create_impacted_bom_operations(product)
            # Iterate on the next layer of Products impacted by the BOMs added
            if cost_details_add:
                impacted_products = (
                    cost_details_add.product_id - self.bom_impact_ids.product_id
                )
                if impacted_products:
                    self._populate_bom_impact_details(
                        impacted_products - products, level=level + 1
                    )

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

    @api.model
    def _create_impacted_bom_operations(self, product):
        self and self.ensure_one()
        CostDetail = self.env["stock.cost.adjustment.detail"]  # bom_impact_ids
        cost_details = CostDetail
        ops_lines = self._get_impacted_bom_operations(product)
        for ops_line in ops_lines:
            impacted_products = ops_line.bom_id.get_produced_items()
            for impacted_product in impacted_products:
                # TODO: use create multi
                cost_details |= CostDetail.create(
                    {
                        "cost_adjustment_id": self.id,
                        "operation_id": ops_line.id,
                        "bom_id": ops_line.bom_id.id,
                        "product_id": impacted_product.id,
                        "quantity": ops_line.product_qty,
                        "additional_cost": self.difference_cost,
                        "parent_product_id": product.id,
                    }
                )
        return cost_details
