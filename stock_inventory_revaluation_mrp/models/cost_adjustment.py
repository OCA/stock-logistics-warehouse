# Copyright 2021-2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class CostAdjustment(models.Model):
    _inherit = "stock.cost.adjustment"

    explode_subassemblies = fields.Boolean(
        help="Also adds subcomponents or components"
        " that may have a Proposed Cost set.",
    )

    def action_open_cost_adjustment_details(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Cost Adjustment Detail"),
            "res_model": "stock.cost.adjustment.detail",
            "context": {"search_default_group_by_product_id": 1},
            "domain": [("cost_adjustment_id", "=", self.id)],
            "view_id": self.env.ref(
                "stock_inventory_revaluation_mrp.cost_adjustment_detail_mrp_view_tree"
            ).id,
        }

    def _populate_adjustment_lines(self, products, level=1):
        # Enhances adding Adjustment Line
        # To compute the impact where used in BoM
        # The impacted Products will be recursively added too
        self.ensure_one()
        if self.explode_subassemblies and level == 1:
            subcomponents = products._get_bom_structure_products()
            products |= subcomponents.filtered("proposed_cost")
        lines = super()._populate_adjustment_lines(products)
        for line in lines:
            line.level = level
            details = line._create_impacted_bom_lines()
            line.bom_impact_ids = details
            if details:
                new_products = details.product_id
                self._populate_adjustment_lines(new_products, level=level + 1)
        return lines

    def action_post(self):
        res = super().action_post()

        # bom's that are impacted as a result of cost change
        adjustment_details = self.env["stock.cost.adjustment.detail"].search(
            [
                ("cost_adjustment_line_id.cost_adjustment_id", "=", self.id),
            ]
        )
        boms = adjustment_details.mapped('bom_id')
        boms.update_bom_version()

        #bom's that are input as changed
        for product in self.product_ids:
            if product.bom_ids and (product.bom_ids[0] not in boms):
                product.bom_ids[0].update_bom_version()

        return res
