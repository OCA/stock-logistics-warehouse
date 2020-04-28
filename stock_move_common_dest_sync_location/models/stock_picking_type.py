# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    sync_common_move_dest_location = fields.Boolean(
        string="Group incoming goods in the same destination",
        help="When checked, the first time an operation is moved in a transfer"
        " of this type, the destination of the pending operations are changed"
        " to the same destination.",
    )
