# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    discrepancy_percent = fields.Float(
        string="Discrepancy percent (%)",
        compute="_compute_discrepancy",
        digits=(3, 2),
        help="The discrepancy expressed in percent with theoretical quantity "
        "as basis",
        group_operator="avg",
        store=True,
        compute_sudo=True,
    )
    discrepancy_threshold = fields.Float(
        string="Threshold (%)",
        digits=(3, 2),
        help="Maximum Discrepancy Rate Threshold",
        compute="_compute_discrepancy_threshold",
    )
    has_over_discrepancy = fields.Boolean(
        compute="_compute_has_over_discrepancy",
    )

    @api.depends("quantity", "inventory_quantity")
    def _compute_discrepancy(self):
        for quant in self:
            if not quant.quantity or not quant.inventory_quantity_set:
                quant.discrepancy_percent = 0
            else:
                quant.discrepancy_percent = abs(
                    100 * (quant.inventory_diff_quantity) / quant.quantity
                )

    def _compute_discrepancy_threshold(self):
        for quant in self:
            whs = quant.location_id.warehouse_id
            if quant.location_id.discrepancy_threshold > 0.0:
                quant.discrepancy_threshold = quant.location_id.discrepancy_threshold
            elif whs.discrepancy_threshold > 0.0:
                quant.discrepancy_threshold = whs.discrepancy_threshold
            else:
                quant.discrepancy_threshold = False

    def _compute_has_over_discrepancy(self):
        for rec in self:
            rec.has_over_discrepancy = (
                rec.discrepancy_percent > rec.discrepancy_threshold
            )

    def action_apply_inventory(self):
        if self.env.context.get("skip_exceeded_discrepancy", False):
            return super().action_apply_inventory()
        over_discrepancy = self.filtered(lambda r: r.has_over_discrepancy)
        if over_discrepancy:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "stock_inventory_discrepancy.confirm_discrepancy_action"
            )
            action["context"] = dict(
                self._context.copy(),
                discrepancy_quant_ids=over_discrepancy.ids,
                active_ids=self.ids,
            )
            return action
        return super().action_apply_inventory()
