# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _gather(self, product_or_template, *args, **kwargs):
        if isinstance(procurement.product_id, self.env["product.product"].__class__):
            return super()._gather(product_or_template, *args, **kwargs)

        quants = self.browse()
        for product in product_or_template.product_ids:
            quants |= self._gather(product, *args, kwargs)

        return quants._sort_gathered_record_from_product_template()

    def _sort_gathered_record_from_product_template(self):
        """allow to sort quants in different order to match business requirements
        FEFO / product.product attributes / ...
        """
        return self
