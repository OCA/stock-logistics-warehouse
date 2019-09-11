# Copyright 2017 Syvain Van Hoof (Okia sprl) <sylvainvh@okia.be>
# Copyright 2016-2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    location_name_format = fields.Char(
        'Location Name Format',
        help="Format string that will compute the name of the location. "
             "Use location fields. Example: "
             "'{area}-{corridor:0>2}.{rack:0>3}"
             ".{level:0>2}'")

    area = fields.Char(
        'Area',
        compute='_compute_area',
        store=True,
    )

    @api.depends('name', 'location_kind', 'location_id.area')
    def _compute_area(self):
        for location in self:
            if location.location_kind == 'area':
                location.area = location.name
            else:
                location.area = location.location_id.area

    @api.multi
    @api.onchange('corridor', 'row', 'rack', 'level',
                  'posx', 'posy', 'posz')
    def _onchange_attribute_compute_name(self):
        for location in self:
            if not location.location_kind == 'bin':
                continue
            area = location
            while area and not area.location_name_format:
                area = area.location_id
            if not area:
                continue
            template = area.location_name_format
            # We don't want to use the full browse record as it would
            # give too much access to internals for the users.
            # We cannot use location.read() as we may have a NewId.
            # We should have the record's values in the cache at this
            # point. We must be cautious not to leak an environment through
            # relational fields.
            location.name = template.format(**location._cache)
