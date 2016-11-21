# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def update_proposal(self):
        rfqs = self.filtered(lambda x: x.state == 'draft')
        rfqs.mapped('order_line').mapped('product_id').write(
            {'ultimate_purchase': False}
        )
        # set the partner's ultimate_purchase as the soonest
        # of all the UP's in the products where he is supplier.
        self.env['res.partner'].sql_update_partner()
        return True

    @api.model
    def create(self, vals):
        purchase = super(PurchaseOrder, self).create(vals=vals)
        purchase.update_proposal()
        return purchase

    @api.multi
    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)
        if result:
            self.update_proposal()
        return result
