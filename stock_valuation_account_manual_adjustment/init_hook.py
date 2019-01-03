# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.

    Without this script, if a database has a few hundred thousand
    moves, which is not unlikely, the update will take
    at least a few hours.
    """
    set_stock_valuation_account_manual_adjustment_in_account_move(cr)
    set_stock_valuation_account_manual_adjustment_in_account_move_line(cr)


def set_stock_valuation_account_manual_adjustment_in_account_move(cr):
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move' AND
    column_name='stock_valuation_account_manual_adjustment_id'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE account_move
            ADD COLUMN stock_valuation_account_manual_adjustment_id
            integer;
            COMMENT ON COLUMN
            account_move.stock_valuation_account_manual_adjustment_id IS
            'Stock Valuation Account Manual Adjustment';
            """)


def set_stock_valuation_account_manual_adjustment_in_account_move_line(cr):
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move_line' AND
    column_name='stock_valuation_account_manual_adjustment_id'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE account_move_line
            ADD COLUMN stock_valuation_account_manual_adjustment_id
            integer;
            COMMENT ON COLUMN
            account_move_line.stock_valuation_account_manual_adjustment_id
            IS 'Stock Valuation Account Manual Adjustment';
            """)
