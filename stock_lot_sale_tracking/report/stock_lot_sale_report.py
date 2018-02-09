# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockLotSaleTrackingReport(models.Model):
    _name = "stock.lot.sale.tracking.report"
    _description = "Stock Lot Sale Tracking report"
    _auto = False

    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot/Serial Number',
        readonly=True)
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        readonly=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True)
    date = fields.Datetime(
        string='Date Order',
        readonly=True)
    product_uom = fields.Many2one(
        comodel_name='product.uom',
        string='Unit of Measure',
        readonly=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        readonly=True)
    product_uom_qty = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True)

    @api.model_cr
    def init(self):
        sql = """CREATE or REPLACE VIEW stock_lot_sale_tracking_report as (
               SELECT row_number() OVER () AS id,
                      sq.lot_id,
                      so.id as order_id,
                      sm.product_id,
                      sm.date,
                      sm.product_uom,
                      sm.company_id,
                      sum(sm.product_uom_qty) as product_uom_qty
               FROM stock_move sm
               JOIN stock_location loc ON loc.id = sm.location_dest_id
               JOIN stock_quant_move_rel sq_mv ON sq_mv.move_id = sm.id
               JOIN stock_quant sq ON sq.id = sq_mv.quant_id
               LEFT JOIN sale_order so ON so.procurement_group_id = sm.group_id
               WHERE loc.usage = 'customer'
                 AND sm.state = 'done'
               GROUP BY sq.lot_id,
                        so.id,
                        sm.product_id,
                        sm.date,
                        sm.product_uom,
                        sm.company_id
               ORDER BY so.id,
                        sm.product_id,
                        sm.date,
                        sm.product_uom,
                        sm.company_id
               )"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(sql)
