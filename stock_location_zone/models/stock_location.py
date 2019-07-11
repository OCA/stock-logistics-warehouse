# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018-2019 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    kind = fields.Char('Kind', help="zone, area, bin, reserve, ...")

    picking_zone_id = fields.Many2one('picking.zone', string='Picking zone')

    # floor = fields.Char('Level', help="Floor level")
    area = fields.Char('Area', oldname='zone')
    corridor = fields.Char('Corridor', help="Street")
    row = fields.Char('Row', help="Side in the street")
    rack = fields.Char('Rack', oldname='shelf', help="House number")
    level = fields.Char('Level', help="Height on the shelf")
    posx = fields.Integer('Box (X)')
    posy = fields.Integer('Box (Y)')
    posz = fields.Integer('Box (Z)')

    _sql_constraints = [
        (
            'unique_location_name',
            'UNIQUE(name, location_id)',
            _('The location name must be unique'),
        )
    ]

    @api.multi
    @api.onchange('area', 'corridor', 'row', 'rack', 'level',
                  'posx', 'posy', 'posz')
    def _compute_name(self):
        for location in self:
            if not location.picking_zone_id.location_name_format:
                continue
            location.name = location.picking_zone_id.location_name_format.format(
                self=location)
