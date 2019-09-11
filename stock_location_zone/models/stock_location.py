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
        compute='_compute_zone_location_id',
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
        compute='_compute_location_kind',
        help='Group location according to their kinds:'
             '* Zone: locations that are flagged as being zones'
             '* Area: locations with children that are part of a zone'
             '* Bin: locations without children that are part of a zone'
             '* Stock: internal locations whose parent is a view'
             '* Other: any other location',
    )

    _sql_constraints = [(
        'name_zone_unique',
        'EXCLUDE (name WITH =, zone_location_id WITH =)'
        ' WHERE (zone_location_id IS NOT NULL)',
        'Another location with the same name exists in the same zone.'
        ' Please rename the location.'
    )]

    @api.depends('is_zone', 'usage', 'location_id.usage', 'zone_location_id',
                 'child_ids')
    def _compute_location_kind(self):
        for location in self:
            if location.is_zone:
                location.location_kind = 'zone'
                continue
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
                and location.zone_location_id
                and not location.child_ids
            ):
                location.location_kind = 'bin'
                continue
            # Internal locations having a zone and children are areas
            if (
                location.usage == 'internal'
                and location.zone_location_id
                and location.child_ids
            ):
                location.location_kind = 'area'
                continue
            # All the rest are other locations
            location.location_kind = 'other'

    @api.depends('is_zone', 'location_id.zone_location_id')
    def _compute_zone_location_id(self):
        for location in self:
            if location.is_zone:
                location.zone_location_id = location
            else:
                location.zone_location_id = \
                    location.location_id.zone_location_id

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)") % self.name
        return super().copy(default=default)
