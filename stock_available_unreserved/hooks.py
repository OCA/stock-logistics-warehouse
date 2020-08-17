# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)

import logging
logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.

    Without this script, if a database has a few hundred thousand
    quants, which is not unlikely, the update will take
    at least a few hours.

    The pre init script pre-computes the field using SQL.
    """
    add_field_unreserved_quantity(cr)
    add_field_contains_unreserved(cr)


def add_field_unreserved_quantity(cr):
    """Add field unreserved_quantity and compute its value"""

    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='stock_quant' AND
        column_name='unreserved_quantity'
    """)
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE stock_quant ADD COLUMN unreserved_quantity numeric;
            """)
        cr.execute(
            """
            UPDATE stock_quant
            SET unreserved_quantity = quantity - reserved_quantity
            WHERE reserved_quantity > 0.01
            """
        )


def add_field_contains_unreserved(cr):
    """Add field contains_unerserved and compute its value"""

    cr.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='stock_quant' AND
            column_name='contains_unreserved'
        """)
    if not cr.fetchone():
        cr.execute(
            """
            ALTER TABLE stock_quant ADD COLUMN contains_unreserved boolean;
            """)
        cr.execute(
            """
            UPDATE stock_quant
            SET contains_unreserved = (reserved_quantity > 0.01);
            """
        )
