# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018-2019 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    corridor = fields.Char("Corridor", help="Define as the street")
    row = fields.Char("Row", help="Define as the side within the street")
    rack = fields.Char("Rack", help="Define as the house number within the street")
    level = fields.Char("Level", help="Define as the floor of the house")
    posx = fields.Integer(
        "Box (X)",
        help="Optional (X) coordinate of the bin if the location"
        " is split in several parts. (e.g. drawer storage)",
    )
    posy = fields.Integer(
        "Box (Y)",
        help="Optional (Y) coordinate of the bin if the location"
        " is split in several parts. (e.g. drawer storage)",
    )
    posz = fields.Integer(
        "Box (Z)",
        help="Optional (Z) coordinate of the bin if the location"
        " is split in several parts. (e.g. storage tray)",
    )
