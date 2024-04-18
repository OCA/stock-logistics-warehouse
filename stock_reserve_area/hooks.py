# Copyright 2023 ForgeFlow SL.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists, table_exists

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    if not column_exists(cr, "stock_move", "area_reserved_availability"):
        cr.execute(
            """
                ALTER TABLE "stock_move"
                ADD COLUMN "area_reserved_availability" double precision DEFAULT 0
            """
        )
        cr.execute(
            """
        ALTER TABLE "stock_move" ALTER COLUMN "area_reserved_availability" DROP DEFAULT
        """
        )

    if not table_exists(cr, "stock_move_stock_reserve_area_rel"):
        cr.execute(
            """
        CREATE TABLE stock_move_stock_reserve_area_rel
        (stock_move_id INTEGER, stock_reserve_area_id INTEGER);
        """
        )


def assign_reserve_area_ids_to_stock_move_query(cr):
    query = """
        INSERT INTO stock_move_stock_reserve_area_rel (stock_move_id, stock_reserve_area_id)
        SELECT DISTINCT sm.id AS stock_move_id, srl.reserve_area_id AS stock_reserve_area_id
        FROM stock_move sm
        JOIN stock_location sl ON sm.location_id = sl.id
        JOIN stock_reserve_area_stock_location_rel srl ON sl.id = srl.location_id
        WHERE NOT EXISTS (
        SELECT 1
        FROM stock_move_stock_reserve_area_rel existing_rel
        WHERE existing_rel.stock_move_id = sm.id
        AND existing_rel.stock_reserve_area_id = srl.reserve_area_id
        );
    """
    cr.execute(query)


def create_reservation_data(cr):
    cr.execute(
        """
insert into stock_move_reserve_area_line
  (
  create_uid,
  create_date,
  move_id,
  product_id,
  reserve_area_id,
  reserved_availability
  )

select
  1 as create_uid,
  current_timestamp as create_date,
  sm.id as move_id,
  sm.product_id as product_id,
  rel.stock_reserve_area_id as reserve_area_id,
  coalesce(sum(sml.reserved_uom_qty), 0) as reserved_availability
from stock_move as sm
inner join stock_move_stock_reserve_area_rel as rel on rel.stock_move_id = sm.id
left join stock_move_line as sml on sml.move_id = sm.id
where sm.state in ('assigned', 'partially_assigned')
and sm.id not in (
  select move_id from stock_move_reserve_area_line group by move_id
)
and sm.location_dest_id not in (
    select location_id from stock_reserve_area_stock_location_rel
    where reserve_area_id = rel.stock_reserve_area_id
    )
group by sm.id, rel.stock_reserve_area_id, sm.picking_id, sm.product_id
having coalesce(sum(sml.reserved_uom_qty), 0) > 0
"""
    )

    cr.execute(
        """
update stock_move as sm set area_reserved_availability = q.reserved_availability
from (
  select move_id, min(reserved_availability) as reserved_availability
  from stock_move_reserve_area_line
  group by move_id
  ) as q
where q.move_id = sm.id
    """
    )


def post_init_hook(cr, registry):
    """
    This post-init-hook will create a Reserve Area for each existing WH.
    """
    _logger.info("Starting Post Init Hook")

    env = api.Environment(cr, SUPERUSER_ID, dict())
    warehouse_obj = env["stock.warehouse"]
    warehouses = warehouse_obj.search([])
    reserve_area_obj = env["stock.reserve.area"]
    _logger.info("Creating a Reserve Area for each WH")
    for warehouse_id in warehouses.ids:
        warehouse = warehouse_obj.browse(warehouse_id)

        all_locations = env["stock.location"].search(
            [("id", "child_of", warehouse.view_location_id.id)]
        )

        reserve_area_obj.with_context(init_hook=True).create(
            {
                "name": warehouse.name,
                "location_ids": [(6, 0, all_locations.ids)],
                "company_id": warehouse.company_id.id,
            }
        )

    _logger.info("Starting assign_reserve_area_ids_to_stock_move_query")

    assign_reserve_area_ids_to_stock_move_query(cr)

    _logger.info("Create reservation data for current moves")
    create_reservation_data(cr)
