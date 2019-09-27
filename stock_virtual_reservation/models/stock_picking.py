# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Add store on the field, as it is quite used in the searches,
    # and this is an easy-win to reduce the number of SQL queries.
    picking_type_code = fields.Selection(store=True)
    need_rule_pull = fields.Boolean(compute="_compute_need_rule_pull")

    @api.depends("move_lines.need_rule_pull")
    def _compute_need_rule_pull(self):
        for picking in self:
            picking.need_rule_pull = any(
                move.need_rule_pull for move in picking
            )

    @api.multi
    def release_virtual_reservation(self):
        self.mapped("move_lines").release_virtual_reservation()
