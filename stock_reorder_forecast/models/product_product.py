# -*- coding: utf-8 -*-
# © 2012-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta
from openerp import api, fields, models
from openerp.tools import float_round
from openerp.addons.decimal_precision import get_precision


class ProductProduct(models.Model):

    _inherit = 'product.product'

    stock_period_max = fields.Integer(
        'Maximium stock', help='Maximum stock in days turnover to resupply '
        'for. Used by the purchase proposal.')
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
        if self.turnover_period:
            return self.turnover_period
        # TODO IMPLEMENT SELLER RULES IN FUNCTION _select_seller
        for seller in self.product_tmpl_id.seller_ids:
            if seller.name.turnover_period:
                return seller.name.turnover_period
        if self.product_tmpl_id.categ_id.turnover_period:
            return self.product_tmpl_id.categ_id.turnover_period
        return int(self.env['ir.config_parameter'].search(
            [('key', '=', 'default_turnover_period')])[0].value)

    @api.model
    def calc_purchase_date(self):
        # Defauts if not specified
        tp_default = self.env['ir.config_parameter'].search(
            [('key', '=', 'default_turnover_period')])[0].value
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
                    EXTRACT(
                        EPOCH FROM AGE(DATE(NOW()
                        ),
                        DATE(PP.create_date))
                        )/(24*60*60)
                        AS prod_age,
                    COALESCE(
                            NULLIF(PP.turnover_period, 0),
                            NULLIF(RP.turnover_period, 0),
                            NULLIF(PC.turnover_period, 0),
                            %s
                            )
                    AS turnover_period,
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
                FROM product_template PT
                JOIN product_product PP ON PP.product_tmpl_id = PT.id
                LEFT JOIN product_supplierinfo PS
                ON PS.product_id = PP.id
                LEFT JOIN res_partner RP ON RP.id = PS.name AND RP.active
                LEFT JOIN product_category PC ON PC.id = PT.categ_id
                WHERE PP.active
                AND (PP.id in
                        (select product_id from procurement_order
                            where rule_id in
                            (select id from procurement_rule where
                                procure_method in
                                ('make_to_stock','make_to_order')
                                AND (
                                picking_type_id in
                                    ( select id from stock_picking_type
                                        where code='outgoing'
                                    )
                                )
                            )
                        ) OR NOT PP.ultimate_purchase IS NULL)
                )
            SELECT
                TP.product_id AS id,
                MAX(TP.stock_period_min) AS stock_period_min,
                COALESCE(
                    SUM(SOL.product_uom_qty), 0) /
                    MAX(CASE WHEN TP.turnover_period < TP.prod_age
                        THEN TP.turnover_period
                    WHEN TP.prod_age > TP.turnover_period THEN TP.prod_age
                    ELSE 1 END)
                        AS turnover_average,
                    MAX(TP.stock_period_max) AS stock_period_max
            FROM TP
            LEFT JOIN sale_order_line SOL on SOL.product_id = TP.product_id
            AND SOL.product_id in
                        (select product_id from procurement_order  where
                            rule_id in
                                (select id from procurement_rule where
                                    procure_method='make_to_stock'
                                )
                        )
            AND NOT state IN ('draft', 'cancel')
            and SOL.order_id in
                (
                    select id from sale_order where DATE(create_date) >
                    (DATE(now()) - TP.turnover_period)
                )
            AND DATE(SOL.create_date) BETWEEN DATE(NOW()) - CAST(
            CASE WHEN TP.turnover_period < TP.prod_age THEN TP.turnover_period
            WHEN
            TP.prod_age > 1 THEN TP.prod_age ELSE 1 END AS INTEGER)
            AND DATE(NOW())
            GROUP BY TP.product_id
        """
        self.env.cr.execute(sql, (
            tp_default,
            stock_per_min_default,
            stock_per_max_default,
            ))
        sqlresult = self.env.cr.fetchall()
        for product_id, stock_period_min, turnover_average, \
                stock_period_max in sqlresult:
            turnover_average = float_round(
                turnover_average, self._fields['turnover_average'].digits[1])
            this = self.env['product.product'].browse(product_id)
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
