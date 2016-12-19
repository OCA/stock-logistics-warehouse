# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

__name__ = u"Back up the old account move in inventory revaluation"
_logger = logging.getLogger(__name__)

__name__ = "Upgrade to 8.0.1.1.0"


def copy_account_move_id(cr):

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_inventory_revaluation' AND
    column_name='old_account_move_id'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE stock_inventory_revaluation
            ADD COLUMN old_account_move_id
            integer;
            COMMENT ON COLUMN stock_inventory_revaluation.old_account_move_id
            IS 'Old
            Journal Entry';
            """)
    cr.execute(
        """
        UPDATE stock_inventory_revaluation as sir
        SET old_account_move_id = account_move_id
        """)


def set_revaluation_in_account_move(cr):

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move' AND
    column_name='stock_inventory_revaluation_id'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE account_move ADD COLUMN stock_inventory_revaluation_id
            integer;
            COMMENT ON COLUMN account_move.stock_inventory_revaluation_id IS
            'Stock Inventory Revaluation';
            """)
    cr.execute(
        """
        UPDATE account_move as am
        SET stock_inventory_revaluation_id = sir.id
        FROM stock_inventory_revaluation as sir
        WHERE old_account_move_id = am.id
        """)


def set_revaluation_in_account_move_line(cr):
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move_line' AND
    column_name='stock_inventory_revaluation_id'""")
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE account_move_line
            ADD COLUMN stock_inventory_revaluation_id
            integer;
            COMMENT ON COLUMN account_move_line.stock_inventory_revaluation_id
            IS 'Stock Inventory Revaluation';
            """)
    cr.execute(
        """
        UPDATE account_move_line as aml
        SET stock_inventory_revaluation_id = sir.id
        FROM stock_inventory_revaluation as sir
        WHERE old_account_move_id = aml.move_id
        """)


def migrate(cr, version):
    if not version:
        return
    copy_account_move_id(cr)
    set_revaluation_in_account_move(cr)
    set_revaluation_in_account_move_line(cr)
