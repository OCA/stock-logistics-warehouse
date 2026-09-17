# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VerticalLiftSelectShuttle(models.TransientModel):
    _name = "vertical.lift.select.shuttle"
    _description = "Vertical Lift Shuttle Selector"

    location_id = fields.Many2one(
        "stock.location", string="Location", readonly=True, required=True
    )
    res_model = fields.Char(required=True, readonly=True)
    res_id = fields.Integer(required=True, readonly=True)
    method_name = fields.Char(required=True, readonly=True)
    allowed_shuttle_ids = fields.One2many(
        comodel_name="vertical.lift.shuttle",
        related="location_id.inverse_vertical_lift_shuttle_ids",
    )
    shuttle_id = fields.Many2one(
        comodel_name="vertical.lift.shuttle",
        string="Select Shuttle",
        required=True,
        domain="[('id', 'in', allowed_shuttle_ids)]",
        help="Select the specific shuttle to perform this operation.",
    )

    def action_confirm(self):
        self.ensure_one()
        # Retrieve the original record (stock.location or stock.move.line)
        record = self.env[self.res_model].browse(self.res_id)

        # We inject the selected shuttle into the context so the target method
        # and computed fields can retrieve it.
        return getattr(
            record.with_context(shuttle_id=self.shuttle_id.id), self.method_name
        )()
