# Copyright 2017 Syvain Van Hoof (Okia sprl) <sylvainvh@okia.be>
# Copyright 2017-2019 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PickingZone(models.Model):
    _name = 'picking.zone'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    picking_type_ids = fields.One2many(
        'stock.picking.type', 'picking_zone_id',
        string='Picking Types')
    location_name_format = fields.Char(
        'Location Name Format',
        help="Format string that will compute the name of the location. "
             "Use 'self' to access location object. Example: "
             "'{self.area}-{self.corridor:0>2}.{self.rack:0>3}.{self.level:0>2}'")

    _sql_constraints = [
        (
            'unique_picking_zone',
            'unique (code)',
            'The picking zone code must be unique',
        )
    ]
