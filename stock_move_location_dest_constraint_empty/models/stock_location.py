# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):

    _inherit = 'stock.location'

    def check_move_dest_constraint(self, line=None, product=None):
        """Raise Validation error if not allowed"""
        res = super().check_move_dest_constraint(line=line)
        existing_quant = self.env['stock.quant'].search([
            ('location_id', '=', self.id), ('quantity', '>', 0)
        ])
        if existing_quant:
            raise ValidationError(_(
                'At least one quant already exists on this location'
            ))
        search_domain = [
            ('location_dest_id', '=', self.id),
            ('state', 'not in', ('done', 'cancel', 'draft')),
        ]
        if line:
            search_domain.append(('id', '!=', line.move_id.id))
        planned_moves = self.env['stock.move'].search(search_domain)
        if planned_moves:
            raise ValidationError(_(
                'At least one stock move is planned on this locations'
            ))
        return res
