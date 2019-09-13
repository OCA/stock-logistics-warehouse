# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018-2019 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_zone = fields.Boolean(
        string='Is a Zone Location?',
        help='Mark to define this location as a zone',
    )

    zone_location_id = fields.Many2one(
        'stock.location',
        string='Location zone',
        compute='_compute_location_zone',
        store=True,
        index=True,
    )

    location_kind = fields.Selection(
        [
            ('zone', 'Zone'),
            ('area', 'Area'),
            ('bin', 'Bin'),
            ('stock', 'Main Stock'),
            ('other', 'Other'),
        ],
        string='Location Kind',
        compute='_compute_location_zone',
        help='Group location according to their kinds:'
             '* Zone: locations that are flagged as being zones'
             '* Area: locations with children that are part of a zone'
             '* Bin: locations without children that are part of a zone'
             '* Stock: internal locations whose parent is a view'
             '* Other: any other location',
    )

    @api.depends('is_zone', 'usage', 'location_id.usage', 'child_ids',
                 'location_id.is_zone')
    def _compute_location_zone(self):
        for location in self:
            if location.is_zone:
                location.location_kind = 'zone'
                location.zone_location_id = location
                continue

            # Get the zone from the parents
            parent = location.location_id
            while parent:
                if parent.is_zone:
                    zone_location = parent
                    break
                parent = parent.location_id
            else:
                zone_location = self.browse()

            location.zone_location_id = zone_location

            # Internal locations whose parent is view are main stocks
            if (
                location.usage == 'internal'
                and location.location_id.usage == 'view'
            ):
                location.location_kind = 'stock'
                continue
            # Internal locations having a zone and no children are bins
            if (
                location.usage == 'internal'
                and zone_location
                and not location.child_ids
            ):
                location.location_kind = 'bin'
                continue
            # Internal locations having a zone and children are areas
            if (
                location.usage == 'internal'
                and zone_location
                and location.child_ids
            ):
                location.location_kind = 'area'
                continue
            # All the rest are other locations
            location.location_kind = 'other'

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)") % self.name
        return super().copy(default=default)
