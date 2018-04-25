# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, fields


class StockRequestKanban(models.Model):
    _name = 'stock.request.kanban'
    _description = 'Stock Request Kanban'
    _inherit = 'stock.request.abstract'

    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.request.kanban')
        return super().create(vals)
