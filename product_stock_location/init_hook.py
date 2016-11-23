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
    create_product_stock_locations(cr)


def create_product_stock_locations(cr):

    cr.execute("""SELECT relname FROM pg_class
    WHERE relname = 'product_stock_location'""")

    if not cr.fetchone():
        logger.info('Creating table product_stock_location')
        cr.execute(
            """
            CREATE TABLE product_stock_location(
            id SERIAL NOT NULL,
            PRIMARY KEY(id),
            product_id integer,
            location_id integer,
            company_id integer,
            parent_id integer)
            """)

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' AND
    column_name='product_stock_location_id'""")
    if not cr.fetchone():
        logger.info('Extending table stock_move with column '
                    'product_stock_location_id')
        cr.execute(
            """
            ALTER TABLE stock_move ADD COLUMN product_stock_location_id
            integer;
            COMMENT ON COLUMN stock_move.product_stock_location_id IS
            'Product Source Stock Location';
            """)

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' AND
    column_name='product_stock_location_dest_id'""")

    if not cr.fetchone():
        logger.info('Extending table stock_move with column '
                    'product_stock_location_dest_id')
        cr.execute(
            """
            ALTER TABLE stock_move ADD COLUMN product_stock_location_dest_id
            integer;
            COMMENT ON COLUMN stock_move.product_stock_location_dest_id IS
            'Product Destination Stock Location';
            """)

    cr.execute("""SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_quant' AND
    column_name='product_stock_location_id'""")

    if not cr.fetchone():
        logger.info('Extending table stock_quant')
        cr.execute(
            """
            ALTER TABLE stock_quant ADD COLUMN product_stock_location_id
            integer;
            COMMENT ON COLUMN stock_quant.product_stock_location_id IS
            'Product Source Stock Location';
            """)

    logger.info('Creating product stock locations based on all moves')
    cr.execute(
        """
        INSERT INTO product_stock_location(product_id, location_id,
        company_id)
        SELECT sm.product_id, sl2.id, sm.company_id
        FROM stock_move AS sm
        INNER JOIN stock_location AS sl1
        ON sl1.id = sm.location_id
        INNER JOIN stock_location AS sl2
        ON sl2.parent_left <= sl1.parent_left
        AND sl2.parent_right >= sl1.parent_right
        WHERE sl2.id is not null
        GROUP BY sm.product_id, sl2.id, sm.company_id
        """
    )

    cr.execute(
        """
        INSERT INTO product_stock_location(product_id, location_id,
        company_id)
        SELECT sm.product_id, sl2.id, sm.company_id
        FROM stock_move AS sm
        INNER JOIN stock_location AS sl1
        ON sl1.id = sm.location_dest_id
        INNER JOIN stock_location AS sl2
        ON sl2.parent_left <= sl1.parent_left
        AND sl2.parent_right >= sl1.parent_right
        WHERE NOT EXISTS (SELECT psl.id
        FROM product_stock_location AS psl
        WHERE psl.product_id = sm.product_id
        AND psl.location_id = sm.location_dest_id
        AND psl.company_id = sm.company_id)
        AND sl2.id is not null
        GROUP BY sm.product_id, sl2.id, sm.company_id
        """
    )
    logger.info('Creating product stock locations based on all quants')

    cr.execute(
        """
        INSERT INTO product_stock_location(product_id, location_id,
        company_id)
        SELECT sq.product_id, sl2.id, sq.company_id
        FROM stock_quant AS sq
        INNER JOIN stock_location AS sl1
        ON sl1.id = sq.location_id
        INNER JOIN stock_location AS sl2
        ON sl2.parent_left <= sl1.parent_left
        AND sl2.parent_right >= sl1.parent_right
        WHERE NOT EXISTS (SELECT psl.id
        FROM product_stock_location AS psl
        WHERE psl.product_id = sq.product_id
        AND psl.location_id = sq.location_id
        AND psl.company_id = sq.company_id)
        AND sl2.id is not null
        GROUP BY sq.product_id, sl2.id, sq.company_id
        """
    )

    logger.info('Updating the parent relationships between '
                'product_stock_location records')

    cr.execute(
        """
        UPDATE product_stock_location AS psl1
        SET parent_id = psl2.id
        FROM product_stock_location AS psl2
        WHERE psl2.product_id = psl1.product_id
        AND psl2.location_id in (SELECT location_id FROM stock_location
        where id=psl1.location_id)
        """
    )

    logger.info('Updating stock moves')
    cr.execute(
        """
        UPDATE stock_move AS sm
        SET product_stock_location_id = psl.id
        FROM product_stock_location AS psl
        WHERE psl.product_id = sm.product_id
        AND psl.location_id = sm.location_id
        """
    )
    cr.execute(
        """
        UPDATE stock_move AS sm
        SET product_stock_location_dest_id = psl.id
        FROM product_stock_location AS psl
        WHERE psl.product_id = sm.product_id
        AND psl.location_id = sm.location_dest_id
        """
    )
    logger.info('Updating stock quants')
    cr.execute(
        """
        UPDATE stock_quant AS sq
        SET product_stock_location_id = psl.id
        FROM product_stock_location AS psl
        WHERE psl.product_id = sq.product_id
        AND psl.location_id = sq.location_id
        """
    )
