# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from datetime import datetime
from osv import fields, osv
from tools.translate import _
import netsvc

# ----------------------------------------------------
# Move
# ----------------------------------------------------

#
# Fields:
#   location_dest_id is only used for predicting future stocks
#
class stock_move(osv.osv):
    
    _inherit = 'stock.move'

    _columns = {
        'state': fields.selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting'),
            ('on_hold', 'Waiting for prepayment'),
            ('on_hold_billing', 'Waiting for billing'),
            ('on_hold_paym', 'Waiting for payment'),
            ('confirmed', 'Not Available'),
            ('assigned', 'Available'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], 'State', readonly=True, select=True,
            help="* When the stock move is created it is in the \'Draft\' state.\n"\
                 "* After that, it is set to \'Not Available\' state if the scheduler did not find the products.\n"\
                 "* When products are reserved it is set to \'Available\'.\n"\
                 "* When the picking is done the state is \'Done\'.\n"\
                 "* The state is \'Waiting\' if the move is waiting for another one.\n"\
                 "* The state is \'Waiting for prepayment\' if it's waiting for a prepayment of the sale order\n"\
                 "* The state is \'Waiting for billing\' if it's waiting for billing of the move\n"\
                 "* The state is \'Waiting for payment\' if it's waiting for the payment of the move"),
    }
    
    def action_on_hold(self, cr, uid, ids, context=None):
        """ Holds stock move.
        @return: List of ids.
        """
        moves = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'on_hold'})
        
        if moves:
            picking = moves[0].picking_id
            if picking:
                moves = picking.move_lines
                state = 'on_hold'
                for move in moves:
                    if move.state not in ['on_hold','done','cancel']:
                        state = False
                        break
                if state:
                    self.pool.get('stock.picking').write(cr, uid, picking.id, {'state': state}, context)
        return []
    
    def action_hold_to_confirm(self, cr, uid, ids, context=None):
        """ Makes hold stock moves to the confirmed state.
        @return: List of ids.
        """
        moves = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        
        if moves:
            picking = moves[0].picking_id
            if picking:
                moves = picking.move_lines
                state = 'confirmed'
                for move in moves:
                    if move.state in ['on_hold','draft']:
                        state = False
                        break
                if state:
                    self.pool.get('stock.picking').write(cr, uid, picking.id, {'state': state}, context)
        return []

    def action_confirm_waiting_bill(self, cr, uid, ids, context=None):
        """ Makes hold stock moves to the wait for billing state.
        @return: List of ids.
        """
        moves = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'on_hold_billing'})
        
        if moves:
            picking = moves[0].picking_id
            if picking:
                moves = picking.move_lines
                state = 'on_hold_billing'
                for move in moves:
                    if move.state in ['on_hold','draft']:
                        state = False
                        break
                if state:
                    self.pool.get('stock.picking').write(cr, uid, picking.id, {'state': state}, context)
        return []

    def action_waiting_bill_to_unpaid(self, cr, uid, ids, context=None):
        """ Makes hold stock moves to the wait for payment state.
        @return: List of ids.
        """
        moves = self.browse(cr, uid, ids, context=context)
        
        if moves:
            picking = moves[0].picking_id
            if picking:
                moves = picking.move_lines
                state = 'on_hold_paym'
                for move in moves:
                    if move.state in ['on_hold','draft']:
                        state = False
                        break
                if state:
                    self.pool.get('stock.picking').write(cr, uid, picking.id, {'state': state}, context)
        return []
    
    """ This part is replacing the usual one to be able to taking in account the new states. """
    def action_assign(self, cr, uid, ids, *args):
        """ Changes state to confirmed or waiting.
        @return: List of values
        """
        todo = []
        for move in self.browse(cr, uid, ids):
            if move.state in ('confirmed', 'waiting', 'on_hold_billing', 'on_hold_paym', 'assigned'):
                todo.append(move.id)
        res = self.check_assign(cr, uid, todo)
        return res
    
    """ This part is replacing the usual one to be able to taking in account the new states. """
    def check_assign(self, cr, uid, ids, context=None):
        """ Checks the product type and accordingly writes the state.
        @return: No. of moves done
        """
        done = []
        count = 0
        waiting = 0
        pickings = {}
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.product_id.type == 'consu' or move.location_id.usage == 'supplier':
                if move.state in ('confirmed', 'waiting'):
                    done.append(move.id)
                pickings[move.picking_id.id] = 1
                continue
            if move.state in ('confirmed', 'waiting', 'on_hold_billing', 'on_hold_paym'):
                if move.state in ('on_hold_billing', 'on_hold_paym'):
                    res = True
                else:
                    # Important: we must pass lock=True to _product_reserve() to avoid race conditions and double reservations
                    res = self.pool.get('stock.location')._product_reserve(cr, uid, [move.location_id.id], move.product_id.id, move.product_qty, {'uom': move.product_uom.id}, lock=True)
                if res:
                    if move.sale_line_id and move.sale_line_id.order_id.order_policy in ['ship_prepayment','wait_prepayment']:
                        if not move.sale_line_id.invoice_lines:
                            self.write(cr, uid, [move.id], {'state':'on_hold_billing'})
                            pickings[move.picking_id.id] = 1
                            waiting += 1
                        else:
                            for line in move.sale_line_id.invoice_lines:
                                if line.invoice_id and line.invoice_id.state == 'cancel':
                                    self.write(cr, uid, [move.id], {'state':'on_hold_billing'})
                                    pickings[move.picking_id.id] = 1
                                    waiting += 1
                                elif line.invoice_id and line.invoice_id.state != 'paid':
                                    self.write(cr, uid, [move.id], {'state':'on_hold_paym'})
                                    pickings[move.picking_id.id] = 1
                                    waiting += 1
                                elif line.invoice_id and line.invoice_id.state == 'paid':
                                    self.write(cr, uid, [move.id], {'state':'assigned'})
                                    pickings[move.picking_id.id] = 1
                                    waiting += 1
                    #_product_available_test depends on the next status for correct functioning
                    #the test does not work correctly if the same product occurs multiple times
                    #in the same order. This is e.g. the case when using the button 'split in two' of
                    #the stock outgoing form
                    elif res != True:
                        self.write(cr, uid, [move.id], {'state':'assigned'})
                        done.append(move.id)
                        pickings[move.picking_id.id] = 1
                        r = res.pop(0)
                        cr.execute('update stock_move set location_id=%s, product_qty=%s where id=%s', (r[1], r[0], move.id))
    
                        while res:
                            r = res.pop(0)
                            move_id = self.copy(cr, uid, move.id, {'product_qty': r[0], 'location_id': r[1]})
                            done.append(move_id)
        if done:
            count += len(done)
            self.write(cr, uid, done, {'state': 'assigned'})

        if count or waiting:
            for pick_id in pickings:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
        return count
    
stock_move()

class stock_picking(osv.osv):
    
    _inherit = 'stock.picking'
    
    _columns = {
        'state': fields.selection([
            ('draft', 'Draft'),
            ('auto', 'Waiting'),
            ('on_hold', 'Waiting for prepayment'),
            ('on_hold_billing', 'Waiting for billing'),
            ('on_hold_paym', 'Waiting for payment'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Available'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ], 'State', readonly=True, select=True,
            help="* Draft: not confirmed yet and will not be scheduled until confirmed\n"\
                 "* Confirmed: still waiting for the availability of products\n"\
                 "* Waiting: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"\
                 "* On Hold: waiting for a payment, payment or billing\n"\
                 "* Waiting for billing: waiting for billing of the picking\n"\
                 "* Waiting for payment: waiting for the payment of the picking\n"\
                 "* Available: products reserved, simply waiting for confirmation.\n"\
                 "* Done: has been processed, can't be modified or cancelled anymore\n"\
                 "* Cancelled: has been cancelled, can't be confirmed anymore"),
    }
    
    def action_on_hold(self, cr, uid, ids, context=None):
        """ Holds picking.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'on_hold'})
        todo = []
        for picking in self.browse(cr, uid, ids, context=context):
            for r in picking.move_lines:
                if r.state in ['draft','confirmed','waiting','assigned','on_hold_billing','on_hold_paym']:
                    todo.append(r.id)

        self.log_picking(cr, uid, ids, context=context)

        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_on_hold(cr, uid, todo, context=context)
        return True
    
    def action_hold_to_confirm(self, cr, uid, ids, context=None):
        """ Makes hold pickings to the confirmed state.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'confirmed'})
        todo = []
        for picking in self.browse(cr, uid, ids, context=context):
            for r in picking.move_lines:
                if r.state in ['on_hold']:
                    todo.append(r.id)

        self.log_picking(cr, uid, ids, context=context)

        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_hold_to_confirm(cr, uid, todo, context=context)
        return True

    def action_confirm_waiting_bill(self, cr, uid, ids, context=None):
        """ Makes hold pickings to the wait for billing state.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'on_hold_billing', 'invoice_state': '2binvoiced'})
        todo = []
        for picking in self.browse(cr, uid, ids, context=context):
            for r in picking.move_lines:
                if r.state in ['on_hold_billing']:
                    todo.append(r.id)

        self.log_picking(cr, uid, ids, context=context)

        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_confirm_waiting_bill(cr, uid, todo, context=context)
        return True
    
    def action_waiting_bill_to_unpaid(self, cr, uid, ids, context=None):
        """ Makes hold pickings to the wait for payment state.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'on_hold_paym'})
        todo = []
        for picking in self.browse(cr, uid, ids, context=context):
            for r in picking.move_lines:
                if r.state in ['on_hold_paym']:
                    todo.append(r.id)

        self.log_picking(cr, uid, ids, context=context)

        todo = self.action_explode(cr, uid, todo, context)
        if len(todo):
            self.pool.get('stock.move').action_waiting_bill_to_unpaid(cr, uid, todo, context=context)
        return True

    """ This part is replacing the usual one to be able to taking in account the new states. """
    def action_assign(self, cr, uid, ids, *args):
        """ Changes state of picking to available if all moves are confirmed.
        @return: True
        """
        for pick in self.browse(cr, uid, ids):
            move_ids = [x.id for x in pick.move_lines if x.state in ['confirmed','on_hold_billing','on_hold_paym']]
            if not move_ids:
                raise osv.except_osv(_('Warning !'),_('Not enough stock, unable to reserve the products.'))
            self.pool.get('stock.move').action_assign(cr, uid, move_ids)
        return True
    
    def test_billed(self, cr, uid, ids):
        """ Tests whether the move has been billed or not.
        @return: True or False
        """
        ok = True
        for pick in self.browse(cr, uid, ids):
            mt = pick.move_type
            for move in pick.move_lines:
                if (move.state in ('confirmed', 'draft')) and (mt == 'one'):
                    return False
                if (mt == 'direct') and (move.state == 'on_hold_billing') and (move.product_qty):
                    return True
                ok = ok and (move.state in ('cancel', 'done', 'assigned', 'on_hold_paym'))
        return ok
    
    def test_bill_and_paid(self, cr, uid, ids):
        """ Tests whether the move has been billed and paid or not.
        @return: True or False
        """
        ok = True
        for pick in self.browse(cr, uid, ids):
            mt = pick.move_type
            for move in pick.move_lines:
                if (move.state in ('confirmed', 'draft', 'on_hold', 'on_hold_billing')) and (mt == 'one'):
                    return False
                if (mt == 'direct') and (move.state == 'on_hold_paym') and (move.product_qty):
                    return True
                ok = ok and (move.state in ('cancel', 'done', 'assigned'))
        return ok
    
    def test_paid(self, cr, uid, ids):
        """ Tests whether the move has been paid.
        @return: True or False
        """
        ok = True
        for pick in self.browse(cr, uid, ids):
            mt = pick.move_type
            for move in pick.move_lines:
                if (move.state in ('confirmed', 'draft', 'on_hold', 'on_hold_billing', 'on_hold_paym')) and (mt == 'one'):
                    return False
                if (mt == 'direct') and (move.state == 'assigned') and (move.product_qty):
                    return True
                ok = ok and (move.state in ('cancel', 'done', 'assigned'))
        return ok

    """ This part is replacing the usual one to be able to taking in account the new states. """
    def log_picking(self, cr, uid, ids, context=None):
        """ This function will create log messages for picking.
        @param cr: the database cursor
        @param uid: the current user's ID for security checks,
        @param ids: List of Picking Ids
        @param context: A standard dictionary for contextual values
        """
        if context is None:
            context = {}
        data_obj = self.pool.get('ir.model.data')
        for pick in self.browse(cr, uid, ids, context=context):
            msg=''
            if pick.auto_picking:
                continue
            type_list = {
                'out':_("Delivery Order"),
                'in':_('Reception'),
                'internal': _('Internal picking'),
            }
            view_list = {
                'out': 'view_picking_out_form',
                'in': 'view_picking_in_form',
                'internal': 'view_picking_form',
            }
            message = type_list.get(pick.type, _('Document')) + " '" + (pick.name or '?') + "' "
            if pick.min_date:
                msg= _(' for the ')+ datetime.strptime(pick.min_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
            state_list = {
                'confirmed': _("is scheduled") + msg +'.',
                'assigned': _('is ready to process.'),
                'cancel': _('is cancelled.'),
                'done': _('is done.'),
                'draft': _('is in draft state.'),
                'auto': _('is waiting.'),
                'on_hold': _('is hold, waiting for prepayment.'),
                'on_hold_billing': _('is ready to process but waiting for a billing.'),
                'on_hold_paym': _('is ready to process but waiting for the payment.'),
            }
            res = data_obj.get_object_reference(cr, uid, 'stock', view_list.get(pick.type, 'view_picking_form'))
            context.update({'view_id': res and res[1] or False})
            message += state_list[pick.state]
            self.log(cr, uid, pick.id, message, context=context)
        return True
    
    def already_invoiced(self, cr, uid, ids, pick_invoice, context=None):
        """ Looking for what have already been invoice to deduce it on the new invoice """
        invoice_obj = self.pool.get('account.invoice')
        sale_obj = self.pool.get('sale.order')
        picking_ids = self.browse(cr, uid, ids, context)
        res = {}
        for pick in picking_ids:
            sale_id = pick.sale_id and pick.sale_id.id
            if sale_id:
                amount_prepaid = 0.00
                amount_total = 0.00
                cr.execute("""SELECT invoice_id FROM sale_order_invoice_rel WHERE order_id = %s """, (sale_id,))
                invoice_ids = map(lambda x: x[0], cr.fetchall())
                invoice_open_paid = invoice_obj.search(cr, uid, [('id', 'in', invoice_ids),('state', 'in', ['open','paid'])])
                invoice_id = pick_invoice[pick.id]
                res[invoice_id] = invoice_open_paid
                for invoice in invoice_obj.browse(cr, uid, invoice_open_paid):
                    if invoice.is_advance:
                        amount_prepaid += invoice.amount_untaxed or 0.00
                    else:
                        for line in invoice.invoice_line:
                            if not line.is_advance:
                                amount_total += line.price_subtotal or 0.00
                sale_obj.write(cr, uid, [sale_id], {'amount_prepaid': amount_prepaid, 'amount_shipped': amount_total})
        return res
    
    def create_advance_line(self, cr, uid, pick_invoice, invoice_done, context=None):
        invoice_obj = self.pool.get('account.invoice')
        account_line_obj = self.pool.get('account.invoice.line')
        for pick in pick_invoice:
            picking_id = self.browse(cr, uid, pick, context)
            sale_id = picking_id.sale_id
            total_amount = sale_id.amount_untaxed or 0.00
            prepaid_amount = sale_id.amount_prepaid or 0.00
            amount_shipped = sale_id.amount_shipped or 0.00
            invoice_id = pick_invoice[pick]
            invoice_id = invoice_obj.browse(cr, uid, invoice_id)
            invoice_amount = invoice_id.amount_untaxed
            if prepaid_amount >= amount_shipped:
                if (invoice_amount + amount_shipped) > prepaid_amount:
                    line_amount = - (prepaid_amount - amount_shipped)
                else:
                    line_amount = - invoice_amount
                res = account_line_obj.product_id_change(cr, uid, [], 7624, False, 1, partner_id=invoice_id.partner_id.id, fposition_id=invoice_id.fiscal_position.id, price_unit=line_amount, address_invoice_id=invoice_id.address_invoice_id.id, currency_id=invoice_id.currency_id.id, context=context)
                account_line_obj = self.pool.get('account.invoice.line')
                vals = res['value']
                vals.update({'invoice_id': invoice_id.id, 'invoice_line_tax_id': [(6, 0, vals['invoice_line_tax_id'])], 'note':'', 'price_unit': line_amount, 'is_advance': True})
                if vals['price_unit'] <> 0:
                    account_line_obj.create(cr, uid, vals)
            invoice_amount = invoice_id.amount_untaxed
            if sale_id:
                self.pool.get('sale.order').write(cr, uid, [sale_id.id], {'amount_shipped': amount_shipped + invoice_amount})
            invoice_obj.button_reset_taxes(cr, uid, [invoice_id.id], context=context)
        return
    
    def associate_lines(self, cr, uid, ids, pick_invoice, context):
        inv_line_obj = self.pool.get('account.invoice.line')
        move_line_obj = self.pool.get('stock.move')
        for pick in pick_invoice:
            picking_id = self.browse(cr, uid, pick, context)
            invoice_id = pick_invoice[pick]
            move_lines = picking_id.move_lines
            for line in move_lines:
                invoice_line_ids = inv_line_obj(cr, uid, [
                                                          ('invoice_id', '=', invoice_id),
                                                          ('product_id', '=', line.product_id.id),
                                                          ('quantity', '=', line.product_qty),
                                                          ])
                if invoice_line_ids:
                    move_line_obj.write(cr, uid, [line.id], {'invoice_line_id': invoice_line_ids[0]})

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        if context is None:
            context = {}
        if context.get('before_shipping', False):
            picking_ids = self.browse(cr, uid, ids)
            todo = []
            sequence_obj = self.pool.get('ir.sequence')
            for pick in picking_ids:
                line_ids = [x.id for x in pick.move_lines if x.state == 'on_hold_billing']
                old_lines_ids = [x.id for x in pick.move_lines if x.id not in line_ids]
                if line_ids:
                    wf_service = netsvc.LocalService("workflow")
                    if old_lines_ids:
                        new_picking = self.copy(cr, uid, pick.id,
                                {
                                 'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
                                 'move_lines' : [],
                                 'state':'confirmed',
                                 'backorder_id': pick.id,
                                })
                        self.pool.get('stock.move').write(cr, uid, old_lines_ids, {'picking_id': new_picking}),
                        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                    self.pool.get('stock.move').write(cr, uid, line_ids, {'state': 'on_hold_paym'}),
                    todo.append(pick.id)
            ids = todo
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id, group, type, context)
        invoice_done = self.already_invoiced(cr, uid, ids, res, context)
        self.create_advance_line(cr, uid, res, invoice_done, context)
        return res
    
stock_picking()

class stock_location(osv.osv):
    
    _inherit = "stock.location"

    def _product_reserve(self, cr, uid, ids, product_id, product_qty, context=None, lock=False):
        result = super(stock_location, self)._product_reserve(cr, uid, ids, product_id, product_qty, context, lock)
        if context is None:
            context = {}
        result = []
        for id in self.search(cr, uid, [('location_id', 'child_of', ids)]):
            cr.execute("""SELECT product_uom, sum(product_qty) AS product_qty
                          FROM stock_move
                          WHERE location_dest_id=%s AND
                                location_id<>%s AND
                                product_id=%s AND
                                state='done'
                          GROUP BY product_uom
                       """,
                       (id, id, product_id))
            results = cr.dictfetchall()
            cr.execute("""SELECT product_uom,-sum(product_qty) AS product_qty
                          FROM stock_move
                          WHERE location_id=%s AND
                                location_dest_id<>%s AND
                                product_id=%s AND
                                state in ('done', 'assigned', 'on_hold_billing', 'on_hold_paym')
                          GROUP BY product_uom
                       """,
                       (id, id, product_id))
            results += cr.dictfetchall()
            total = 0.0
            results2 = 0.0
            for r in results:
                amount = self.pool.get('product.uom')._compute_qty(cr, uid, r['product_uom'], r['product_qty'], context.get('uom', False))
                results2 += amount
                total += amount

            if total <= 0.0:
                continue

            amount = results2
            if amount > 0:
                if amount > min(total, product_qty):
                    amount = min(product_qty, total)
                result.append((amount, id))
                product_qty -= amount
                total -= amount
                if product_qty <= 0.0:
                    return result
                if total <= 0.0:
                    continue
        return False
        
stock_location()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
