# -*- coding: utf-8 -*-
# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockConfig(models.TransientModel):
    _inherit = 'stock.config.settings'

    backorder_manual_quants = fields.Boolean(
        string='',
        help="")

    def _get_parameter(self, key, default=False):
        param_obj = self.env['ir.config_parameter']
        rec = param_obj.search([('key', '=', key)])
        return rec or default

    def _write_or_create_param(self, key, value):
        param_obj = self.env['ir.config_parameter']
        rec = self._get_parameter(key)
        if rec:
            rec.value = str(value)
        else:
            param_obj.create({'key': key, 'value': str(value)})

    @api.multi
    def get_default_parameter_backorder_manual_quants(self):
        def get_value(key, default=''):
            rec = self._get_parameter(key)
            return rec and rec.value and rec.value != 'False' or default
        return {'backorder_manual_quants':
                get_value('stock.backorder.manual_quants', False)}

    @api.multi
    def set_parameter_backorder_manual_quants(self):
        self._write_or_create_param('stock.backorder.manual_quants',
                                    self.backorder_manual_quants)
