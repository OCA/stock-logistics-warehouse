# Copyright 2016 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

from odoo import api, models

from odoo.addons.sale_automatic_workflow.models.automatic_workflow_job import savepoint

_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    @api.model
    def _get_domain_for_stock_reservation(self):
        return [
            ("state", "=", "draft"),
            ("is_stock_reservable", "=", True),
            ("has_stock_reservation", "=", False),
            ("workflow_process_id.validate_order", "=", False),
            ("workflow_process_id.stock_reservation", "=", True),
            ("workflow_process_id.stock_reservation_validity", ">=", 0),
        ]

    @api.model
    def _make_stock_reservation(self):
        sales = self.env["sale.order"].search(self._get_domain_for_stock_reservation())
        _logger.debug("Sales orders for which stock will be reserved: %s" % sales)
        today = datetime.now()
        for sale in sales:
            workflow_process = sale.workflow_process_id
            # Check that the date_order is set at least at n days
            # declared at workflow_process. Doing this, we are sure
            # that the reservation.validity_date will be at least
            # at today. If this wasn't like that, the cron of stock_reserve
            # will release this reservation.
            plus_days = timedelta(days=workflow_process.stock_reservation_validity)
            min_date_order = today - plus_days
            if sale.date_order <= min_date_order:
                continue
            ctx = dict(self.env.context)
            ctx.update(
                {
                    "active_model": "sale.order",
                    "active_id": sale.id,
                    "active_ids": sale.ids,
                }
            )
            with savepoint(self.env.cr):
                reservation_vals = {}
                if workflow_process.stock_reservation_validity:
                    reserve_until = today + plus_days
                    reservation_vals["date_validity"] = reserve_until
                if workflow_process.stock_reservation_location_id:
                    reservation_vals[
                        "location_id"
                    ] = workflow_process.stock_reservation_location_id.id
                if workflow_process.stock_reservation_location_dest_id:
                    reservation_vals[
                        "location_dest_id"
                    ] = workflow_process.stock_reservation_location_dest_id.id
                sale_stock_reserve = (
                    self.env["sale.stock.reserve"]
                    .with_context(ctx)
                    .create(reservation_vals)
                )
                line_ids = [line.id for line in sale.order_line]
                sale_stock_reserve.stock_reserve(line_ids)

    @api.model
    def run(self):
        res = super().run()
        self._make_stock_reservation()
        return res
