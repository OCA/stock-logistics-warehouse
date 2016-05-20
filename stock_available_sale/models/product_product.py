# -*- coding: utf-8 -*-
# © 2014 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import Counter

from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    """Add the computation for the stock available to promise"""
    _inherit = 'product.product'

    quoted_qty = fields.Float(
        compute='_get_quoted_qty',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='Quoted',
        help="Total quantity of this Product that have been included in "
             "Quotations (Draft Sale Orders).\n"
             "In a context with a single Warehouse, this includes "
             "Quotation processed in this Warehouse.\n"
             "In a context with a single Stock Location, this includes "
             "Quotation processed at any Warehouse using "
             "this Location, or any of its children, as it's Stock "
             "Location.\n"
             "Otherwise, this includes every Quotation.")

    @api.multi
    @api.depends('quoted_qty')
    def _immediately_usable_qty(self):
        """Subtract quoted quantity from qty available to promise

        This is the same implementation as for templates."""
        super(ProductProduct, self)._immediately_usable_qty()
        for product in self:
            product.immediately_usable_qty -= product.quoted_qty

    @api.multi
    def _get_quoted_qty(self):
        """Compute the quantities in Quotations."""

        domain = [
            ('state', '=', 'draft'),
            ('product_id', 'in', self.ids)]

        #  Limit to a specific company
        if self.env.context.get('force_company', False):
            domain.append(('company_id', '=',
                           self.env.context['force_company']))
        # when we search locations, should children be searched too?
        if self.env.context.get('compute_child', True):
            loc_op = 'child_of'
        else:
            loc_op = 'in'
        # Limit to some locations
        # Take warehouses that have these locations as stock locations
        if self.env.context.get('location', False):
            # Search by ID
            if isinstance(self.env.context['location'], (int, long)):
                domain.append(
                    ('order_id.warehouse_id.lot_stock_id', loc_op,
                     [self.env.context['location']]))
            # Search by name
            elif isinstance(self.env.context['location'], basestring):
                location_ids = [
                    l.id
                    for l in self.env['stock.location'].search([
                        ('complete_name', 'ilike',
                         self.env.context['location'])])]
                domain.append(
                    ('order_id.warehouse_id.lot_stock_id', loc_op,
                     location_ids))
            # Search by whatever the context has - probably a list of IDs
            else:
                domain.append(
                    ('order_id.warehouse_id.lot_stock_id', loc_op,
                     self.env.context['location']))
        # Limit to a warehouse
        if self.env.context.get('warehouse', False):
            domain.append(
                ('order_id.warehouse_id', '=', self.env.context['warehouse']))
        # Limit to a period
        from_date = self.env.context.get('from_date', False)
        to_date = self.env.context.get('to_date', False)
        if from_date:
            domain.extend([
                ('order_id.requested_date', '>=', from_date),
                '&',  # only consider 'date' when 'equested_date' is empty
                ('order_id.requested_date', '=', False),
                ('order_id.date', '>=', from_date),
                ])
        if to_date:
            domain.extend([
                ('order_id.requested_date', '<=', to_date),
                '&',  # only consider 'date' when 'equested_date' is empty
                ('order_id.requested_date', '=', False),
                ('order_id.date', '<=', to_date),
                ])

        # Compute the quoted quantity for each product
        results = Counter()
        for group in self.env['sale.order.line'].read_group(
                domain, ['product_uom_qty', 'product_id', 'product_uom'],
                ['product_id', 'product_uom'],
                lazy=False):
            product_id = group['product_id'][0]
            uom_id = group['product_uom'][0]
            # Compute the quoted quantity in the product's UoM
            # Rounding is OK since small values have not been squashed before
            results += Counter({
                product_id: self.env['product.uom']._compute_qty(
                    uom_id, group['product_uom_qty'],
                    self.browse(product_id).uom_id.id)})

        for product in self:
            product.quoted_qty = results.get(product.id, 0.0)
