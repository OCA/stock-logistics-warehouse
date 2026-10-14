# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    condition_id = fields.Many2one(
        comodel_name="stock.lot.condition", string="Condition"
    )
    condition_required_note = fields.Boolean(compute="_compute_condition_required_note")
    condition_note = fields.Text()

    @api.depends("condition_id")
    def _compute_condition_required_note(self):
        for item in self:
            item.condition_required_note = (
                item.condition_id.required_note if item.condition_id else False
            )
