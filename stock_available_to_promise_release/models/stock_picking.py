# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Add store on the field, as it is quite used in the searches,
    # and this is an easy-win to reduce the number of SQL queries.
    picking_type_code = fields.Selection(store=True)
    need_release = fields.Boolean(compute="_compute_need_release")

    @api.depends("move_lines.need_release")
    def _compute_need_release(self):
        for picking in self:
            picking.need_release = any(
                move.need_release for move in picking.move_lines
            )

    @api.multi
    def release_available_to_promise(self):
        self.mapped("move_lines").release_available_to_promise()
