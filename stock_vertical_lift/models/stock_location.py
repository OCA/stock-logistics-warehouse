# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    vertical_lift_location = fields.Boolean(
        'Is a Vertical Lift View Location?',
        default=False,
        help="Check this box to use it as the view for Vertical"
        " Lift Shuttles.",
    )
    vertical_lift_kind = fields.Selection(
        selection=[
            ('view', 'View'),
            ('shuttle', 'Shuttle'),
            ('tray', 'Tray'),
            ('cell', 'Cell'),
        ],
        compute='_compute_vertical_lift_kind',
        store=True,
    )

    @api.depends(
        'location_id',
        'location_id.vertical_lift_kind',
        'vertical_lift_location',
    )
    def _compute_vertical_lift_kind(self):
        tree = {'view': 'shuttle', 'shuttle': 'tray', 'tray': 'cell'}
        for location in self:
            if location.vertical_lift_location:
                location.vertical_lift_kind = 'view'
                continue
            kind = tree.get(location.location_id.vertical_lift_kind)
            if kind:
                location.vertical_lift_kind = kind
