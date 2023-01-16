# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import SUPERUSER_ID, api

logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    The objective of this hook is to link existing MOs
    coming from a Stock Request.
    """
    logger.info("Linking existing MOs coming from a Stock Request")
    link_existing_mos_to_stock_request(cr)


def link_existing_mos_to_stock_request(cr):
    env = api.Environment(cr, SUPERUSER_ID, dict())
    stock_request_obj = env["stock.request"]
    stock_request_order_obj = env["stock.request.order"]
    stock_request_allocation_obj = env["stock.request.allocation"]
    mrp_production_obj = env["mrp.production"]
    mos_with_sr = mrp_production_obj.search([("origin", "ilike", "SR/%")])
    logger.info("Linking %s MOs records" % len(mos_with_sr))
    stock_requests = stock_request_obj.search(
        [("name", "in", [mo.origin for mo in mos_with_sr])]
    )
    for mo in mos_with_sr:
        stock_request = stock_requests.filtered(lambda x: x.name == mo.origin)
        if stock_request:
            # Link SR to MO
            mo.stock_request_ids = [(6, 0, stock_request.ids)]
            logger.info("MO {} linked to SR {}".format(mo.name, stock_request.name))
            if (
                not stock_request_allocation_obj.search(
                    [("stock_request_id", "=", stock_request.id)]
                )
                and mo.state != "cancel"
            ):
                # Create allocation for finish move
                logger.info("Create allocation for {}".format(stock_request.name))
                mo.move_finished_ids[0].allocation_ids = [
                    (
                        0,
                        0,
                        {
                            "stock_request_id": request.id,
                            "requested_product_uom_qty": request.product_qty,
                        },
                    )
                    for request in mo.stock_request_ids
                ]

            # Update allocations
            logger.info("Updating Allocations for SR %s" % stock_request.name)
            for ml in mo.finished_move_line_ids.filtered(
                lambda m: m.exists() and m.move_id.allocation_ids
            ):
                qty_done = ml.product_uom_id._compute_quantity(
                    ml.qty_done, ml.product_id.uom_id
                )
                to_allocate_qty = ml.qty_done
                for allocation in ml.move_id.allocation_ids:
                    if allocation.open_product_qty:
                        allocated_qty = min(allocation.open_product_qty, qty_done)
                        allocation.allocated_product_qty += allocated_qty
                        to_allocate_qty -= allocated_qty
            stock_request.check_done()
    # Update production_ids from SROs
    stock_request_order_obj.search([])._compute_production_ids()
