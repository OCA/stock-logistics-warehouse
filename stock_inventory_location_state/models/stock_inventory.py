# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    sub_location_ids = fields.One2many(
        comodel_name="stock.inventory.location",
        inverse_name="inventory_id",
        string="Sub-Locations",
    )
    location_count = fields.Integer(
        compute="_compute_location_count",
        string="Number of Sub-Locations",
    )
    done_location_count = fields.Integer(
        compute="_compute_location_count",
        string="Number of Done Sub-Locations",
    )
    remaining_location_count = fields.Integer(
        compute="_compute_location_count",
        string="Number of Remaining Sub-Locations",
    )

    def _compute_location_count(self):
        for inventory in self:
            inventory.location_count = len(inventory.sub_location_ids)
            inventory.done_location_count = len(
                inventory.sub_location_ids.filtered(lambda line: line.state == "done")
            )
            inventory.remaining_location_count = (
                inventory.location_count - inventory.done_location_count
            )

    def action_state_to_in_progress(self):
        res = super().action_state_to_in_progress()
        existing_locations = self.sub_location_ids.location_id
        domain_loc = self._get_base_domain(self.location_ids)
        locations = self.env["stock.location"].search(domain_loc)
        # Retrieve locations from quants too to not forget any
        quants = self._get_quants(self.location_ids)
        locations |= quants.location_id
        locations -= existing_locations
        inv_locations_vals = [
            {
                "inventory_id": self.id,
                "location_id": location.id,
                "state": "pending",
            }
            for location in locations
        ]
        self.env["stock.inventory.location"].create(inv_locations_vals)
        return res

    def action_state_to_done(self):
        self.ensure_one()
        if any(loc.state != "done" for loc in self.sub_location_ids):
            locations_str = "\n".join(
                [
                    "- " + loc.display_name
                    for loc in self.sub_location_ids
                    if loc.state != "done"
                ]
            )
            raise UserError(
                self.env._(
                    "The following locations have not been inventoried yet:"
                    "\n%(locations)s\n"
                    "You must finalize the corresponding sub-locations.",
                    locations=locations_str,
                )
            )
        return super().action_state_to_done()

    def action_state_to_draft(self):
        self.sub_location_ids.write({"state": "pending"})
        return super().action_state_to_draft()

    def action_open_inventory_locations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "list",
            "name": self.env._("Inventory Locations"),
            "res_model": "stock.inventory.location",
            "context": {
                "default_inventory_id": self.id,
            },
            "domain": [
                ("inventory_id", "=", self.id),
            ],
        }
