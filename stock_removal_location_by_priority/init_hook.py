# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """
    The objective of this hook is to speed up the installation
    of the module on an existing Odoo instance.

    Without this script, big databases can take a long time to install this
    module.
    """
    set_stock_location_removal_priority_default(cr)
    set_stock_quant_removal_priority_default(cr)


def set_stock_location_removal_priority_default(cr):
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_location' AND
    column_name='removal_priority'""")
    if not cr.fetchone():
        logger.info('Creating field removal_priority on stock_location')
        cr.execute(
            """
            ALTER TABLE stock_location
            ADD COLUMN removal_priority integer
            DEFAULT 10;
            """)


def set_stock_quant_removal_priority_default(cr):
    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_quant' AND
    column_name='removal_priority'""")
    if not cr.fetchone():
        logger.info('Creating field removal_priority on stock_quant')
        cr.execute(
            """
            ALTER TABLE stock_quant
            ADD COLUMN removal_priority integer
            DEFAULT 10;
            """)
