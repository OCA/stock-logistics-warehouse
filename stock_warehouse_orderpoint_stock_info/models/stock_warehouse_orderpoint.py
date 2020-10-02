# Copyright 2016 OdooMRP Team
# Copyright 2016 AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2016-17 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    product_location_qty = fields.Float(
        string='Quantity On Location',
        compute='_compute_product_available_qty',
    )
    incoming_location_qty = fields.Float(
        string='Incoming On Location',
        compute='_compute_product_available_qty'
    )
    outgoing_location_qty = fields.Float(
        string='Outgoing On Location',
        compute='_compute_product_available_qty'
    )
    virtual_location_qty = fields.Float(
        string='Forecast On Location',
        compute='_compute_product_available_qty'
    )
    product_category = fields.Many2one(
        string='Product Category',
        related='product_id.categ_id',
        store=True
    )
    product_under_minimun = fields.Boolean(
        string='Product Under Minimun',
        compute='_compute_product_available_qty',
        search='_search_product_under_minimun'
    )
    product_over_maximum = fields.Boolean(
        string='Product Over Maximum',
        compute='_compute_product_available_qty',
        search='_search_product_over_maximum'
    )

    @api.multi
    def _compute_product_available_qty(self):
        operation_by_location = defaultdict(
            lambda: self.env['stock.warehouse.orderpoint']
        )
        for order in self:
            operation_by_location[order.location_id] |= order
        for location_id, order_in_location in operation_by_location.items():
            products = order_in_location.mapped('product_id').with_context(
                location=location_id.id
            )._compute_quantities_dict(
                lot_id=self.env.context.get('lot_id'),
                owner_id=self.env.context.get('owner_id'),
                package_id=self.env.context.get('package_id')
            )
            for order in order_in_location:
                p = products[order.product_id.id]
                order.update({
                    'product_location_qty': p['qty_available'],
                    'incoming_location_qty': p['incoming_qty'],
                    'outgoing_location_qty': p['outgoing_qty'],
                    'virtual_location_qty': p['virtual_available'],
                    'product_under_minimun' : p['qty_available'] < order.product_min_qty,
                    'product_over_maximum' : p['qty_available'] > order.product_max_qty,
                })

    def _search_product_under_minimun(self, operator, value):
        if operator == '=':
            recs = self.search([]).filtered(lambda x : x.product_under_minimun is True)
        else:
            recs = self.search([]).filtered(lambda x : x.product_under_minimun is False)
        if recs:
            return [('id', 'in', [x.id for x in recs])]

    def _search_product_over_maximum(self, operator, value):
        if operator == '=':
            recs = self.search([]).filtered(lambda x : x.product_over_maximum is True)
        else:
            recs = self.search([]).filtered(lambda x : x.product_over_maximum is False)
        if recs:
            return [('id', 'in', [x.id for x in recs])]
