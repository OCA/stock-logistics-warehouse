# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools.misc import format_date


class StockRequest(models.Model):
    _inherit = "stock.request"

    def _get_default_stage_id(self):
        search_domain = [("fold", "=", False)]
        order = "sequence"
        return (
            self.env["stock.request.stage"]
            .search(search_domain, order=order, limit=1)
            .id
        )

    stage_id = fields.Many2one(
        "stock.request.stage",
        default=_get_default_stage_id,
        group_expand="_read_group_stage_ids",
    )
    color = fields.Integer(string="Color Index")
    expected_date_formatted = fields.Char(compute="_compute_expected_date_formatted")
    image_128 = fields.Image(related="product_id.image_128", readonly=True)

    @api.depends("expected_date")
    def _compute_expected_date_formatted(self):
        for request in self:
            request.expected_date_formatted = (
                format_date(self.env, request.expected_date_formatted)
                if request.expected_date
                else None
            )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return stages.sudo().search([], order=order)

    def update_request_state(self):
        for rec in self:
            set_state = rec.stage_id.set_state
            if set_state == "draft" and rec.state != "draft":
                rec.action_draft()
            elif set_state == "open" and rec.state != "open":
                rec.action_confirm()
            elif set_state == "cancel" and rec.state != "cancel":
                rec.action_cancel()
            elif set_state == "done" and rec.state != "done":
                rec.action_done()

    @api.model
    def create(self, vals):
        request = super(StockRequest, self).create(vals)
        if vals.get("stage_id"):
            request.update_request_state()
        return request

    def write(self, vals):
        super(StockRequest, self).write(vals)
        if vals.get("stage_id"):
            self.update_request_state()
