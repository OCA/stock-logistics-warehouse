# -*- coding: utf-8 -*-
# © 2016 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime, timedelta
from openerp import models, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.addons.sale_automatic_workflow.automatic_workflow_job import \
    commit

_logger = logging.getLogger(__name__)


class AutomaticWorkflowJob(models.Model):

    _inherit = 'automatic.workflow.job'

    @api.model
    def _get_domain_for_stock_reservation(self):
        return [('state', '=', 'draft'),
                ('is_stock_reservable', '=', True),
                ('has_stock_reservation', '=', False),
                ('workflow_process_id.validate_order', '=', False),
                ('workflow_process_id.stock_reservation', '=', True),
                ('workflow_process_id.stock_reservation_validity', '>=', 0)]

    @api.model
    def _make_stock_reservation(self):
        sale_env = self.env['sale.order']
        sale_stock_reserve_env = self.env['sale.stock.reserve']
        sales = sale_env.search(self._get_domain_for_stock_reservation())
        _logger.debug('Sale Orders for what the stock will be reserved: %s' %
                      sales)
        today = datetime.now()
        for sale in sales:
            workflow_process = sale.workflow_process_id
            plus_days = timedelta(
                days=workflow_process.stock_reservation_validity)
            min_date_order = (today.date() - plus_days).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
            # Check reservation date
            if sale.date_order <= min_date_order:
                continue
            ctx = dict(self.env.context)
            ctx.update({
                'active_model': 'sale.order',
                'active_id': sale.id,
                'active_ids': [sale.id]
            })
            with commit(self.env.cr):
                reservation_vals = {}
                if workflow_process.stock_reservation_validity:
                    reserve_until = today + plus_days
                    reservation_vals['date_validity'] =\
                        reserve_until.strftime(DEFAULT_SERVER_DATE_FORMAT)
                if workflow_process.stock_reservation_location_id:
                    reservation_vals['location_id'] =\
                        workflow_process.stock_reservation_location_id.id
                if workflow_process.stock_reservation_location_dest_id:
                    reservation_vals['location_dest_id'] =\
                        workflow_process.stock_reservation_location_dest_id.id
                sale_stock_reserve = sale_stock_reserve_env.with_context(ctx)\
                    .create(reservation_vals)
                line_ids = [line.id for line in sale.order_line]
                sale_stock_reserve.stock_reserve(line_ids)

    @api.model
    def run(self):
        res = super(AutomaticWorkflowJob, self).run()
        self._make_stock_reservation()
        return res
