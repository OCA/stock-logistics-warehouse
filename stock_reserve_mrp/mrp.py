# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
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

from openerp import models, fields, api


class mrp_bom(models.Model):
        _inherit = "mrp.bom"

        reserve_stock = fields.Boolean('Reserve Finished Goods')


class mrp_production(models.Model):
    _inherit = "mrp.production"

    reserve_stock = fields.Boolean('Reserve Finished Goods')

    @api.multi
    def product_id_change(self, product_id, product_qty=0):
        res = super(mrp_production, self).product_id_change(
            product_id=product_id, product_qty=product_qty)
        if self.bom_id.reserve_stock:
            res['value']['reserve_stock'] = self.bom_id.reserve_stock
        return res

    def action_produce(self, cr, uid, production_id, production_qty,
                       production_mode, wiz=False, context=None):
        production = self.browse(cr, uid, production_id, context=context)
        if production.reserve_stock is True:
            ctx = context.copy()
            ctx.update({'reserve_stock': True})
            res = super(mrp_production, self).action_produce(
                cr, uid, production_id, production_qty,
                production_mode, wiz=wiz, context=ctx)
            return res
        return super(mrp_production, self).action_produce(
            cr, uid, production_id, production_qty, production_mode,
            wiz=wiz, context=context)
