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
    last_stage_id = fields.Many2one("stock.location.stage", string="Last stage")
    location_history_ids = fields.One2many(
        "stock.location.history", "location_id", string="Location History"
    )
    last_stage_validated = fields.Boolean(
        string="Is the last stage progress validated?"
    )

    @api.constrains("stage_id")
    def check_stage_change(self):
        self.ensure_one()
        if self.stage_id and not any(
            g in self.env.user.groups_id for g in self.stage_id.change_group_ids
        ):
            raise ValidationError(_("Stage change not allowed for your user"))
        if (
            self.past_stage_id
            and self.past_stage_id.validation
            and not self.last_stage_validated
        ):
            raise ValidationError(_("Validation required"))
        if self.stage_id != self.past_stage_id and self.past_stage_id:
            if not self.validate_stage_route():
                raise ValidationError(_("Invalid stage change"))
            else:
                if self.stage_id.is_first:
                    self.create_location_history("free")
                elif self.stage_id.is_final:
                    self.create_location_history("maint")
                elif self.stage_id.is_pause:
                    self.create_location_history("paused")
                elif self.stage_id.is_use:
                    if not self.verifyBDSource():
                        raise ValidationError(_("Database not found"))
                    else:
                        self.with_delay().PLC_Complete()
                    self.create_location_history("prog")
                elif (
                    self.past_stage_id.is_first
                    and not self.macrolot_product_id
                    and self.stage_id
                ):
                    raise ValidationError(_("Product required"))
                elif self.past_stage_id.is_first and self.macrolot_product_id:
                    self.create_new_macrolot()
                    self.create_location_history("prog")
                elif self.past_stage_id.is_pause:
                    self.create_location_history("reg")
                else:
                    self.create_location_history("prog")
        elif not self.past_stage_id and self.stage_id:
            self.create_location_history("free")
        self.past_stage_id = self.stage_id
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
        destination_ids = self.last_stage_id.allowed_destination_location_ids
        return self.stage_id in destination_ids

    def create_location_history(self, registry_type):
        history_vals = {
            "location_id": self.id,
            "previous_stage_id": self.past_stage_id.id,
            "next_stage_id": self.stage_id.id,
            "registry_type": registry_type,
            "user_id": self.env.uid,
        }
        if self.actual_macrolot_id:
            history_vals["macrolot_id"] = self.actual_macrolot_id.id

        self.env["stock.location.history"].create(history_vals)

    def validate_stage(self):
        if not any(
            g in self.env.user.groups_id for g in self.stage_id.validation_group_ids
        ):
            raise ValidationError(_("Stage change not allowed for your user"))
        else:
            self.create_location_history("val")
            self.last_stage_validated = True
