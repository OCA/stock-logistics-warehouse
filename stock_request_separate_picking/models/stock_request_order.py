# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    procurement_group_id = fields.Many2one(
        copy=False,
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if (
            self.env.company.stock_request_allow_separate_picking
            and not res.procurement_group_id
        ):
            res.procurement_group_id = self.env["procurement.group"].create(
                {"name": res.name}
            )
            for line in res.stock_request_ids:
                line.procurement_group_id = res.procurement_group_id
        return res
