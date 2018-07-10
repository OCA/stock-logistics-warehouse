# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ProductPutaway(models.Model):
    _inherit = 'product.putaway'

    STOCK_MOVE_PENDING_STATES = [
        'confirmed',
        'partially_available',
        'assigned',
    ]

    @api.model
    def _get_putaway_options(self):
        res = super(ProductPutaway, self)._get_putaway_options()
        res.append(
            ('previous/empty', 'Previous location or empty one'),
        )
        return res

    # @override
    # super()::putaway_apply defined w/out @api.multi
    def putaway_apply(self, product):
        # TODO handle multiple warehouses
        if self.method == 'previous/empty':
            return self.get_previous_or_empty_location(product)
        return super().putaway_apply(product)

    @api.model
    def get_previous_or_empty_location(self, product):
        most_recent_location = self.get_most_recent_location(product)
        if most_recent_location:
            return most_recent_location
        return self.get_closest_empty_sublocation()

    @api.model
    def get_most_recent_location(self, product, root_location=False):
        """Return most recent location that received that product.

        Most recent location is a `location_dest_id` of a most recent confirmed
        `stock.move.line` (ordered by date, then by ID) ending in a location
        under the given `root_location`.

        :param product: a product to search moves for
        :param root_location: defaults to WH/Stock
        """
        exclude_root = self.env.context.get('exclude_root')
        if not root_location:
            root_location = self.env.ref('stock.stock_location_stock')
        domain = [
            ('product_id', '=', product.id),
            ('state', 'in', self.STOCK_MOVE_PENDING_STATES + ['done']),
            ('location_dest_id', 'child_of', root_location.id),
        ]
        hooked_lot_id = self.env.context.get('lot_id')
        if product.tracking == 'lot' and hooked_lot_id:
            # Try to search for this particular lot
            domain.append(('lot_id', '=', hooked_lot_id))
        if exclude_root:
            domain.append(('location_dest_id', '!=', root_location.id))
        last_known_move = self.env['stock.move.line'].search(
            domain, order='date desc, id desc', limit=1)
        return last_known_move.location_dest_id

    @api.model
    def get_closest_empty_sublocation(self, root_location=False):
        """Ordered by Z-Y-X successively in ascending order."""
        if not root_location:
            root_location = self.env.ref('stock.stock_location_stock')
        exclude_root = self.env.context.get('exclude_root')
        domain = [
            ('quant_ids', '=', False),
            ('usage', '=', 'internal'),
            ('location_id', 'child_of', root_location.id),
            # exclude locations having their own sublocations
            ('child_ids', '=', False),
        ]
        if exclude_root:
            domain.append(('id', '!=', root_location.id))
        # FIXME is that efficient enough?
        stock_move_confirmed_states = [
            'confirmed',
            'partially_available',
            'assigned',
        ]
        # TODO extract order to context
        empty_locations = self.env['stock.location'].search(
            domain, order='posz asc, posy asc, posx asc')
        for current_empty_location in empty_locations:
            # check if there are incoming moves to that location
            incoming_moves_pending = self.env['stock.move.line'].search([
                '|',
                '&',
                # `move.line`-s of other moves
                ('state', 'not in', stock_move_confirmed_states),
                ('location_dest_id', '=', current_empty_location.id),
                '&',
                # respect `move.line`-s of the same `stock.move`
                ('state', '=', 'waiting'),
                ('move_id', '=', self.env.context.get('current_move_id')),
            ], limit=1)
            if not incoming_moves_pending:
                return current_empty_location
        return self.env['stock.location']
