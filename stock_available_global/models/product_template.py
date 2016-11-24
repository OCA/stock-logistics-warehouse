# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qty_available_global = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_product_available_global',
        search='_search_qty_available_global',
        string='Global Quantity On Hand',
        help="Compute all companies")
    incoming_qty_global = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_product_available_global',
        search='_search_incoming_qty_global',
        string='Global Incoming',
        help="Compute all companies")
    outgoing_qty_global = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_product_available_global',
        search='_search_outgoing_qty_global',
        string='Global Outgoing',
        help="Compute all companies")
    virtual_available_global = fields.Float(
        compute='_product_available_global',
        search='_search_virtual_available_global',
        digits=dp.get_precision('Forecasted Quantity'),
        string='Global Forecasted Quantity',
        help="Compute all companies")

    @api.multi
    @api.depends('qty_available', 'virtual_available', 'incoming_qty',
                 'outgoing_qty')
    def _product_available_global(self):
        for product in self:
            product.qty_available_global = product.sudo().qty_available
            product.virtual_available_global = product.sudo().virtual_available
            product.incoming_qty_global = product.sudo().incoming_qty
            product.outgoing_qty_global = product.sudo().outgoing_qty

    @api.model
    def _search_qty_available_global(self, operator, value):
        name = 'qty_available'
        domain = [(name, operator, value)]
        return self.sudo()._search_product_quantity(self, name, domain)

    @api.model
    def _search_incoming_qty_global(self, operator, value):
        name = 'incoming_qty'
        domain = [(name, operator, value)]
        return self.sudo()._search_product_quantity(self, name, domain)

    @api.model
    def _search_outgoing_qty_global(self, operator, value):
        name = 'outgoing_qty'
        domain = [(name, operator, value)]
        return self.sudo()._search_product_quantity(self, name, domain)

    @api.model
    def _search_virtual_available_global(self, operator, value):
        name = 'virtual_available'
        domain = [(name, operator, value)]
        return self.sudo()._search_product_quantity(self, name, domain)
