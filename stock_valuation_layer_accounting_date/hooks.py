# Copyright 2022 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    if not column_exists(cr, "stock_valuation_layer", "accounting_date"):
        _logger.info("Creating column 'accounting_date' in stock_valuation_layer.")
        create_column(cr, "stock_valuation_layer", "accounting_date", "date")
    _logger.info("Updating accounting_date with account_move.date.")
    cr.execute(
        """
        UPDATE stock_valuation_layer svl
        SET accounting_date = am.date
        FROM account_move am
        WHERE svl.account_move_id = am.id
        AND am.state = 'posted'
        """
    )
    _logger.info("Updating 'account_date' with stock_valuation_layer.create_date.")
    cr.execute(
        """
        UPDATE stock_valuation_layer svl
        SET accounting_date = svl.create_date::date
        WHERE svl.accounting_date IS NULL
        """
    )
