# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockLotSaleTrackingDetail(models.Model):
    _name = "stock.lot.sale.tracking.detail"
    _description = "Stock Lot Sale Tracking Detail"
    _auto = False

    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot/Serial Number',
        readonly=True)
    move_id = fields.Many2one(
        comodel_name='stock.move',
        readonly=True,
    )
    picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Operation Type',
        readonly=True,
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        readonly=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=True,
    )

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True)
    default_code = fields.Char(
        related='product_id.default_code',
        readonly=True,
    )
    quant_id = fields.Many2one(
        comodel_name='stock.quant',
        readonly=True,
    )
    date = fields.Datetime(
        string='Delivery Date',
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
    inventory_value = fields.Float(
        related='quant_id.inventory_value',
        readonly=True,
    )

    def _get_select_columns(self):
        columns = [
            'row_number() OVER() AS id',
            'sq.lot_id',
            'so.id as order_id',
            'sm.product_id',
            'sm.id as move_id',
            'sq.id as quant_id',
            'sm.picking_type_id',
            'sm.partner_id',
            'sm.date',
            'sm.product_uom',
            'sm.company_id',
            'sq.qty as product_uom_qty'
        ]
        return columns

    def _get_from(self):
        sql_from = [
            'stock_move sm',
            'JOIN stock_location loc ON loc.id = sm.location_dest_id',
            'JOIN stock_quant_move_rel sq_mv ON sq_mv.move_id = sm.id',
            'JOIN stock_quant sq ON sq.id = sq_mv.quant_id',
            'LEFT JOIN sale_order so ON so.procurement_group_id = sm.group_id',
        ]
        return sql_from

    def _get_where(self):
        sql_where = " WHERE loc.usage = 'customer' AND sm.state = 'done'"
        return sql_where

    def _get_group_by(self):
        sql_group_by = [
            'sq.lot_id',
            'so.id',
            'sm.id',
            'sm.product_id',
            'sm.partner_id',
            'sq.id',
            'sm.picking_type_id',
            'sm.date',
            'sm.product_uom',
            'sm.company_id',
        ]
        return sql_group_by

    def _get_order_by(self):
        sql_order_by = [
            'so.id',
            'sm.product_id',
            'sm.date',
            'sm.product_uom',
            'sm.company_id',
        ]
        return sql_order_by

    def _prepare_sql(self):
        sql = "SELECT "
        sql += ", ".join([select for select in self._get_select_columns()])
        sql += " FROM "
        sql += " ".join([sql_from for sql_from in self._get_from()])
        sql += self._get_where()
        sql += " GROUP BY "
        sql += ", ".join([group for group in self._get_group_by()])
        sql += " ORDER BY "
        sql += ", ".join([order for order in self._get_order_by()])
        return sql

    @api.model_cr
    def init(self):
        sql = """CREATE or REPLACE VIEW stock_lot_sale_tracking_detail as ("""
        sql += self._prepare_sql()
        sql += """)"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(sql)
