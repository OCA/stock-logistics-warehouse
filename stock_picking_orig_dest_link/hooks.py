# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api
from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info(
        "Create temporary table to avoid the automatic launch of the compute method"
    )
    if not sql.table_exists(cr, "stock_picking_orig_dest_rel"):
        cr.execute("CREATE TABLE stock_picking_orig_dest_rel (temp INTEGER)")


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Dropping temporary table")
    cr.execute("DROP TABLE stock_picking_orig_dest_rel")
    _logger.info("Creating new table via ORM")
    StockPicking = env["stock.picking"]
    StockPicking._fields["orig_picking_ids"].update_db(StockPicking, False)
    StockPicking._fields["dest_picking_ids"].update_db(StockPicking, False)
    _logger.info("Filling Origin and Destination Picking relation table")
    query = """
        WITH query AS (
            SELECT spo.id AS orig_picking_id, spd.id AS dest_picking_id
            FROM stock_move_move_rel smml
                JOIN stock_move smo ON smo.id = smml.move_orig_id
                JOIN stock_move smd ON smd.id = smml.move_dest_id
                JOIN stock_picking spo ON smo.picking_id = spo.id
                JOIN stock_picking spd ON smd.picking_id = spd.id
            GROUP BY spo.id, spd.id
        )
        INSERT INTO stock_picking_orig_dest_rel (orig_picking_id, dest_picking_id)
        SELECT * FROM query;
    """
    cr.execute(query)
