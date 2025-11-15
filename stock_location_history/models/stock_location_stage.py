from odoo import fields, models


class StockLocationStage(models.Model):
    _name = "stock.location.stage"
    _description = "Stock Location Stage"
    _order = "sequence, name, id"

    name = fields.Char(required=True)
    description = fields.Text()
    validation = fields.Boolean(string="Requires validation?", default=False)
    sequence = fields.Integer(default=1)
    active = fields.Boolean(help="If active, the stage will be displayed", default=True)
    fold = fields.Boolean(
        "Folded in Kanban",
        help="This stage is folded in the kanban view when "
        "there are no record in that stage to display.",
    )
    is_closed = fields.Boolean(
        "Is a close stage", help="Locations in this stage are considered as closed."
    )
    is_default = fields.Boolean("Is a default stage", help="Used a default stage")
    next_ids = fields.Many2many(
        "stock.location.stage",
        "location_stage_rel",
        "stage_id",
        "allowed_stage_id",
        string="Allowed next stages",
    )
    is_use = fields.Boolean(
        string="Usage stage?",
        help="Mark this stage as a usage stage if raw material is being taken "
        "from the location",
    )
    validation_group_ids = fields.Many2many(
        "res.groups",
        "location_stage_validation_group_rel",
        "stage_id",
        "group_id",
        string="Groups allowed to validate",
        help="Only users in this group can validate the current stage",
    )
    change_group_ids = fields.Many2many(
        "res.groups",
        "location_stage_change_group_rel",
        "stage_id",
        "group_id",
        string="Groups allowed to change the stage",
        help="Only users in this group can move the process forward from this stage",
    )
