# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PushedFlow(models.Model):
    _inherit = "stock.location.path"

    auto_create_group = fields.Boolean(string="Auto-create Procurement Group")

    def _prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super(PushedFlow, self)._prepare_move_copy_values(
            move_to_copy, new_date
        )
        if self.auto_create_group:
            group_data = self._prepare_auto_procurement_group_data()
            group = self.env["procurement.group"].create(group_data)
            new_move_vals["group_id"] = group.id
        return new_move_vals

    @api.model
    def _prepare_auto_procurement_group_data(self):
        name = self.env["ir.sequence"].next_by_code("procurement.group") or False
        if not name:
            raise UserError(_("No sequence defined for procurement group"))
        return {"name": name}
