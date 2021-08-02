#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from datetime import date, time
from datetime import datetime as dt
from datetime import timedelta as td

from dateutil.relativedelta import relativedelta as rd
from odoo import models, fields, api
from odoo.addons.queue_job.job import job

import logging
_logger = logging.getLogger(__name__)

DAYS_IN_RANGE = {
    'days': 1,
    'weeks': 7,
    'months': 30,
}

NUMBER_OF_PRODUCTS_PER_JOB = 50


class ProductProduct(models.Model):
    _inherit = "product.product"

    # these computed fields are defined in product_average_consumption;
    # with product_history installed, we take the assumption that all products
    # will use it (consumption_calculation_method = 'history')
    # so we can store these fields, and we explicitly recompute them after
    # the creation of product.history records, by _compute_history()
    # (see data/cron.xml)
    average_consumption = fields.Float(store=True)
    displayed_average_consumption = fields.Float(store=True)
    total_consumption = fields.Float(store=True)
    nb_days = fields.Integer(store=True)

    product_tmpl_id = fields.Many2one(comodel_name='product.template')
    history_range = fields.Selection(
        related="product_tmpl_id.history_range",
        readonly=True,
    )
    product_history_ids = fields.Many2many(
        comodel_name='product.history',
        inverse_name='product_id',
        string='History',
        compute="_compute_product_history_ids",
    )
    number_of_periods_real = fields.Integer(
        'Number of History Periods',
        help="Number of valid history periods used for the calculation",
    )
    number_of_periods_target = fields.Integer(
        string='Number of History Periods (Target)',
        related='product_tmpl_id.number_of_periods',
    )
    last_history_day = fields.Many2one(
        comodel_name='product.history',
        string='Last day history record',
    )
    last_history_week = fields.Many2one(
        comodel_name='product.history',
        string='Last week history record',
    )
    last_history_month = fields.Many2one(
        comodel_name='product.history',
        string='Last month history record',
    )

    # Private section
    @api.depends(
        'history_range', 'product_history_ids', 'number_of_periods_target')
    @api.multi
    def _compute_average_consumption(self):
        for product in self:
            if product.consumption_calculation_method == 'history':
                product._average_consumption_history()
        super(ProductProduct, self)._compute_average_consumption()

    @api.depends('history_range')
    @api.multi
    def _compute_product_history_ids(self):
        for product in self:
            ph_ids = self.env['product.history'].search([
                ('product_id', '=', product.id),
                ('history_range', '=', product.history_range)])
            ph_ids = [ph.id for ph in ph_ids]
            product.product_history_ids = [(6, 0, ph_ids)]

    @api.multi
    def _compute_qtys(self, states=('done',)):
        domain = [('state', 'in', states)] + self._get_domain_dates()
        for product in self:
            domain_product = domain + [('product_id', '=', product.id)]
            res = {
                'purchase_qty': 0,
                'view_qty': 0,
                'sale_qty': 0,
                'inventory_qty': 0,
                'procurement_qty': 0,
                'production_qty': 0,
                'transit_qty': 0,
                'total_qty': 0, }
            move_pool = self.env['stock.move']

            for field, usage, sign in (
                    ('purchase_qty', 'supplier', 1),
                    ('sale_qty', 'customer', 1),
                    ('inventory_qty', 'inventory', 1),
                    ('procurement_qty', 'procurement', 1),
                    ('production_qty', 'production', 1),
                    ('transit_qty', 'transit', 1),
            ):
                moves = move_pool.read_group(domain_product + [
                    ('location_id.usage', '=', usage),
                    ('location_dest_id.usage', '=', 'internal'),
                ], ['product_qty'], [])
                for move in moves:
                    res[field] = sign * (move['product_qty'] or 0)
                    res['total_qty'] += sign * (move['product_qty'] or 0)
                moves = move_pool.read_group(domain_product + [
                    ('location_dest_id.usage', '=', usage),
                    ('location_id.usage', '=', 'internal'),
                ], ['product_qty'], [])
                for move in moves:
                    res[field] -= sign * (move['product_qty'] or 0)
                    res['total_qty'] -= sign * (move['product_qty'] or 0)
            return res

    @api.multi
    def _average_consumption_history(self):
        for product in self:
            nb = product.number_of_periods_target
            history_range = product.history_range
            history_ids = self.env['product.history'].search([
                ('product_id', '=', product.id),
                ('history_range', '=', history_range),
                ('ignored', '=', 0)]).sorted()
            nb = min(len(history_ids), nb)
            if nb == 0:
                product.total_consumption = 0
                product.average_consumption = 0
                product.number_of_periods_real = 0
            else:
                list_indexes = list(range(nb))
                total_consumption = 0
                for index in list_indexes:
                    total_consumption -= history_ids[index].sale_qty
                product.total_consumption = total_consumption
                product.average_consumption = \
                    total_consumption/nb/DAYS_IN_RANGE[product.history_range]
                product.number_of_periods_real = nb
                self._compute_displayed_average_consumption()

    # Action section
    @api.model
    def _get_products_multiple_parts(self):
        """ Gets the list of products to process, splitted in chunks """
        Product = self.env['product.product'].with_context(active_test=False)
        product_ids = Product._search([])
        # Split in chunks
        chunked = [
            product_ids[i: i + NUMBER_OF_PRODUCTS_PER_JOB]
            for i in range(0, len(product_ids), NUMBER_OF_PRODUCTS_PER_JOB)
        ]
        return chunked

    @api.model
    def _create_job_compute_history(self, history_range):
        """ Creates the jobs to recompute history """
        product_chunks = self._get_products_multiple_parts()
        for chunk in product_chunks:
            self.with_delay().job_compute_history(history_range, chunk)

    @api.model
    def run_product_history_day(self):
        # This method is called by the cron task
        self._create_job_compute_history('days')

    @api.model
    def run_product_history_week(self):
        # This method is called by the cron task
        self._create_job_compute_history('weeks')

    @api.model
    def run_product_history_month(self):
        # This method is called by the cron task
        self._create_job_compute_history('months')

    @api.model
    def run_product_average_consumption(self):
        product_chunks = self._get_products_multiple_parts()
        for chunk in product_chunks:
            self.with_delay().job_compute_average_consumption(chunk)

    @api.model
    def run_recompute_6weeks_product_history(self):
        # This method is called by the cron task
        product_chunks = self._get_products_multiple_parts()
        for chunk in product_chunks:
            self.with_delay().job_recompute_last_6weeks_history('weeks', chunk)

    @api.model
    def init_history(self):
        products = self.env['product.product'].with_context(
            active_test=False).search([])
        products._compute_history('months')
        products._compute_history('weeks')
        products._compute_history('days')

    @api.multi
    def _compute_history(self, history_range):
        to_date = date.today()
        if history_range == "months":
            delta = rd(months=1)
        elif history_range == "weeks":
            delta = rd(weeks=1)
        else:
            delta = rd(days=1)
        last_dates = {}
        last_qtys = {}
        product_ids = []
        for product in self:
            _logger.debug(
                "Computing '%s' history for product: %s",
                history_range,
                product,
            )
            product_ids.append(product.id)
            history_ids = self.env['product.history'].search([
                ('history_range', '=', history_range),
                ('product_id', '=', product.id)])
            if history_ids:
                self.env.cr.execute("""
                    SELECT to_date, end_qty FROM product_history
                    WHERE product_id = %s
                    AND history_range = %s
                    ORDER BY "id" DESC LIMIT 1
                """, (product.id, history_range))
                last_record = self.env.cr.fetchone()
                last_date = last_record and last_record[0]
                last_qty = last_record and last_record[1] or 0
                from_date = last_date + td(days=1)
            else:
                self.env.cr.execute("""
                    SELECT date FROM stock_move
                    WHERE product_id = %s
                    ORDER BY "date" LIMIT 1
                """, (product.id, ))
                fetch = self.env.cr.fetchone()
                from_date = fetch and fetch[0].date() or to_date
                if history_range == "months":
                    from_date = date(
                        from_date.year, from_date.month, 1)
                elif history_range == "weeks":
                    from_date = from_date - td(days=from_date.weekday())
                last_qty = 0
            last_dates[product.id] = from_date
            last_qtys[product.id] = last_qty

        product_ids.sort()
        if not last_dates:
            return False
        last_date = min(last_dates.values())

        sql = """
            SELECT
                MIN(sm.id),
                sm.product_id,
                DATE_TRUNC('day', sm.date),
                sm.state,
                SUM(sm.product_qty) AS product_qty,
                orig.usage,
                dest.usage
            FROM stock_move AS sm,
                 stock_location AS orig,
                 stock_location AS dest
            WHERE
                sm.location_id = orig.id
                AND sm.location_dest_id = dest.id
                AND sm.product_id in %s
                AND sm.date >= %s
                AND sm.state != 'cancel'
            GROUP BY
                sm.product_id,
                DATE_TRUNC('day', sm.date),
                sm.state,
                orig.usage,
                dest.usage
            ORDER BY
                sm.product_id,
                DATE_TRUNC('day', sm.date)
        """
        params = (tuple(product_ids), fields.Datetime.to_string(last_date))
        self.env.cr.execute(sql, params)
        stock_moves = self.env.cr.fetchall()

        for product_id in product_ids:
            stock_moves_product = []

            while len(stock_moves):
                if stock_moves[0][1] == product_id:
                    stock_moves_product.append(stock_moves.pop(0))
                else:
                    break

            if not stock_moves_product:
                continue

            product = self.env['product.product'].browse(product_id)
            from_date = last_dates.get(product_id)
            last_qty = last_qtys.get(product_id, 0)
            history_id = False

            while from_date + delta <= to_date:
                stock_moves_product_dates = []
                start_qty = last_qty
                last_date = from_date + delta - td(days=1)
                purchase_qty = sale_qty = loss_qty = 0
                incoming_qty = outgoing_qty = 0

                i_move = 0
                while i_move < len(stock_moves_product):
                    if stock_moves_product[i_move][2].date() >= from_date and \
                            stock_moves_product[i_move][2].date() <= last_date:
                        stock_moves_product_dates.append(
                            stock_moves_product.pop(i_move))
                    else:
                        i_move += 1

                for move in stock_moves_product_dates:
                    if move[3] == 'done':
                        if move[5] == 'internal':
                            if move[6] == 'supplier':
                                purchase_qty -= move[4]
                            elif move[6] == 'customer':
                                sale_qty -= move[4]
                            elif move[6] == 'inventory':
                                loss_qty -= move[4]
                        elif move[6] == 'internal':
                            if move[5] == 'supplier':
                                purchase_qty += move[4]
                            elif move[5] == 'customer':
                                sale_qty += move[4]
                            elif move[5] == 'inventory':
                                loss_qty += move[4]
                    else:
                        if move[5] == 'internal':
                            if move[6] == 'supplier':
                                incoming_qty -= move[4]
                            elif move[6] == 'customer':
                                outgoing_qty -= move[4]
                            elif move[6] == 'inventory':
                                outgoing_qty -= move[4]
                        elif move[6] == 'internal':
                            if move[5] == 'supplier':
                                incoming_qty += move[4]
                            elif move[5] == 'customer':
                                outgoing_qty += move[4]
                            elif move[5] == 'inventory':
                                outgoing_qty += move[4]

                last_qty = start_qty + purchase_qty + sale_qty + loss_qty

                vals = {
                    'product_id': product_id,
                    'product_tmpl_id': product.product_tmpl_id.id,
                    'location_id': self.env['stock.location'].search([])[0].id,
                    'from_date': dt.strftime(from_date, "%Y-%m-%d"),
                    'to_date': dt.strftime(last_date, "%Y-%m-%d"),
                    'purchase_qty': purchase_qty,
                    'sale_qty': sale_qty,
                    'loss_qty': loss_qty,
                    'start_qty': start_qty,
                    'end_qty': last_qty,
                    'virtual_qty': last_qty + incoming_qty + outgoing_qty,
                    'incoming_qty': incoming_qty,
                    'outgoing_qty': outgoing_qty,
                    'history_range': history_range,
                }
                history_id = self.env['product.history'].create(vals)
                from_date = last_date + td(days=1)

            if history_id:
                if history_range == "months":
                    product.last_history_month = history_id.id
                elif history_range == "weeks":
                    product.last_history_week = history_id.id
                else:
                    product.last_history_day = history_id.id
                product._compute_average_consumption()

    @api.multi
    def recompute_last_6weeks_history(self):
        for product in self:
            history_ids = self.env['product.history'].search([
                ('history_range', '=', 'weeks'),
                ('product_id', '=', product.id)
            ], order="id desc", limit=7)
            if history_ids:
                last_6weeks_histories = history_ids[:6]
                past_7th_history = history_ids[-1]
                # Remove the last 6 weeks histories
                last_6weeks_histories.unlink()

                if len(history_ids) == 7:
                    to_date = past_7th_history.to_date
                    to_date_dt = fields.Date.from_string(to_date)
                    ending_qty = product.get_stock_inventory_at(
                        to_date_dt).get(product.id, 0)
                    past_7th_history.write(dict(end_qty=ending_qty))

    @api.multi
    def get_stock_inventory_at(self, at_date=False):
        values = {}
        if not at_date:
            at_date = fields.Datetime.now()
        # Convert to str
        if isinstance(at_date, date):
            at_date = dt.combine(at_date, time(23, 59, 59))
        elif isinstance(at_date, dt):
            at_date = fields.Datetime.to_string(at_date)

        query = """
            SELECT
                product_id,
                sum(quantity) AS quantity
            FROM
            (
                (
                    SELECT
                        sum(quant.qty) AS quantity,
                        stock_move.product_id AS product_id
                    FROM stock_quant AS quant
                    JOIN stock_quant_move_rel
                        ON stock_quant_move_rel.quant_id = quant.id
                    JOIN stock_move
                        ON stock_move.id = stock_quant_move_rel.move_id
                    JOIN stock_location dest_location
                        ON stock_move.location_dest_id = dest_location.id
                    JOIN stock_location source_location
                        ON stock_move.location_id = source_location.id
                    WHERE
                        quant.qty > 0
                        AND stock_move.state = 'done'
                        AND dest_location.usage IN ( 'internal', 'transit' )
                        AND (
                            NOT (
                                source_location.company_id IS NULL
                                AND dest_location.company_id IS NULL
                            )
                            OR source_location.company_id !=
                                dest_location.company_id
                            OR source_location.usage NOT IN
                                ( 'internal', 'transit' )
                        )
                        AND stock_move.date <= %s
                        AND stock_move.product_id = %s
                    GROUP BY stock_move.product_id

                ) UNION ALL (

                    SELECT
                        sum(-quant.qty) AS quantity,
                        stock_move.product_id AS product_id
                    FROM stock_quant AS quant
                    JOIN stock_quant_move_rel
                        ON stock_quant_move_rel.quant_id = quant.id
                    JOIN stock_move
                        ON stock_move.id = stock_quant_move_rel.move_id
                    JOIN stock_location source_location
                        ON stock_move.location_id = source_location.id
                    JOIN stock_location dest_location
                        ON stock_move.location_dest_id = dest_location.id
                    WHERE
                        quant.qty > 0
                        AND stock_move.state = 'done'
                        AND source_location.usage IN ( 'internal', 'transit' )
                        AND (
                            NOT (
                                dest_location.company_id IS NULL
                                AND source_location.company_id IS NULL
                            )
                            OR dest_location.company_id !=
                                source_location.company_id
                            OR dest_location.usage NOT IN
                                ( 'internal', 'transit' )
                        )
                        AND stock_move.date <= %s
                        AND stock_move.product_id = %s
                    GROUP BY stock_move.product_id
                )
            ) AS foo
            GROUP BY product_id
        """
        for product in self:
            product.env.cr.execute(
                query, (at_date, product.id, at_date, product.id))
            result = product.env.cr.fetchall()
            values[product.id] = result and result[0][1] or 0
        return values

    @job
    def job_compute_history(self, history_range, product_ids):
        """ Job for Computing Product History """
        products = self.browse(product_ids)
        products._compute_history(history_range)

    @job
    def job_compute_average_consumption(self, product_ids):
        """ Job for Computing Average Consumption """
        products = self.browse(product_ids)
        products._compute_average_consumption()

    @job
    def job_recompute_last_6weeks_history(self, history_range, product_ids):
        """ Job for Recompute the last 6 weeks Product History """
        products = self.browse(product_ids)
        products.recompute_last_6weeks_history()
