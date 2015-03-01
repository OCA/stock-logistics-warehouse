# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields


class StockProductionLot(orm.Model):

    """
    Extend the stock.production.lot model.

    We add the retained_stock field to our model. It will be used to
    recaculate the available quantity of products. The available quantity
    of products is calculated inside a view.

    The view is named "stock.report.prodlots" the extended view is located
    in the report folder. The stock and search function for available quantity
    depends on this view. For that reason, only the view as to be rewritten
    to take in account the retained_stock field.
    """

    def _validate_retained_stock(self, cr, uid, ids, context=None):
        """Check that the retained stock is a positive number."""
        for lot in self.browse(cr, uid, ids, context=context):
            if lot.retained_stock < 0:
                return False

        return True

    _inherit = "stock.production.lot"

    _columns = {
        'retained_stock': fields.float(string='Retained stock'),
    }

    _constraints = [
        (
            _validate_retained_stock,
            'Retained stock cannot be negative',
            ['retained_stock'],
        ),
    ]
