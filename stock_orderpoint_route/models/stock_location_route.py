# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Route(models.Model):
    _inherit = "stock.location.route"

    orderpoint_selectable = fields.Boolean(
        string="Applicable on Reordering Rules",
        help="When checked, the route will be selectable in the Reordering"
        " rules. It will take priority over the Warehouse route for"
        " reordering. ",
    )
