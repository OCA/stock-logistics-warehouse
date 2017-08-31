# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockChangeStandardPrice(models.TransientModel):
    _inherit = "stock.change.standard.price"

    @api.model
    def default_get(self, fields):
        res = super(StockChangeStandardPrice, self).default_get(fields)

        product_or_template = self.env[self._context['active_model']].browse(
            self._context['active_id'])
        if 'counterpart_account_id' in fields:
            # We can only use one account here, so we use the decrease
            # account. It will be ignored anyway, because we'll use the
            # increase/decrease accounts defined in the product category.
            res['counterpart_account_id'] = product_or_template.categ_id. \
                property_inventory_revaluation_decrease_account_categ.id
        return res
