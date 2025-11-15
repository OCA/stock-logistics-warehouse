from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = "stock.location"

    track_stage = fields.Boolean(
        string="Track location stage?",
        default=False,
        help="If enabled, the location stages will be tracked.",
    )
    stage_id = fields.Many2one("stock.location.stage", string="Stage")
    lot_id = fields.Many2one("stock.lot")
    product_id = fields.Many2one(related="lot_id.product_id", store=True)
    last_stage_id = fields.Many2one("stock.location.stage", string="Last stage")
    last_stage_validated = fields.Boolean(
        string="Is the last stage progress validated?"
    )

    def open_location_history(self):
        self.ensure_one()
        return {
            "name": _("Location History"),
            "type": "ir.actions.act_window",
            "res_model": "stock.location.history",
            "view_mode": "list,form",
            "domain": [("location_id", "=", self.id)],
            "context": {"default_location_id": self.id},
        }

    @api.constrains("stage_id")
    def check_stage_change(self):
        self.ensure_one()
        if self.stage_id and not any(
            g in self.env.user.groups_id for g in self.stage_id.change_group_ids
        ):
            raise ValidationError(_("You are not allowed to change the stage."))
        if (
            self.last_stage_id
            and self.last_stage_id.validation
            and not self.last_stage_validated
        ):
            raise ValidationError(_("Validation required"))
        if self.stage_id != self.last_stage_id and self.last_stage_id:
            if not self.validate_stage_route():
                raise ValidationError(_("Invalid stage change"))
            else:
                self.create_location_history(self.stage_id.name)
        self.last_stage_id = self.stage_id
        self.last_stage_validated = not self.stage_id.validation

    @api.constrains("location_history_ids")
    def check_last_history_change(self):
        last_history = self.env["stock.location.history"].search(
            [("location_id", "=", self.id)], order="create_date desc", limit=1
        )
        if not last_history:
            self.last_stage_validated = True
        else:
            if last_history.registry_type == "val":
                self.last_stage_validated = True

    def validate_stage_route(self):
        if not self.stage_id:
            return True
        destination_ids = self.last_stage_id.next_ids
        return self.stage_id in destination_ids

    def create_location_history(self, registry_type):
        history_vals = {
            "location_id": self.id,
            "lot_id": self.lot_id.id,
            "previous_stage_id": self.last_stage_id.id,
            "new_stage_id": self.stage_id.id,
            "registry_type": registry_type,
            "user_id": self.env.uid,
        }
        self.env["stock.location.history"].sudo().create(history_vals)

    def validate_stage(self):
        if not any(
            g in self.env.user.groups_id for g in self.stage_id.validation_group_ids
        ):
            raise ValidationError(_("You are not allowed to change the stage."))
        else:
            self.create_location_history("Validation")
            self.last_stage_validated = True
