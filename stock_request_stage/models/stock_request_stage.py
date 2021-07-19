# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from odoo.addons.stock_request.models.stock_request import REQUEST_STATES


class StockRequestStage(models.Model):
    _name = "stock.request.stage"
    _description = "Stock Request Stage"
    _order = "sequence, id"

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get("default_project_id")
        return [default_project_id] if default_project_id else None

    name = fields.Char(string="Stage Name", required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage is folded in the kanban view when there are "
        "no records in that stage to display.",
    )
    set_state = fields.Selection(
        selection=REQUEST_STATES,
        string="Target Status",
        help="Status that should be set when the stock request reaches to "
        "this stage.",
    )
    complete_pickings = fields.Boolean(
        string="Complete pickings",
        help="When this stage is reached the system will try to complete the "
        "pickings associated with the stock request.",
    )
