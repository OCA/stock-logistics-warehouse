# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Post init hook to set compute the volume on pending move and pickings."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    pickings = env["stock.picking"].search([("state", "not in", ["done", "cancel"])])
    moves = env["stock.move"].search(
        [
            "|",
            ("state", "not in", ["done", "cancel"]),
            ("picking_id", "in", pickings.ids),
        ]
    )
    _logger.info("Compute volumes for %d moves", len(moves))
    moves._compute_volume()


def pre_init_hook(cr):
    """Pre init create volume column on stock.picking and stock.move"""
    if not column_exists(cr, "stock_move", "volume"):
        create_column(cr, "stock_move", "volume", "double precision")
    if not column_exists(cr, "stock_picking", "volume"):
        create_column(cr, "stock_picking", "volume", "double precision")
