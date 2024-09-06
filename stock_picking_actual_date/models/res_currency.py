# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _convert(self, from_amount, to_currency, company, date, round=True):
        if self.env.context.get("actual_date"):
            date = self.env.context.get("actual_date")
        return super()._convert(from_amount, to_currency, company, date, round)
