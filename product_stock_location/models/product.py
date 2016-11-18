# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _product_available_compute_nonstored(self):
        return self.env.context.get('compute_stored_product_stock', False) or \
            self.env.context.get('lot_id', False) or \
            self.env.context.get('owner_id', False) or \
            self.env.context.get('package_id', False)

    @api.model
    def _get_product_stock_location_search_domain(self, product, location_ids):
        return [('product_id', '=', product.id),
                ('location_id', 'in', location_ids)]

    @api.multi
    def _product_available(self, field_names=None, arg=False, context=None):
        if self._product_available_compute_nonstored():
            return super(ProductProduct, self)._product_available(
                field_names=field_names, arg=arg, context=context)
        location_obj = self.env['stock.location']
        warehouse_obj = self.env['stock.warehouse']
        location_ids = []
        if self.env.context.get('location', False):
            if isinstance(self.env.context['location'], (int, long)):
                location_ids = [self.env.context['location']]
            elif isinstance(self.env.context['location'], basestring):
                domain = [('complete_name', 'ilike',
                           self.env.context['location'])]
                if context.get('force_company', False):
                    domain += [('company_id', '=',
                                self.env.context['force_company'])]
                location_ids = location_obj.search(domain).ids
            else:
                location_ids = self.env.context['location']
        else:
            if self.env.context.get('warehouse', False):
                if isinstance(self.env.context['warehouse'], (int, long)):
                    wids = [self.env.context['warehouse']]
                elif isinstance(self.env.context['warehouse'], basestring):
                    domain = [('name', 'ilike', self.env.context['warehouse'])]
                    if self.env.context.get('force_company', False):
                        domain += [('company_id', '=',
                                    self.env.context['force_company'])]
                    wids = warehouse_obj.search(domain)
                else:
                    wids = context['warehouse']
            else:
                wids = warehouse_obj.search([]).ids

            for w in warehouse_obj.browse(wids):
                location_ids.append(w.view_location_id.id)

        res = {}
        for product in self:
            domain = self._get_product_stock_location_search_domain(
                product, location_ids)

            qty_available = 0.0
            for group in self.env['product.stock.location'].read_group(
                domain, ['product_id', 'product_location_qty'],
                    ['product_id']):
                qty_available = group['product_location_qty']

            incoming_qty = 0.0
            for group in self.env['product.stock.location'].read_group(
                domain, ['product_id', 'incoming_location_qty'],
                    ['product_id']):
                incoming_qty = group['incoming_location_qty']

            outgoing_qty = 0.0
            for group in self.env['product.stock.location'].read_group(
                domain, ['product_id', 'outgoing_location_qty'],
                    ['product_id']):
                outgoing_qty = group['outgoing_location_qty']

            virtual_available = 0.0
            for group in self.env['product.stock.location'].read_group(
                domain, ['product_id', 'virtual_location_qty'],
                    ['product_id']):
                virtual_available = group['virtual_location_qty']

            res[product.id] = {
                'qty_available': qty_available,
                'incoming_qty': incoming_qty,
                'outgoing_qty': outgoing_qty,
                'virtual_available': virtual_available,
            }
        return res
