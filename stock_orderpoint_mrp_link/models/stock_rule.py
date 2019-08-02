# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        result = super(StockRule, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id,
            name, origin, values, bom
        )
        if 'orderpoint_id' in values:
            result['orderpoint_id'] = values['orderpoint_id'].id
        elif 'orderpoint_ids' in values:
            # We take the always first value as in case of chain procurements,
            # the procurements are resolved first and then the moves are
            # merged. Thus here we are going to have only one OP in
            # in orderpoint_ids.
            result['orderpoint_id'] = values['orderpoint_ids'][0].id
        return result
