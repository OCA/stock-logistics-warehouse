# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    checkout_sync = fields.Boolean(
        string="Checkout Synchronization",
        help="When checked, a button on transfers allow users to select "
        "a single location for all moves reaching this operation type. "
        "On selection, all the move lines are updated with the same destination.",
    )
