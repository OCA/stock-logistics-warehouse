# Copyright 2016-2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductStockAvailableMixin(models.AbstractModel):
    _name = 'product.stock.available.mixin'

    qty_available_global = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_quantities_global',
        search='_search_qty_available_global',
        string='Global Quantity On Hand',
        help="Compute all companies")
    incoming_qty_global = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_quantities_global',
        search='_search_incoming_qty_global',
        string='Global Incoming',
        help="Compute all companies")
    outgoing_qty_global = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_quantities_global',
        search='_search_outgoing_qty_global',
        string='Global Outgoing',
        help="Compute all companies")
    virtual_available_global = fields.Float(
        compute='_compute_quantities_global',
        search='_search_virtual_available_global',
        digits=dp.get_precision('Forecasted Quantity'),
        string='Global Forecasted Quantity',
        help="Compute all companies")

    @api.multi
    @api.depends('qty_available', 'virtual_available', 'incoming_qty',
                 'outgoing_qty')
    def _compute_quantities_global(self):
        # If use for product in self.sudo() raise error in assignation as sudo
        for product in self:
            product_sudo = product.sudo()
            product.qty_available_global = product_sudo.qty_available
            product.virtual_available_global = product_sudo.virtual_available
            product.incoming_qty_global = product_sudo.incoming_qty
            product.outgoing_qty_global = product_sudo.outgoing_qty

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
