# Copyright 2017 Syvain Van Hoof (Okia sprl) <sylvainvh@okia.be>
# Copyright 2017-2019 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PickingZone(models.Model):
    _name = 'stock.picking.zone'
    _description = "Stock Picking Zone"

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Pick Type',
        help="Picking type for operations from this location",
    )

    _sql_constraints = [
        (
            'unique_picking_zone',
            'unique (code)',
            'The picking zone code must be unique',
        )
    ]
