# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging


logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.

    Without this script, if a database has a few hundred thousand
    move lines, which is not unlikely, the update will take
    at least a few hours.

    The pre init script pre-computes the field using SQL.
    """
    store_field_stock_inventory_revaluation_id(cr)


def store_field_stock_inventory_revaluation_id(cr):

    cr.execute(
        """SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move_line' AND
    column_name='stock_inventory_revaluation_id'"""
    )
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE account_move_line
            ADD COLUMN stock_inventory_revaluation_id integer;
            COMMENT ON COLUMN account_move_line.stock_inventory_revaluation_id
            IS 'Stock Inventory Revaluation';
            """
        )

    logger.info(
        "Computing field stock_inventory_revaluation_id on account.move.line"
    )
