# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018-2019 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    # FIXME: add in selection: shuttle, tray (module vertical lift)
    kind = fields.Selection([
        ('zone', 'Picking Zone'),
        ('area', 'Area'),
        ('bin', 'Bin'),
        ],
        string='Kind')

    picking_zone_id = fields.Many2one(
        'stock.picking.zone',
        string='Picking zone')

    picking_type_id = fields.Many2one(
        related='picking_zone_id.pick_type_id',
        help="Picking type for operations from this location",
        oldname='barcode_picking_type_id')

    area = fields.Char(
        'Area',
        compute='_compute_area', store=True,
        oldname='zone')

    @api.depends('name', 'kind', 'location_id.area')
    def _compute_area(self):
        for location in self:
            if location.kind == 'area':
                location.area = location.name
            else:
                location.area = location.location_id.area

    corridor = fields.Char('Corridor', help="Street")
    row = fields.Char('Row', help="Side in the street")
    rack = fields.Char('Rack', oldname='shelf', help="House number")
    level = fields.Char('Level', help="Height on the shelf")
    posx = fields.Integer('Box (X)')
    posy = fields.Integer('Box (Y)')
    posz = fields.Integer('Box (Z)')

    location_name_format = fields.Char(
        'Location Name Format',
        help="Format string that will compute the name of the location. "
             "Use location fields. Example: "
             "'{area}-{corridor:0>2}.{rack:0>3}"
             ".{level:0>2}'")

    @api.multi
    @api.onchange('corridor', 'row', 'rack', 'level',
                  'posx', 'posy', 'posz')
    def _compute_name(self):
        for location in self:
            if not location.kind == 'bin':
                continue
            area = location
            while not area.location_name_format:
                if not area.location_id:
                    return
                area = area.location_id
            location.name = area.location_name_format\
                .format(**location.read())

    _sql_constraints = [
        (
            'unique_location_name',
            'UNIQUE(name, location_id)',
            _('The location name must be unique'),
        )
    ]

