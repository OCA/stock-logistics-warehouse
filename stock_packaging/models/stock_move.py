# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        if self.product_packaging and \
                self.rule_id and \
                self.rule_id.propagate_product_packaging:
            vals.update({'product_packaging': self.product_packaging.id})
        return vals
