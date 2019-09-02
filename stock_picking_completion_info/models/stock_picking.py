# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, fields


class PickingType(models.Model):

    _inherit = 'stock.picking.type'

    display_completion_info = fields.Boolean(
        help='Inform operator of a completed operation at processing and at'
        ' completion'
    )


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    completion_info = fields.Selection(
        [
            ('no', 'No'),
            (
                'last_picking',
                'Completion of this operation allows next operations to be '
                'processed.',
            ),
            (
                'next_picking_ready',
                'Next operations are ready to be processed.',
            ),
        ],
        compute='_compute_completion_info',
    )

    @api.depends(
        'picking_type_id.display_completion_info',
        'move_lines.move_dest_ids.move_orig_ids.state',
    )
    def _compute_completion_info(self):
        for picking in self:
            if (
                picking.state == 'draft'
                or not picking.picking_type_id.display_completion_info
            ):
                picking.completion_info = 'no'
                continue
            # Depending moves are all the origin moves linked to the
            # destination pickings' moves
            depending_moves = picking.move_lines.mapped(
                'move_dest_ids.picking_id.move_lines.move_orig_ids'
            )
            if all(m.state in ('done', 'cancel') for m in depending_moves):
                picking.completion_info = 'next_picking_ready'
                continue
            # If there aren't any depending move from another picking that is
            # not done, then actual picking is the last to process
            other_depending_moves = (
                depending_moves - picking.move_lines
            ).filtered(lambda m: m.state not in ('done', 'cancel'))
            if not other_depending_moves:
                picking.completion_info = 'last_picking'
                continue
            picking.completion_info = 'no'
