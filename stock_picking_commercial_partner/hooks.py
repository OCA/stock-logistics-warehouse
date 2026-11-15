# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Initialise the commercial_partner_id field on stock.picking"""
    if not sql.column_exists(cr, "stock_picking", "commercial_partner_id"):
        _logger.info("Create column commercial_partner_id on stock_picking")
        cr.execute(
            """
            ALTER TABLE stock_picking ADD COLUMN commercial_partner_id integer;
            """
        )
        _logger.info("Init commercial_partner_id on stock_picking")
        cr.execute(
            """
            UPDATE stock_picking
            SET commercial_partner_id = res_partner.commercial_partner_id
            FROM res_partner
            WHERE
                stock_picking.partner_id = res_partner.id;
        """
        )
        _logger.info(f"{cr.rowcount} rows updated in stock_picking")
