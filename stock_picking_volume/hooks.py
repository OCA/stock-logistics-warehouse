# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Pre init create volume column on stock.picking and stock.move"""
    if not column_exists(cr, "stock_move", "volume"):
        create_column(cr, "stock_move", "volume", "double precision")
        # First we compute the reserved qty by move_id
        # the reserved qty is the sum of the reserved qty of the move lines
        # linked to the move
        # Then we update the volume of the moves not in state done or cancel
        # If the move is in state partially available, or assigned, the volume
        # is the reserved qty * the product volume
        # else the volume is the move quantity * the product volume
        cr.execute(
            """
            with reserved_qty_by_move as (
                select
                    move_id,
                    product_id,
                    sum(product_qty) as product_qty
                from stock_move_line
                group by move_id, product_id
            )
            update stock_move
                set volume =
                    CASE
                        WHEN stock_move.state in ('partially_available', 'assigned') THEN
                            reserved_qty_by_move.product_qty * pp.volume
                        ELSE
                            stock_move.product_uom_qty * pp.volume
                    END
            from reserved_qty_by_move
            join product_product pp on pp.id = reserved_qty_by_move.product_id
            where
                stock_move.id = reserved_qty_by_move.move_id
                and stock_move.state not in ('done', 'cancel')
            """
        )
        _logger.info(f"{cr.rowcount} rows updated in stock_move")

    if not column_exists(cr, "stock_picking", "volume"):
        create_column(cr, "stock_picking", "volume", "double precision")
        # we recompute the volume of the pickings not in state done or cancel
        # the volume is the sum of the volume of the moves linked to the picking
        # that are not in state done or cancel
        cr.execute(
            """
            update stock_picking
                set volume = (
                    select sum(volume)
                    from stock_move
                    where
                        stock_move.picking_id = stock_picking.id
                        and state not in ('done', 'cancel')
                )
            where state not in ('done', 'cancel')
            """
        )
        _logger.info(f"{cr.rowcount} rows updated in stock_picking")
