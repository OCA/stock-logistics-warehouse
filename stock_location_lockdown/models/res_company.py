# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    allow_lockdown_on_stocked_location = fields.Boolean(
        string="Allow Inbound Lockdown on Stocked Locations",
        help="When enabled, an internal location can be marked as "
        "'Block Stock Entrance' even if it already contains stock.",
    )
    block_location_on_inventory = fields.Boolean(
        string="Block Location on Inventory",
        help="When enabled, a location (and its descendants) is treated as "
        "blocked for both inbound and outbound while an inventory is "
        "in progress on it.",
    )

    def _refresh_inventory_blocked(self, company_ids):
        locations = (
            self.env["stock.location"]
            .sudo()
            .search([("company_id", "in", company_ids)])
        )
        if locations:
            locations._compute_is_inventory_blocked()

    def write(self, vals):
        refresh_inventory = "block_location_on_inventory" in vals
        res = super().write(vals)
        if refresh_inventory:
            self._refresh_inventory_blocked(self.ids + [False])
        return res
