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
        
    def do_change_standard_price(self, cr, uid, ids, datas, context=None):
        """ Changes the Standard Price of Lot and creates an account move accordingly.
        @param datas : dict. contain default datas like new_price, stock_output_account, stock_input_account, stock_journal
        @param context: A standard dictionary
        """
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        if context is None:
            context = {}

        new_price = datas.get('new_price', 0.0)
        stock_output_acc = datas.get('stock_output_account', False)
        stock_input_acc = datas.get('stock_input_account', False)
        journal_id = datas.get('stock_journal', False)
        lot_obj=self.browse(cr, uid, ids, context=context)[0]
        account_valuation = lot_obj.product_it.categ_id.property_stock_valuation_account_id
        account_valuation_id = account_valuation and account_valuation.id or False
        if not account_valuation_id: raise osv.except_osv(_('Error!'), _('Specify valuation Account for Product Category: %s.') % (lot_obj.product_it.categ_id.name))
        move_ids = []
        loc_ids = location_obj.search(cr, uid,[('usage','=','internal')])
        for rec_id in ids:
            for location in location_obj.browse(cr, uid, loc_ids, context=context):
                c = context.copy()
                c.update({
                    'location': location.id,
                    'compute_child': False
                })

                lot = self.browse(cr, uid, rec_id, context=c)
                qty = lot.stock_available
                diff = lot.standard_price - new_price
                if not diff: raise osv.except_osv(_('Error!'), _("No difference between standard price and new price!"))
                if qty:
                    company_id = location.company_id and location.company_id.id or False
                    if not company_id: raise osv.except_osv(_('Error!'), _('Please specify company in Location.'))
                    #
                    # Accounting Entries
                    #
                    product = lot.product_id
                    if not journal_id:
                        journal_id = product.categ_id.property_stock_journal and product.categ_id.property_stock_journal.id or False
                    if not journal_id:
                        raise osv.except_osv(_('Error!'),
                            _('Please define journal '\
                              'on the product category: "%s" (id: %d).') % \
                                (product.categ_id.name,
                                    product.categ_id.id,))
                    move_id = move_obj.create(cr, uid, {
                                'journal_id': journal_id,
                                'company_id': company_id
                                })

                    move_ids.append(move_id)


                    if diff > 0:
                        if not stock_input_acc:
                            stock_input_acc = product.\
                                property_stock_account_input.id
                        if not stock_input_acc:
                            stock_input_acc = product.categ_id.\
                                    property_stock_account_input_categ.id
                        if not stock_input_acc:
                            raise osv.except_osv(_('Error!'),
                                    _('Please define stock input account ' \
                                            'for this product: "%s" (id: %d).') % \
                                            (product.name,
                                                product.id,))
                        amount_diff = qty * diff
                        move_line_obj.create(cr, uid, {
                                    'name': product.name,
                                    'account_id': stock_input_acc,
                                    'debit': amount_diff,
                                    'move_id': move_id,
                                    })
                        move_line_obj.create(cr, uid, {
                                    'name': product.categ_id.name,
                                    'account_id': account_valuation_id,
                                    'credit': amount_diff,
                                    'move_id': move_id
                                    })
                    elif diff < 0:
                        if not stock_output_acc:
                            stock_output_acc = product.\
                                property_stock_account_output.id
                        if not stock_output_acc:
                            stock_output_acc = product.categ_id.\
                                    property_stock_account_output_categ.id
                        if not stock_output_acc:
                            raise osv.except_osv(_('Error!'),
                                    _('Please define stock output account ' \
                                            'for this product: "%s" (id: %d).') % \
                                            (product.name,
                                                product.id,))
                        amount_diff = qty * -diff
                        move_line_obj.create(cr, uid, {
                                        'name': product.name,
                                        'account_id': stock_output_acc,
                                        'credit': amount_diff,
                                        'move_id': move_id
                                    })
                        move_line_obj.create(cr, uid, {
                                        'name': product.categ_id.name,
                                        'account_id': account_valuation_id,
                                        'debit': amount_diff,
                                        'move_id': move_id
                                    })

            self.write(cr, uid, rec_id, {'standard_price': new_price})

        return move_ids

class stock_move(orm.Model):
    _inherit = "stock.move"

    def _get_reference_accounting_values_for_valuation(self, cr, uid, move, context=None):
        res = super(stock_move,self)._get_reference_accounting_values_for_valuation(
            cr, uid, move, context=context)
        if not move.product_id.cost_method == 'average' or not move.price_unit:
            if move.product_id.lot_valuation and move.prodlot_id:
                if context is None:
                    context = {}
                currency_ctx = dict(context, currency_id = move.company_id.currency_id.id)
                amount_unit = move.prodlot_id.price_get(context=currency_ctx)[move.prodlot_id.id]
                reference_amount = amount_unit * qty
                res[0]  = reference_amount
        return res
