# -*- coding: utf-8 -*-
# © 2012-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, datetime, timedelta
from openerp import api, fields, models
from openerp.tools import float_round, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.decimal_precision import get_precision


class ProductProduct(models.Model):

    _inherit = 'product.product'

    stock_period_max = fields.Integer(
        'Maximium days stock', help='Maximum stock in days turnover to '
        'resupply for. Used by the purchase proposal.')
    stock_period_min = fields.Integer(
        'Minimium days stock', help='Miminum stock in days turnover to '
        'resupply for. Used by the purchase proposal.')
    turnover_period = fields.Integer(
        string='Turnover period',
        help='Turnover days to calculate average '
        'turnover per day. Used by the purchase proposal.')
    turnover_average = fields.Float(
        'Turnover per day', digits=get_precision('Purchase Price'),
        readonly=True, help='Average turnover per day. Used by the purchase '
        'proposal.')
    ultimate_purchase = fields.Date(
        'Ultimate purchase', readonly=True, help='Ultimate date to purchase '
        'for not running out of stock. Used by the purchase proposal.')
    automatic_purchase_days = fields.Integer(
        "Trigger automatic purchase proposal on first supplier",
        default=0,
        help="Trigger an automatic RFQ on first (default supplier) if ultimate"
             "purchase is less than these days away"
    )
    is_buy = fields.Boolean("Does the product have Buy Route?",
                            compute='_compute_isbuy', store=True)

    @api.multi
    @api.depends('product_tmpl_id.route_ids')
    def _compute_isbuy(self):
        """
        Returns true if 'Buy' is amongst routes for this product
        """
        for this in self:
            prd_routes = this.product_tmpl_id.route_ids.ids
            buy_routes = this.product_tmpl_id._get_buy_route()
            this.is_buy = any(x in buy_routes for x in prd_routes)

    def has_purchase_draft(self):
        sql = """
            select count(id) from purchase_order_line
                where product_id = %s
                and order_id in (select id from purchase_order where
                state='draft')
            """
        self.env.cr.execute(sql, (self.id, ))
        return bool(self.env.cr.fetchone()[0])

    def _get_ultimate_purchase(
            self, stock_period_min, turnover_average):
        for this in self:
            stock_days = int(float_round((((
                this.virtual_available or 0
                ) - stock_period_min) / turnover_average) + .5, 0))
            if this.has_purchase_draft():
                return False
            if stock_days < 0:
                return fields.Date.to_string(
                    date.today())
            return fields.Date.to_string(
                date.today() + timedelta(days=stock_days))

    def _get_turnover_period(self):
        product_age = date.today() - datetime.strptime(
            self.create_date, DEFAULT_SERVER_DATETIME_FORMAT
        ).date()
        if not self.turnover_period:
            self.turnover_period = int(self.env['ir.config_parameter'].search(
                [('key', '=', 'default_turnover_period')])[0].value)
        if product_age.days < self.turnover_period:
            if product_age.days == 0:
                return 1
            return product_age.days
        return self.turnover_period

    @api.model
    def calc_purchase_date(self):
        # Defauts if not specified
        stock_per_min_default = self.env['ir.config_parameter'].search(
            [('key', '=', 'default_period_min')])[0].value
        stock_per_max_default = self.env['ir.config_parameter'].search(
            [('key', '=', 'default_period_max')])[0].value

        # calculate turnover_average over a certain period (turnover_period)
        # The turnover_period can be stored per product, supplier or
        # product category (in order of precedence).
        # The delivery and purchase period can be stored per supplier_info,
        # supplier or product category.
        # Defaults are codes in the cr.execute parameters.
        # One query retrieves turnover_average and stock_period_min per prd.
        # Each product is updated with turnover_average and ultimate_purchase
        # ( = now - stock_period_min + virtual stock / turnover_average).
        # In case the turnover period exceeds the products age the latter
        # defaults
        # The WITH clause determines the parameters per product.
        # The final SELECT calculates turnover and detects procurements.
        # Called by cronjob every day.

        sql = """
            WITH TP AS
                (SELECT
                    PP.id AS product_id,
                    COALESCE(
                            NULLIF(PS.stock_period_min, 0),
                            NULLIF(RP.stock_period_min, 0),
                            NULLIF(PC.stock_period_min, 0),
                            %s
                           )
                    AS stock_period_min,
                    COALESCE(
                            NULLIF(PP.stock_period_max, 0),
                            NULLIF(RP.stock_period_max, 0),
                            NULLIF(PC.stock_period_max, 0),
                            %s
                    )
                    AS stock_period_max
                FROM product_product PP
                JOIN product_template PT ON PP.product_tmpl_id = PT.id
                LEFT JOIN product_supplierinfo PS
                ON PS.product_tmpl_id = PP.product_tmpl_id
                LEFT JOIN res_partner RP ON RP.id = PS.name AND RP.active
                LEFT JOIN product_category PC ON PC.id = PT.categ_id
                WHERE PP.active
                )
            SELECT
                TP.product_id AS id,
                MAX(TP.stock_period_min) AS stock_period_min,
                MAX(TP.stock_period_max) AS stock_period_max
        FROM TP
            GROUP BY TP.product_id
        """
        self.env.cr.execute(
            sql,
            (
                stock_per_min_default,
                stock_per_max_default,
            )
        )
        sqlresult = self.env.cr.fetchall()
        for product_id, stock_period_min, stock_period_max in sqlresult:
            this = self.env['product.product'].browse(product_id)
            turnover_period = this._get_turnover_period()
            # turnover_period may be 0 for new products
            if turnover_period == 0:
                turnover_period = 1
            sales = self.env['sale.order'].search([(
                'date_order',
                '>=',
                date.strftime(
                    date.today() - timedelta(days=turnover_period),
                    DEFAULT_SERVER_DATE_FORMAT
                 )
            )])
            line_qty = self.env['sale.order.line'].search(
                [
                    ('product_id', '=', product_id),
                    ('state', 'not in', ['draft', 'cancel', 'sent']),
                    ('order_id', 'in', sales.ids)
                ]).mapped('product_uom_qty')
            turnover_average = float_round(
                sum(line_qty)/turnover_period,
                self._fields['turnover_average'].digits[1]
            )
            if turnover_average != 0.0 and this.is_buy:
                up_val = this._get_ultimate_purchase(
                    stock_period_min, turnover_average
                )
                values = {
                    'turnover_average': turnover_average,
                    'ultimate_purchase': up_val,
                    'stock_period_max': stock_period_max,
                    'stock_period_min': stock_period_min,
                }
            else:  # remove data when supply method no longer = "buy"
                values = {
                    'turnover_average': 0,
                    'ultimate_purchase': False,
                }
            this.write(values)
        return True
