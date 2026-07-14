# Copyright 2024 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def set_initial_last_inventory_date(cr):
    cr.execute(
        """
    Update
        stock_location
    set
        last_inventory_date = sub.date
    from (
        Select
            line.location_id,
            max(inventory.date) as date
        from
            stock_inventory_line as line
        join
            stock_inventory as inventory
        on
            inventory.id = line.inventory_id
        group by
            line.location_id
    ) as sub
    where
        stock_location.id = sub.location_id;
    """
    )


def set_inventory_date_on_child_location(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    inventories = env["stock.inventory"].search([("state", "=", "done")])

    for inv in inventories:
        done_locations = inv._get_all_inventory_locations()
        last_inventory_date = inv.date
        for loc in done_locations:
            if (
                not loc.last_inventory_date
                or loc.last_inventory_date < last_inventory_date
            ):
                loc.write({"last_inventory_date": last_inventory_date})


def post_init_hook(cr, registry):
    logger.info("Calculate last inventory date for locations")
    set_initial_last_inventory_date(cr)
    set_inventory_date_on_child_location(cr)
