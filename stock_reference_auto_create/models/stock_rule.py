# Copyright 2017-2020 ForgeFlow, S.L.
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = "stock.rule"

    auto_create_reference = fields.Boolean(string="Auto-create Reference")

    @api.model
    def _get_rule(self, product_id, location_id, values):
        rule = super()._get_rule(product_id, location_id, values)
        if rule and rule.auto_create_reference and values.get("date_planned"):
            values["reference_ids"] = rule._get_auto_reference(product_id)
        return rule

    def _get_auto_reference(self, product):
        return self.env["stock.reference"].create(
            self._prepare_auto_reference_data(product)
        )

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        if self.auto_create_reference:
            reference = self._get_auto_reference(move_to_copy.product_id)
            new_move_vals["reference_ids"] = [Command.set(reference.ids)]
        return new_move_vals

    def _prepare_auto_reference_data(self, product):
        name = self.env["ir.sequence"].next_by_code("stock.reference.auto")
        if not name:
            raise UserError(
                self.env._("No sequence defined for auto-created references.")
            )
        return {"name": name}
