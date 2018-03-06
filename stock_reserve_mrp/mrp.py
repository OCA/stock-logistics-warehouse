# -*- coding: utf-8 -*-
# © 2015 ClearCorp S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class mrp_bom(models.Model):
        _inherit = "mrp.bom"

        reserve_stock = fields.Boolean('Reserve Finished Goods', default=True)


class mrp_production(models.Model):
    _inherit = "mrp.production"

    reserve_stock = fields.Boolean('Reserve Finished Goods', default=True)

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
            if not context:
                context = {}
            ctx = context.copy()
            ctx.update({'reserve_stock': True})
            res = super(mrp_production, self).action_produce(
                cr, uid, production_id, production_qty,
                production_mode, wiz=wiz, context=ctx)
            return res
        return super(mrp_production, self).action_produce(
            cr, uid, production_id, production_qty, production_mode,
            wiz=wiz, context=context)
