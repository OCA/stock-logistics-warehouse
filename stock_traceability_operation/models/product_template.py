# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, exceptions
from openerp.tools.safe_eval import safe_eval


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def action_view_stock_moves(self):
        """Replace the action on stock moves with an action on the report"""
        action = super(ProductTemplate, self).action_view_stock_moves()
        if action['res_model'] != 'stock.move':
            raise exceptions.ValidationError(
                "An incompatible module returned an action for the wrong "
                "model.")
        domain = action.get('domain') and safe_eval(action['domain']) or []
        # The standard may return a default filter instead of a domain
        if action.get('context'):
            action_context = safe_eval(action['context'])
            if action_context.get('search_default_product_id'):
                domain.append(('product_id', '=',
                               action_context['search_default_product_id']))
        moves = self.env['stock.move'].search(domain)
        return moves.mapped('quant_ids').action_view_quant_history()
