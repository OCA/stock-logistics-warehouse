# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    src_routing_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Source Routing Operation',
        help="Change destination of the move line according to the"
             " default destination of the picking type after reservation"
             " occurs, when the source of the move is in this location"
             " (including sub-locations). A new chained move will be created "
             " to reach the original destination.",
    )
    dest_routing_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Destination Routing Operation',
        help="Change source of the move line according to the"
             " default source of the picking type after reservation"
             " occurs, when the destination of the move is in this location"
             " (including sub-locations). A new chained move will be created "
             " to reach the original source.",
    )

    @api.constrains('src_routing_picking_type_id')
    def _check_src_routing_picking_type_id(self):
        for location in self:
            picking_type = location.src_routing_picking_type_id
            if not picking_type:
                continue
            if picking_type.default_location_src_id != location:
                raise ValidationError(_(
                    'A picking type for source routing operations cannot have'
                    ' a different default source location than the location it'
                    ' is used on.'
                ))

    @api.constrains('dest_routing_picking_type_id')
    def _check_dest_routing_picking_type_id(self):
        for location in self:
            picking_type = location.dest_routing_picking_type_id
            if not picking_type:
                continue
            if picking_type.default_location_dest_id != location:
                raise ValidationError(_(
                    'A picking type for destination routing operations '
                    'cannot have a different default destination location'
                    ' than the location it is used on.'
                ))

    @api.multi
    def _find_picking_type_for_routing(self, routing_type):
        if routing_type not in ('src', 'dest'):
            raise ValueError(
                "routing_type must be one of ('src', 'dest')"
            )
        self.ensure_one()
        # First select all the parent locations and the matching
        # picking types. In a second step, the picking type matching the
        # closest location
        # is searched in memory. This is to avoid doing an SQL query
        # for each location in the tree.
        tree = self.search(
            [('id', 'parent_of', self.id)],
            # the recordset will be ordered bottom location to top location
            order='parent_path desc'
        )
        if routing_type == 'src':
            routing_fieldname = 'src_routing_location_ids'
            default_location_fieldname = 'default_location_src_id'
        else:  # dest
            routing_fieldname = 'dest_routing_location_ids'
            default_location_fieldname = 'default_location_dest_id'
        domain = [
            (routing_fieldname, '!=', False),
            (default_location_fieldname, 'in', tree.ids)
        ]
        picking_types = self.env['stock.picking.type'].search(domain)
        # the first location is the current move line's source location,
        # then we climb up the tree of locations
        for location in tree:
            match = picking_types.filtered(
                lambda p: p[default_location_fieldname] == location
            )
            if match:
                # we can only have one match as we have a unique
                # constraint on is_zone + source (or dest) location
                return match
        return self.env['stock.picking.type']
