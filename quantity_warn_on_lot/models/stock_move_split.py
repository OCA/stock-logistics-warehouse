# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
import logging

from openerp.osv import orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class StockMoveSplit(orm.TransientModel):

    """StockMoveSplit override to handle the amount of available products."""

    _inherit = 'stock.move.split'

    def split(self, cr, uid, ids, move_ids, context=None):
        """ To split stock moves into serial numbers

        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        if context is None:
            context = {}
        base_func = super(StockMoveSplit, self).split
        res = base_func(cr, uid, ids, move_ids, context)
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                product_uom = move.product_uom
                if data.use_exist:
                    lines = [l for l in data.line_exist_ids if l]
                else:
                    lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    amount_actual = uom_obj._compute_qty_obj(
                        cr, uid, move.product_uom,
                        line.prodlot_id.stock_available,
                        product_uom, context=context)
                    if (data.location_id.usage == 'internal') and \
                            (quantity > (amount_actual or 0.0)):
                        raise orm.except_orm(
                            _('Insufficient Stock for Serial Number !'),
                            _('You are moving %.2f %s but only %.2f %s '
                              'available for this serial number.') %
                            (total_move_qty, move.product_uom.name,
                             amount_actual, move.product_uom.name))

        return res
