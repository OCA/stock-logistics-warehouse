# Copyright 2020-24 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_create_pull_list(self):
        source_location = next(iter(self)).location_id
        for record in self:
            if source_location != record.location_id:
                raise UserError(
                    self.env._("Choose transfers with same source location")
                )
            if not record.picking_type_id.allow_pull_list_server_action:
                raise UserError(
                    self.env._(
                        "Operation type of %(name)s transfer does not allow "
                        "pull list server action.",
                        name=record.name,
                    )
                )
        pull_wizard = self.env["stock.pull.list.wizard"].create(
            {"location_id": source_location.id}
        )
        res = pull_wizard.action_prepare()
        return res
