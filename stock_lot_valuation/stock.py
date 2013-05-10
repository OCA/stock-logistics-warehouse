# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    
    _columns = {
        'standard_price': fields.float('Cost', digits_compute=dp.get_precision('Lot Price'), help="Cost price (in company currency) of the lot used for standard stock valuation in accounting.", groups="base.group_user"),
        'cost_method': fields.selection([('standard','Standard Price'), ('average','Average Price')], 'Costing Method', required=True,
            help="Standard Price: The cost price is manually updated at the end of a specific period (usually every year). \nAverage Price: The cost price is recomputed at each incoming shipment."),
        }
    
    def price_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for lot in self.browse(cr, uid, ids, context=context):
            res[lot.id] = lot['standard_price'] or 0.0
            if 'uom' in context:
                uom = lot.product_id.uom_id or lot.product_id.uos_id
                res[lot.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, res[lot.id], context['uom'])
            # Convert from price_type currency to asked one
            if 'currency_id' in context:
                res[lot.id] = self.pool.get('res.currency').compute(cr, uid,
                    lot.company_id.currency_id.id,
                    context['currency_id'], res[lot.id],context=context)
        return res

class stock_move(orm.Model):
    _inherit = "stock.move"

    def _get_reference_accounting_values_for_valuation(self, cr, uid, move, context=None):
        res = super(stock_move,self)._get_reference_accounting_values_for_valuation(
            cr, uid, move, context=context)
        if not move.product_id.cost_method == 'average' or not move.price_unit:
            if move.prodlot_id:
                if context is None:
                    context = {}
                currency_ctx = dict(context, currency_id = move.company_id.currency_id.id)
                amount_unit = move.prodlot_id.price_get(context=currency_ctx)[move.prodlot_id.id]
                reference_amount = amount_unit * qty
                res[0]  = reference_amount
        return res
