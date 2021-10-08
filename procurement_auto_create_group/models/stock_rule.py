# Copyright 2017-2020 ForgeFlow, S.L.
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = "stock.rule"

    auto_create_group = fields.Boolean(string="Auto-create Procurement Group")

    @api.onchange("group_propagation_option")
    def _onchange_group_propagation_option(self):
        if self.group_propagation_option != "propagate":
            self.auto_create_group = False

    def _prepare_auto_procurement_group_data(self):
        name = self.env["ir.sequence"].next_by_code("procurement.group") or False
        if not name:
            raise UserError(_("No sequence defined for procurement group."))
        return {
            "name": name,
            "partner_id": self.partner_address_id.id,
        }
