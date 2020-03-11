# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    sync_common_move_dest_location = fields.Boolean(
        string="Sync destination location for common destination moves",
        help="When checked, updating the destination location on a move line "
             "will update move lines from common destination moves (i.e moves "
             "having a chained destination move sharing the same picking)"
    )
