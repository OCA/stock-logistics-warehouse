# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):

    _inherit = 'stock.location'

    routing_operation_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Routing operation',
        help="Change destination of the move line according to the"
             " default destination setup after reservation occurs",
    )

    @api.constrains('routing_operation_picking_type_id')
    def _check_routing_operation_picking_type_id(self):
        for location in self:
            picking_type = location.routing_operation_picking_type_id
            if not picking_type:
                continue
            if picking_type.default_location_src_id != location:
                raise ValidationError(_(
                    'A picking type for routing operations cannot have a'
                    ' different default source location than the location it '
                    'is used on.'
                ))

    @api.multi
    def _find_picking_type_for_routing_operation(self):
        self.ensure_one()
        # First select all the parent locations and the matching
        # picking types. In a second step, the picking type matching the closest location
        # is searched in memory. This is to avoid doing an SQL query
        # for each location in the tree.
        tree = self.search(
            [('id', 'parent_of', self.id)],
            # the recordset will be ordered bottom location to top location
            order='parent_path desc'
        )
        picking_types = self.env['stock.picking.type'].search([
            ('routing_operation_location_ids', '!=', False),
            ('default_location_src_id', 'in', tree.ids)
        ])
        # the first location is the current move line's source location,
        # then we climb up the tree of locations
        for location in tree:
            match = picking_types.filtered(
                lambda p: p.default_location_src_id == location
            )
            if match:
                # we can only have one match as we have a unique
                # constraint on is_zone + source location
                return match
        return self.env['stock.picking.type']
