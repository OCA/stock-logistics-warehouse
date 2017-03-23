# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockConfig(models.TransientModel):

    _inherit = 'stock.config.settings'

    stock_qty_available_lot_expired = fields.Boolean(
        'Stock level won\'t take into account lots expired',
        help='Check this if you want to compute stock level minus expired '
        'product lots (based on removal date) if it is defined')

    @api.model
    def get_default_stock_qty_available_lot_expired(self, fields):
        res = {}
        param_obj = self.env['ir.config_parameter']
        res['stock_qty_available_lot_expired'] = param_obj.get_param(
            'stock_qty_available_lot_expired', False
        )
        return res

    @api.multi
    def set_stock_qty_available_lot_expired(self):
        param_obj = self.env['ir.config_parameter']
        param_obj.set_param('stock_qty_available_lot_expired',
                            self.stock_qty_available_lot_expired)
