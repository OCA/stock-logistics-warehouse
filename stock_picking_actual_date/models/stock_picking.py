# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    actual_date = fields.Date(help="Actual date of stock picking.")
    is_editable_actual_date = fields.Boolean(
        compute="_compute_is_editable_actual_date", string="Is Editable"
    )

    def _compute_is_editable_actual_date(self):
        for record in self:
            if self.env.user.has_group("stock.group_stock_manager"):
                record.is_editable_actual_date = True
            else:
                record.is_editable_actual_date = record.state not in [
                    "done",
                    "cancel",
                ]
