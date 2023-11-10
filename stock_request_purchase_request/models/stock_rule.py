# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):

    _inherit = "stock.rule"

    @api.model
    def _prepare_purchase_request_line(self, request_id, procurement):
        vals = super()._prepare_purchase_request_line(request_id, procurement)
        values = procurement.values
        if "stock_request_id" in values:
            vals["stock_request_ids"] = [(4, values["stock_request_id"])]
        return vals

    @api.model
    def _prepare_purchase_request(self, origin, values):
        vals = super()._prepare_purchase_request(origin, values)
        if "stock_request_id" in values:
            vals["stock_request_ids"] = [(4, values["stock_request_id"])]
        return vals
