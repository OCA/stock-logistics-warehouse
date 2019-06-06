# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductCostEvaluationHistory(models.Model):
    _name = "product.cost.evaluation.history"

    name = fields.Text()
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product')
    inventory_line_id = fields.Many2one(
        comodel_name='stock.inventory.line')
    date_evaluation = fields.Date(
        string='Evaluation date')
    product_qty = fields.Float(
        string='Quantity')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.user.company_id)
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
        string='Company Currency')
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Stock location')
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot/Serial Number',
        ondelete='restrict')
    fifo_cost = fields.Monetary(
        string='FIFO product unit cost',
        currency_field='company_currency_id')
    fifo_purchase_cost = fields.Monetary(
        string='FIFO product unit purchase cost',
        currency_field='company_currency_id')
    lifo_cost = fields.Monetary(
        string='LIFO product unit cost',
        currency_field='company_currency_id')
    lifo_purchase_cost = fields.Monetary(
        string='LIFO product unit purchase cost',
        currency_field='company_currency_id')
    average_cost = fields.Monetary(
        string='Average weighted product unit cost',
        currency_field='company_currency_id')
    average_purchase_cost = fields.Monetary(
        string='Average weighted product unit purchase cost',
        currency_field='company_currency_id')
    # fefo_cost = fields.Monetary(
    #     string='FEFO product unit cost')
    standard_cost = fields.Monetary(
        string='Standard product unit cost',
        currency_field='company_currency_id')
    list_price = fields.Monetary(
        string='Standard product price',
        currency_field='company_currency_id')
    # wip
    real_value = fields.Monetary(
        string='Real market value',
        currency_field='company_currency_id',
        help='If set (by hand), it is used in report instead of every other'
             ' value.')
