# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    consolidate_priority = fields.Boolean(
        string="Raise priority when partially available",
        help="Tick this box to raise the priority of all previous related"
        " picking when current transfer will be made partially available."
        " This is usually used in packing zone when several people work"
        " on different transfers to be consolidated in the packing zone."
        " When the first one finish, all other related pickings gets with"
        " a high priority. The goal is to reduce the number of order being"
        " packed at the same time as the space is often limited.",
        default=False,
    )
