# Copyright 2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    orderpoint_ids = fields.Many2many(
        comodel_name="stock.warehouse.orderpoint", string="Linked Reordering Rules"
    )

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        if self.orderpoint_ids:
            res["orderpoint_ids"] = self.orderpoint_ids
        return res

    def _merge_moves_fields(self):
        res = super()._merge_moves_fields()
        res["orderpoint_ids"] = [(4, m.id) for m in self.mapped("orderpoint_ids")]
        return res
