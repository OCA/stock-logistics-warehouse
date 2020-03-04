#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import models, fields, api


class ComputedPurchaseOrderLine(models.Model):
    _inherit = 'computed.purchase.order.line'

    # Columns section
    displayed_product_history_ids = fields.Many2many(
        'product.history', related='product_id.product_history_ids',
        string='Product History')

    # Private section
    @api.multi
    def view_history(self):
        action = self.env.ref('product_history_for_cpo.action_view_history').read()[0]
        ids = []
        history_ranges = []
        for cpol in self:
            ids.append(cpol.product_id.id)
            history_ranges.append(cpol.product_id.history_range)
        action['domain'] = [
            ('product_id', 'in', ids),
            ('history_range', 'in', history_ranges)]
        return action