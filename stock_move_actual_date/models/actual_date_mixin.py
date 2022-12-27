# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ActualDateMixin(models.AbstractModel):
    _name = "actual.date.mixin"

    actual_date = fields.Date(
        tracking=True,
        help="If set, the value is propagated "
        "to the related journal entries as the date.",
    )
    is_editable_actual_date = fields.Boolean(
        compute="_compute_is_editable_actual_date", string="Is Editable"
    )

    def _compute_is_editable_actual_date(self):
        for rec in self:
            rec.is_editable_actual_date = False
            if rec.state not in ["done", "cancel"] or self.env.user.has_group(
                "stock.group_stock_manager"
            ):
                rec.is_editable_actual_date = True
