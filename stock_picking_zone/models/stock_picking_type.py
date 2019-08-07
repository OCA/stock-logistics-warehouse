# Copyright 2019 Camptocamp (https://www.camptocamp.com)

from odoo import _, api, exceptions, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_zone = fields.Boolean(
        help="Change destination of the move line according to the"
        " default destination setup after reservation occurs",
    )

    @api.constrains('is_zone', 'default_location_src_id')
    def _check_zone_location_src_unique(self):
        for picking_type in self:
            if not picking_type.is_zone:
                continue
            src_location = picking_type.default_location_src_id
            domain = [
                ('is_zone', '=', True),
                ('default_location_src_id', '=', src_location.id),
                ('id', '!=', picking_type.id)
            ]
            other = self.search(domain)
            if other:
                raise exceptions.ValidationError(
                    _('Another zone picking type (%s) exists for'
                      ' the some source location.') % (other.display_name,)
                )

    @api.model
    def _find_zone_for_location(self, location):
        # First select all the parent locations and the matching
        # zones. In a second step, the zone matching the closest location
        # is searched in memory. This is to avoid doing an SQL query
        # for each location in the tree.
        tree = self.env['stock.location'].search(
            [('id', 'parent_of', location.id)],
            # the recordset will be ordered bottom location to top location
            order='parent_path desc'
        )
        zones = self.search([
            ('is_zone', '=', True),
            ('default_location_src_id', 'in', tree.ids)
        ])
        # the first location is the current move line's source location,
        # then we climb up the tree of locations
        for location in tree:
            match = [
                zone for zone in zones
                if zone.default_location_src_id == location
            ]
            if match:
                # we can only have one match as we have a unique
                # constraint on is_zone + source location
                return match[0]
        return self.browse()
