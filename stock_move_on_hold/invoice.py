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

from osv import fields, osv
from tools.translate import _

class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'
    
    def confirm_paid(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        super(account_invoice, self).confirm_paid(cr, uid, ids, context)
        cr.execute("""SELECT order_id FROM sale_order_invoice_rel WHERE invoice_id in %s """, (tuple(ids),))
        order_ids = map(lambda x: x[0], cr.fetchall())
        self.pool.get('sale.order').write(cr, uid, order_ids, {})
        cr.execute("""SELECT id FROM stock_picking where state = 'on_hold_paym' and sale_id in (SELECT order_id FROM sale_order_invoice_rel WHERE invoice_id in %s) """, (tuple(ids),))
        pickings = map(lambda x: x[0], cr.fetchall())
        self.pool.get('stock.picking').action_assign(cr, uid, pickings)
        return True

    _columns = {
        'is_advance': fields.boolean('Is an advance?'),
    }
    
account_invoice()

class account_invoice_line(osv.osv):
    
    _inherit = 'account.invoice.line'
    
    _columns = {
        'is_advance': fields.boolean('Is an advance?'),
    }
    
account_invoice_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
