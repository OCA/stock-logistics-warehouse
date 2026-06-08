# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command, fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    def _prepare_move_line_vals(self):
        vals = super()._prepare_move_line_vals()
        if self.analytic_tag_ids:
            vals.update(analytic_tag_ids=[Command.set(self.analytic_tag_ids.ids)])
        return vals
