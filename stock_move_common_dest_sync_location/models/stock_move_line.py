# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    picking_type_sync_common_move_dest_location = fields.Boolean(
        related='picking_id.picking_type_id.sync_common_move_dest_location',
        readonly=True
    )

    def write(self, vals):
        res = super().write(vals)
        if vals.get('location_dest_id') and not self.env.context.get('_sync_common_dest_location'):
            related_moves = self.env['stock.move']
            for move_line in self:
                if not move_line.picking_type_sync_common_move_dest_location:
                    continue
                related_moves |= move_line.move_id.common_dest_move_ids
            if related_moves:
                moves_lines_to_update = related_moves.mapped('move_line_ids') - self
                moves_lines_to_update.with_context(_sync_common_dest_location=True).write(
                    {
                        'location_dest_id': vals.get('location_dest_id'),
                    }
                )
        return res
