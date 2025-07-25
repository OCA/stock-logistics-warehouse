# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    if not column_exists(env.cr, "stock_move", "reservation_rate"):
        fields_spec = [
            (
                "reservation_rate",
                "stock.move",
                False,
                "float",
                "float",
                "stock_picking_reservation_rate",
                0.0,
            )
        ]
        openupgrade.add_fields(env, field_spec=fields_spec)

        # Update the rate
        query = """
            UPDATE stock_move
                SET reservation_rate = 100.0
                WHERE state = 'done'
        """
        openupgrade.logged_query(env.cr, query)

        query = """
            UPDATE stock_move
                SET reservation_rate = (
                    SELECT ((SUM(l.quantity)/ stock_move.product_uom_qty) * 100)
                        FROM stock_move_line l WHERE l.move_id = stock_move.id)
                WHERE state IN ('assigned', 'partially_available')
        """
        openupgrade.logged_query(env.cr, query)

        fields_spec = [
            (
                "reservation_rate",
                "stock.picking",
                False,
                "float",
                "float",
                "stock_picking_reservation_rate",
                0.0,
            )
        ]
        openupgrade.add_fields(env, field_spec=fields_spec)

        query = """
            UPDATE stock_picking
                SET reservation_rate = (
                    SELECT SUM(reservation_rate) / COUNT(id)
                        FROM stock_move WHERE picking_id = stock_picking.id)
                WHERE state IN ('done', 'assigned', 'partially_available')
        """
        openupgrade.logged_query(env.cr, query)
