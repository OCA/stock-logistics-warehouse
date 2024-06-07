# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, fields, models
from odoo.exceptions import UserError


class ConfirmDiscrepancyWiz(models.TransientModel):
    _name = "confirm.discrepancy.wiz"
    _description = "Confim discrepancy wizard"

    def _default_discrepancy_quant_ids(self):
        return [
            Command.set(
                self.env["stock.quant"]
                .browse(self.env.context.get("discrepancy_quant_ids"))
                .ids
            )
        ]

    discrepancy_quant_ids = fields.Many2many(
        comodel_name="stock.quant",
        readonly=True,
        default=_default_discrepancy_quant_ids,
    )

    def button_apply(self):
        self.ensure_one()
        if not self.user_has_groups(
            "stock_inventory_discrepancy.group_stock_inventory_validation_always"
        ):
            raise UserError(
                _(
                    "You cannot apply inventory adjustments "
                    "if there are products that exceed the discrepancy threshold. "
                    "Only users with rights to apply them can proceed."
                )
            )
        self.env["stock.quant"].browse(self.env.context.get("active_ids")).with_context(
            skip_exceeded_discrepancy=True
        ).action_apply_inventory()
