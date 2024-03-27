# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

try:
    from openupgradelib import openupgrade
except Exception:
    from odoo.tools import sql as openupgrade

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Pre-creating column reservation_date for table stock_move")
    if not openupgrade.column_exists(cr, "stock_move", "reservation_date"):
        cr.execute(
            """
            ALTER TABLE stock_move
            ADD COLUMN reservation_date date;
            COMMENT ON COLUMN stock_move.reservation_date
            IS 'Date to Reserve';
            """
        )
