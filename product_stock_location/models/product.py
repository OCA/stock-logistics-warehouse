# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.osv import fields as old_fields
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def action_open_product_stock_location(self):
        self.ensure_one()
        ref = 'product_stock_location.product_open_product_stock_location'
        products = self._get_products()
        action_dict = self._get_act_window_dict(ref)
        action_dict['domain'] = [('product_id', 'in', products)]
        action_dict['context'] = "{'search_default_internal_loc': 1}"
        return action_dict

    def _product_available(self, cr, uid, ids, name, arg, context=None):
        return super(ProductTemplate, self)._product_available(
            cr, uid, ids, name=name, arg=arg, context=context)

    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        return super(ProductTemplate, self)._search_product_quantity(
            cr, uid, obj, name, domain, context)

    # overwrite ot this fields so that we can modify _product_available
    # function to support packs
    _columns = {
        'qty_available': old_fields.function(
            _product_available, multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float',
            string='Quantity On Hand'),
        'virtual_available': old_fields.function(
            _product_available, multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float',
            string='Forecast Quantity'),
        'incoming_qty': old_fields.function(
            _product_available, multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float',
            string='Incoming'),
        'outgoing_qty': old_fields.function(
            _product_available, multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float',
            string='Outgoing')
    }


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _product_available_compute_nonstored(self, cr, uid, context=None):
        return context.get('compute_stored_product_stock', False) or \
            context.get('lot_id', False) or \
            context.get('owner_id', False) or \
            context.get('package_id', False)

    def _get_product_stock_location_search_domain(self, product, location_ids):
        return [('product_id', '=', product.id),
                ('location_id', 'in', location_ids)]

    def _get_domain_locations_product_stock_location(self, cr,
                                                     uid, context=None):
        location_obj = self.pool.get('stock.location')
        warehouse_obj = self.pool.get('stock.warehouse')

        location_ids = []
        if context.get('location', False):
            if isinstance(context['location'], (int, long)):
                location_ids = [context['location']]
            elif isinstance(context['location'], basestring):
                domain = [('complete_name', 'ilike', context['location'])]
                if context.get('force_company', False):
                    domain += [('company_id', '=', context['force_company'])]
                location_ids = location_obj.search(cr, uid, domain,
                                                   context=context)
            else:
                location_ids = context['location']
        else:
            if context.get('warehouse', False):
                if isinstance(context['warehouse'], (int, long)):
                    wids = [context['warehouse']]
                elif isinstance(context['warehouse'], basestring):
                    domain = [('name', 'ilike', context['warehouse'])]
                    if context.get('force_company', False):
                        domain += [('company_id', '=',
                                    context['force_company'])]
                    wids = warehouse_obj.search(cr, uid, domain,
                                                context=context)
                else:
                    wids = context['warehouse']
            else:
                wids = warehouse_obj.search(cr, uid, [], context=context)

            for w in warehouse_obj.browse(cr, uid, wids, context=context):
                location_ids.append(w.view_location_id.id)
        return location_ids

    def _product_available(self, cr, uid, ids, field_names=None, arg=False,
                           context=None):
        if self._product_available_compute_nonstored(cr, uid, context=context):
            return super(ProductProduct, self)._product_available(
                cr, uid, ids, field_names=field_names,
                arg=arg, context=context)
        location_ids = self._get_domain_locations_product_stock_location(
            cr, uid, context=context)
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            domain = self._get_product_stock_location_search_domain(
                product, location_ids)

            qty_available = 0.0
            for group in self.pool['product.stock.location'].read_group(
                    cr, uid, domain, ['product_id', 'product_location_qty'],
                    ['product_id'], context=context):
                qty_available = group['product_location_qty']

            incoming_qty = 0.0
            for group in self.pool['product.stock.location'].read_group(
                    cr, uid, domain, ['product_id', 'incoming_location_qty'],
                    ['product_id'], context=context):
                incoming_qty = group['incoming_location_qty']

            outgoing_qty = 0.0
            for group in self.pool['product.stock.location'].read_group(
                cr, uid, domain, ['product_id', 'outgoing_location_qty'],
                    ['product_id'], context=context):
                outgoing_qty = group['outgoing_location_qty']

            virtual_available = 0.0
            for group in self.pool['product.stock.location'].read_group(
                cr, uid, domain, ['product_id', 'virtual_location_qty'],
                    ['product_id'], context=context):
                virtual_available = group['virtual_location_qty']

            res[product.id] = {
                'qty_available': qty_available,
                'incoming_qty': incoming_qty,
                'outgoing_qty': outgoing_qty,
                'virtual_available': virtual_available
            }
        return res

    def _search_product_quantity_nonstored(self, cr, uid, context=None):
        return context.get('lot_id', False) or \
            context.get('owner_id', False) or \
            context.get('package_id', False)

    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        if self._search_product_quantity_nonstored(cr, uid, context=context):
            return super(ProductProduct, self)._search_product_quantity(
                cr, uid, obj, name, domain, context)
        psl_obj = self.pool['product.stock.location']
        res = []
        for field, operator, value in domain:
            # to prevent sql injections
            assert field in ('qty_available', 'virtual_available',
                             'incoming_qty', 'outgoing_qty'), \
                'Invalid domain left operand'
            assert operator in (
                '<', '>', '=', '!=', '<=', '>='), 'Invalid domain operator'
            assert isinstance(value, (float, int)), \
                'Invalid domain right operand'

            if operator == '=':
                operator = '=='

            location_ids = \
                self._get_domain_locations_product_stock_location(
                    cr, uid, context=context)

            name = ''
            if field == 'qty_available':
                name = 'product_location_qty'
            elif field == 'incoming_qty':
                name = 'incoming_location_qty'
            elif field == 'outgoing_qty':
                name = 'outgoing_location_qty'
            elif field == 'virtual_available':
                name = 'virtual_location_qty'

            psls_ids = psl_obj.search(
                cr, uid, [(name, operator, value),
                          ('location_id', 'in', location_ids)],
                context=context)
            product_ids = []
            for psl in psl_obj.browse(cr, uid, psls_ids, context=context):
                product_ids.append(psl.product_id.id)
            res.append(('id', 'in', list(set(product_ids))))
        return res

    # overwrite ot this fields so that we can modify _product_available
    # function to support packs
    _columns = {
        'qty_available': old_fields.function(
            _product_available, multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float',
            string='Quantity On Hand'),
        'virtual_available': old_fields.function(
            _product_available, multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float',
            string='Forecast Quantity'),
        'incoming_qty': old_fields.function(
            _product_available, multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float',
            string='Incoming'),
        'outgoing_qty': old_fields.function(
            _product_available, multi='qty_available',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            fnct_search=_search_product_quantity, type='float',
            string='Outgoing')
    }
