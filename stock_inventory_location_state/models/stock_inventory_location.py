# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


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
        if self.state not in ("pending", "started"):
            raise UserError(
                self.env._(
                    "Unable to start inventory of location %(name)s: it isn't pending.",
                    name=self.location_id.complete_name,
                )
            )

        self.write({"state": "started"})
        # TODO create missing inventory line

    def action_done(self):
        self.ensure_one()
        if self.state != "started":
            raise UserError(
                self.env._(
                    "Unable to validate inventory of location %(name)s: "
                    "it hasn't been started.",
                    name=self.location_id.complete_name,
                )
            )
        self.write({"state": "done"})

    def action_reopen(self):
        self.ensure_one()
        if self.inventory_id.state == "done":
            raise UserError(
                self.env._(
                    "Unable to re-open: inventory %(name)s has been validated.",
                    name=self.inventory_id.name,
                )
            )
        self.write({"state": "pending"})

    def action_view_inventory_adjustment(self):
        self.ensure_one()
        action = self.inventory_id.action_view_inventory_adjustment()
        action["context"]["default_location_id"] = self.location_id.id
        action["context"]["readonly_location_id"] = True
        action["domain"] = expression.AND(
            [
                action["domain"],
                [
                    ("location_id", "=", self.location_id.id),
                ],
            ]
        )
        return action
