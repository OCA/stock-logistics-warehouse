# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class Inventory(models.Model):
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
    location_done_count = fields.Integer(
        compute="_compute_location_count",
        string="Number of Done Sub-Locations",
    )

    def _compute_location_count(self):
        for inventory in self:
            inventory.location_count = len(inventory.sub_location_ids)
            inventory.location_done_count = len(
                inventory.sub_location_ids.filtered(lambda l: l.state == "done")
            )

    def action_start(self):
        res = super().action_start()
        existing_locations = self.sub_location_ids.location_id
        if self.location_ids:
            domain_loc = [
                ("id", "child_of", self.location_ids.ids),
                ("child_ids", "=", False),
            ]
        else:
            domain_loc = [
                ("company_id", "=", self.company_id.id),
                ("usage", "in", ["internal", "transit"]),
            ]
        sub_locations = self.env["stock.location"].search(domain_loc)
        if self.product_ids:
            quants = self.env["stock.quant"].search(
                [
                    ("location_id", "in", sub_locations.ids),
                    ("product_id", "in", self.product_ids.ids),
                ]
            )
            sub_locations = quants.location_id
        sub_locations = sub_locations - existing_locations
        for location in sub_locations:
            self.env["stock.inventory.location"].create(
                {
                    "inventory_id": self.id,
                    "location_id": location.id,
                    "state": "pending",
                }
            )
        return res

    def action_validate(self):
        self.ensure_one()
        if any(loc.state != "done" for loc in self.sub_location_ids):
            raise UserError(
                _(
                    "The following locations have not been inventoried yet:\n%s\n"
                    "You must finalize the corresponding sub-locations."
                )
                % "\n".join(
                    [
                        "- " + loc.display_name
                        for loc in self.sub_location_ids
                        if loc.state != "done"
                    ]
                )
            )
        return super().action_validate()

    def action_cancel_draft(self):
        """Called by native button 'Cancel Inventory'"""
        self.sub_location_ids.write({"state": "pending"})
        return super().action_cancel_draft()

    def action_open_inventory_locations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "name": _("Inventory Locations"),
            "res_model": "stock.inventory.location",
            "context": {
                "default_inventory_id": self.id,
            },
            "domain": [
                ("inventory_id", "=", self.id),
            ],
        }


class StockInventoryLocation(models.Model):
    _name = "stock.inventory.location"
    _description = "Stock Inventory Location"

    _rec_name = "location_id"

    _order = "inventory_id desc, id"

    inventory_id = fields.Many2one(
        comodel_name="stock.inventory",
        required=True,
        ondelete="cascade",
    )
    location_id = fields.Many2one(comodel_name="stock.location", required=True)
    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("started", "Started"),
            ("done", "Done"),
        ],
        default="pending",
        required=True,
    )

    _sql_constraints = [
        (
            "inventory_location_unique",
            "UNIQUE(inventory_id, location_id)",
            "Inventory location must be unique per inventory.",
        )
    ]

    def action_start(self):
        self.ensure_one()
        assert self.state == "pending"
        self.write({"state": "started"})
        lines = self.env["stock.inventory.line"].search(
            [
                ("inventory_id", "=", self.inventory_id.id),
                ("location_id", "=", self.location_id.id),
            ]
        )
        lines.action_refresh_quantity()
        # TODO refresh inventory line quantity and create missing inventory line

    def action_done(self):
        self.ensure_one()
        assert self.state == "started"
        self.write({"state": "done"})

    def action_open_inventory_lines(self):
        self.ensure_one()
        action = self.inventory_id.action_open_inventory_lines()
        action["context"]["default_location_id"] = self.location_id.id
        action["context"]["readonly_location_id"] = True
        action["domain"] = [
            ("inventory_id", "=", self.inventory_id.id),
            ("location_id", "=", self.location_id.id),
        ]
        return action
