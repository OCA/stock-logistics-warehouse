# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    """Return whether the given column exists."""
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def pre_init_hook(cr):
    _logger.info("Initialize product_restriction on table stock_location")
    if not column_exists(cr, "stock_location", "product_restriction"):
        cr.execute(
            """
            ALTER TABLE stock_location
                ADD COLUMN product_restriction character varying;
            ALTER TABLE stock_location
                ADD COLUMN parent_product_restriction character varying;
        """
        )
    cr.execute(
        """
        UPDATE stock_location set product_restriction = 'any';
        UPDATE stock_location set parent_product_restriction = 'any'
        where location_id is not null;
    """
    )
