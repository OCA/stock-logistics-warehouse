# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class Inventory(models.Model):
    _inherit = "stock.inventory"

    sub_location_ids = fields.One2many(
        comodel_name="stock.inventory.location",
        inverse_name="inventory_id",
        string="Sub locations",
    )
    location_count = fields.Integer(
        compute="_compute_location_count", string="Location count"
    )
    remaining_location_count = fields.Integer(
        compute="_compute_location_count", string="Remaining location count"
    )

    def _compute_location_count(self):
        for inventory in self:
            inventory.location_count = len(inventory.sub_location_ids)
            inventory.remaining_location_count = len(
                inventory.sub_location_ids.filtered(lambda l: l.state != "done")
            )

    def action_start(self):
        res = super().action_start()
        existing_locations = self.sub_location_ids.mapped("location_id")
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
            sub_locations = quants.mapped("location_id")
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
                _("Not all location have been inventoried, please finalize.")
            )
        return super().action_validate()

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

    _order = "state desc"

    inventory_id = fields.Many2one(
        comodel_name="stock.inventory",
        string="Inventory",
        required=True,
        ondelete="cascade",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location", required=True
    )
    state = fields.Selection(
        selection=[("pending", "Pending"), ("started", "Started"), ("done", "Done")],
        string="State",
        default="pending",
        required=True,
    )

    _sql_constraints = [
        (
            "inventory_location_unique",
            "UNIQUE(inventory_id, location_id)",
            "Location must be unique per inventory.",
        )
    ]

    def action_start(self):
        self.ensure_one()
        self.state = "started"
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
        self.state = "done"
