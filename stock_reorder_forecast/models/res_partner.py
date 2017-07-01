# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

'''
Additional fields for the purchase proposal
'''
from openerp import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def sql_update_partner(self):
        sql = """
        UPDATE res_partner RP
            SET ultimate_purchase =
            (SELECT MIN(PP.ultimate_purchase)
                 FROM product_supplierinfo PS
                 JOIN product_product PP
                 ON PS.product_id = PP.id AND PS.sequence = 1
                 AND PP.active AND NOT PP.ultimate_purchase IS NULL
             WHERE PS.name = RP.id),
             write_date = NOW() AT TIME ZONE 'UTC', write_uid = %s
             WHERE active AND (supplier OR NOT ultimate_purchase IS NULL);
        """
        self.env.cr.execute(sql, [self.env.uid])

    @api.multi
    def _compute_product_supplierinfo_primary(self):
        """given a partner, return a list of products it provides
        as primary supplier"""
        if not self.ids:
            return
        self.env.cr.execute(
            """
            with  min_select as (
                select product_tmpl_id, min(sequence) as min_sequence  from
                product_supplierinfo group by product_tmpl_id
            )
            select
                name, array_agg(product_tmpl_id)
            from product_supplierinfo as sup_select
            where name in %s and sequence in  (
                    select min_sequence from min_select
                    where
                       min_select.product_tmpl_id = sup_select.product_tmpl_id
            )
            group by name
            """,
            (tuple(self.ids),)
        )
        partner2products = dict(self.env.cr.fetchall())
        for this in self:
            if this.id in partner2products.keys():
                this.primary_product_ids = partner2products[this.id]

    @api.multi
    def _compute_product_supplierinfo(self):
        """given a partner, return a list of all products it provides"""
        if not self.ids:
            return
        self.env.cr.execute(
            'select name, array_agg(product_tmpl_id) from product_supplierinfo'
            ' where name in %s   group by name ', (tuple(self.ids),)
        )
        partner2products = dict(self.env.cr.fetchall())
        for this in self:
            if this.id in partner2products.keys():
                this.product_ids = partner2products[this.id]

    stock_period_min = fields.Integer(
        'Delivery period',
        help="""Delivery time in weeks between the creation of the
        purchase order and the reception of the products in your
        warehouse. Used by the purchase proposal.""")
    stock_period_max = fields.Integer(
        'Purchase period',
        help="""Period in weeks to resupply for.
        Used by the purchase proposal.""")
    turnover_period = fields.Integer(
        'Turnover period',
        help="""Turnover period in weeks to calculate average
        turnover per week. Used by the purchase proposal.""")
    ultimate_purchase = fields.Date(
        'Ultimate purchase',
        readonly="1",
        help="""Ultimate date to purchase for not running out of
        stock for any product supplied by this supplier. Used by the
        purchase proposal.""")

    product_ids = fields.Many2many(
        'product.template',
        compute='_compute_product_supplierinfo',
        string="Products",
    )
    primary_product_ids = fields.Many2many(
        'product.template',
        compute='_compute_product_supplierinfo_primary',
        string="Products",
    )
