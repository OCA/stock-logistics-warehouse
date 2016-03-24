# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.cr_uid_context
    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
                           uom=False, qty_uos=0, uos=False, name='',
                           partner_id=False, lang=False, update_tax=True,
                           date_order=False, packaging=False, context=None):
        """
        Replace product_uom_change to use packaging in product_id_change call
        """
        lang = lang or ('lang' in context and context['lang'])
        if not uom:
            return {'value': {'price_unit': 0.0, 'product_uom': False}}
        return self.product_id_change(
            cursor, user, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, context=context)

    @api.cr_uid_context
    def product_packaging_change(self, cr, uid, ids, pricelist, product, qty=0,
                                 uom=False, partner_id=False, packaging=False,
                                 flag=False, context=None):
        """
        Set product_uom when set product_packaging
        """
        if not product:
            packaging = False
        else:
            products = self.pool['product.product'].browse(cr, uid, product,
                                                           context=context)
            if not products.packaging_ids or not flag:
                # reset empty if flag is not set, the update is not packaging
                packaging = False
        res = super(SaleOrderLine, self).product_packaging_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            partner_id=partner_id, packaging=packaging, flag=flag,
            context=context)
        if packaging:
            uom = self.pool['product.packaging'].read(
                cr, uid, packaging, ['uom_id'], context=context)['uom_id'][0]
            res['value']['product_uom'] = uom
        else:
            res['value']['product_packaging'] = False

        return res

    @api.model
    def update_vals(self, vals):
        """
        When product_packaging is set, product_uom is readonly,
        so we need to reset the uom value in the vals dict
        """
        if vals.get('product_packaging'):
            vals['product_uom'] = self.env['product.packaging'].browse(
                vals['product_packaging']).uom_id.id
        return vals

    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, vals):
        return super(SaleOrderLine, self).create(self.update_vals(vals))

    @api.multi
    def write(self, vals):
        return super(SaleOrderLine, self).write(self.update_vals(vals))
