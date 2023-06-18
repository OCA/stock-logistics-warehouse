# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockRequestAbstract(models.AbstractModel):
    _inherit = "stock.request.abstract"

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
            if res.order_id:
                res.procurement_group_id = res.order_id.procurement_group_id
            else:
                res.procurement_group_id = self.env["procurement.group"].create(
                    {"name": res.name}
                )
        return res
