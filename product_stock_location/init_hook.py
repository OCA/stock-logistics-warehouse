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
            parent_id integer,
            product_location_qty float,
            incoming_location_qty float,
            outgoing_location_qty float,
            virtual_location_qty float)
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
        INSERT INTO product_stock_location(product_id, location_id)
        SELECT sm.product_id, sl2.id
        FROM stock_move AS sm
        INNER JOIN stock_location AS sl1
        ON sl1.id = sm.location_id
        INNER JOIN stock_location AS sl2
        ON sl2.parent_left <= sl1.parent_left
        AND sl2.parent_right >= sl1.parent_right
        GROUP BY sm.product_id, sl2.id
        """
    )

    cr.execute(
        """
        WITH Q1 AS (SELECT sm.product_id, sl2.id as location_id
        FROM stock_move AS sm
        INNER JOIN stock_location AS sl1
        ON sl1.id = sm.location_dest_id
        INNER JOIN stock_location AS sl2
        ON sl2.parent_left <= sl1.parent_left
        AND sl2.parent_right >= sl1.parent_right
        GROUP BY sm.product_id, sl2.id)

        INSERT INTO product_stock_location(product_id, location_id)
        SELECT product_id, location_id
        FROM Q1
        WHERE NOT EXISTS (SELECT id FROM product_stock_location
        WHERE product_id = Q1.product_id AND location_id = Q1.location_id)
        """
    )
    logger.info('Creating product stock locations based on all quants')

    cr.execute(
        """
        WITH Q1 AS (SELECT sm.product_id, sl2.id as location_id
        FROM stock_move AS sm
        INNER JOIN stock_location AS sl1
        ON sl1.id = sm.location_id
        INNER JOIN stock_location AS sl2
        ON sl2.parent_left <= sl1.parent_left
        AND sl2.parent_right >= sl1.parent_right
        GROUP BY sm.product_id, sl2.id)

        INSERT INTO product_stock_location(product_id, location_id)
        SELECT product_id, location_id
        FROM Q1
        WHERE NOT EXISTS (SELECT id FROM product_stock_location
        WHERE product_id = Q1.product_id AND location_id = Q1.location_id)
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

    logger.info('Updating product_location_qty and virtual_location_qty in '
                'product_stock_location')

    cr.execute("""
        WITH quant_query AS (
            SELECT psl2.id, sum(sq.qty) as quantity
            FROM product_stock_location as psl2
            INNER JOIN stock_quant as sq
            ON sq.product_id = psl2.product_id
            INNER JOIN stock_location as sl_sq
            ON sq.location_id = sl_sq.id
            INNER JOIN stock_location as sl_psl
            ON psl2.location_id = sl_psl.id
            WHERE sl_sq.parent_left >= sl_psl.parent_left
            AND sl_sq.parent_right <= sl_psl.parent_right
            GROUP BY psl2.id
        )

        UPDATE product_stock_location as psl1
        SET product_location_qty = qq.quantity,
        virtual_location_qty = qq.quantity
        FROM product_stock_location as psl2
        INNER JOIN quant_query AS qq
        ON qq.id = psl2.id
        WHERE psl1.id = psl2.id
    """)

    logger.info('Updating incoming_location_qty and virtual_location_qty in '
                'product_stock_location')
    cr.execute("""
        WITH in_move_query AS (
            SELECT psl2.id, sum(sm.product_qty) as quantity
            FROM product_stock_location as psl2
            INNER JOIN stock_move as sm
            ON sm.product_id = psl2.product_id
            INNER JOIN stock_location as sl_sm
            ON sm.location_dest_id = sl_sm.id
            INNER JOIN stock_location as sl_psl
            ON psl2.location_id = sl_psl.id
            WHERE sl_sm.parent_left >= sl_psl.parent_left
            AND sl_sm.parent_right <= sl_psl.parent_right
            AND sm.state NOT IN ('done', 'cancel', 'draft')
            GROUP BY psl2.id
        )

        UPDATE product_stock_location as psl1
        SET incoming_location_qty = qq.quantity,
        virtual_location_qty =
        coalesce(psl2.virtual_location_qty, 0) + qq.quantity
        FROM product_stock_location as psl2
        INNER JOIN in_move_query AS qq
        ON qq.id = psl2.id
        WHERE psl1.id = psl2.id
    """)

    logger.info('Updating outgoing_location_qty and virtual_location_qty in '
                'product_stock_location')
    cr.execute("""
        WITH out_move_query AS (
            SELECT psl2.id, sum(sm.product_qty) as quantity
            FROM product_stock_location as psl2
            INNER JOIN stock_move as sm
            ON sm.product_id = psl2.product_id
            INNER JOIN stock_location as sl_sm
            ON sm.location_id = sl_sm.id
            INNER JOIN stock_location as sl_psl
            ON psl2.location_id = sl_psl.id
            WHERE sl_sm.parent_left >= sl_psl.parent_left
            AND sl_sm.parent_right <= sl_psl.parent_right
            AND sm.state NOT IN ('done', 'cancel', 'draft')
            GROUP BY psl2.id
        )

        UPDATE product_stock_location as psl1
        SET outgoing_location_qty = qq.quantity,
        virtual_location_qty =
        coalesce(psl2.virtual_location_qty, 0) - qq.quantity
        FROM product_stock_location as psl2
        INNER JOIN out_move_query AS qq
        ON qq.id = psl2.id
        WHERE psl1.id = psl2.id
    """)
