# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequestLine(models.Model):

    _inherit = "purchase.request.line"

    stock_request_ids = fields.Many2many(
        comodel_name="stock.request", string="Stock Requests", copy=False
    )

    @api.constrains("stock_request_ids")
    def _check_purchase_request_company_constrains(self):
        if any(
            any(req.company_id != pol.company_id for req in pol.stock_request_ids)
            for pol in self
        ):
            raise ValidationError(
                _(
                    "You cannot link a purchase request line "
                    "to a stock request that belongs to "
                    "another company."
                )
            )
