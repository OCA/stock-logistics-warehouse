# Copyright 2019 Camptocamp (https://www.camptocamp.com)

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_assign(self):
        super()._action_assign()
        self._apply_move_location_zone()

    def _apply_move_location_zone(self):
        for move in self:
            if move.state != 'assigned':
                continue
            pick_type_model = self.env['stock.picking.type']
            # TODO what if we have more than one move line?
            # split?
            source = move.move_line_ids[0].location_id
            zone = pick_type_model._find_zone_for_location(source)
            if not zone:
                continue
            if move.location_dest_id == zone.default_location_dest_id:
                continue
            move._do_unreserve()
            move.write({
                'location_dest_id': zone.default_location_dest_id.id,
                'picking_type_id': zone.id,
            })
            move._insert_middle_moves()
            move._assign_picking()
            move._action_assign()

    def _insert_middle_moves(self):
        self.ensure_one()
        dest_moves = self.move_dest_ids
        dest_location = self.location_dest_id
        for dest_move in dest_moves:
            final_location = dest_move.location_id
            if dest_location == final_location:
                # shortcircuit to avoid a query checking if it is a child
                continue
            child_locations = self.env['stock.location'].search([
                ('id', 'child_of', final_location.id)
            ])
            if dest_location in child_locations:
                # normal behavior, we don't need a move between A and B
                continue
            # Insert move between the source and destination for the new
            # operation
            middle_move_values = self._prepare_middle_move_values(
                final_location
            )
            middle_move = self.copy(middle_move_values)
            dest_move.write({
                'move_orig_ids': [(3, self.id), (4, middle_move.id)],
            })
            # FIXME: if we have more than one move line on a move,
            # the move will only have the dest of the last one.
            # We have to split the move.
            self.write({
                'move_dest_ids': [(3, dest_move.id), (4, middle_move.id)],
            })
            middle_move._action_confirm()

    def _prepare_middle_move_values(self, destination):
        return {
            'picking_id': False,
            'location_id': self.location_dest_id.id,
            'location_dest_id': destination.id,
            'state': 'waiting',
            'picking_type_id': self.picking_id.picking_type_id.id,
        }
