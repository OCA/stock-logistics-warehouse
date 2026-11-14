# Copyright 2026 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import models


class StockForecastedProductProduct(models.AbstractModel):
    _inherit = "stock.forecasted_product_product"

    def _get_quant_domain(self, location_ids, products):
        # OVERRIDE: leave the lock locations and their sub-locations out. They
        # sit next to the stock location, under the warehouse view location, so
        # their goods count as stock in transit and make the deliveries they
        # would cover show as available, while locked goods only leave on
        # request.
        warehouses = self.env["stock.warehouse"].search(
            [("wh_lock_stock_loc_id", "!=", False)]
        )
        lock_locations = self.env["stock.location"].search(
            [("id", "child_of", warehouses.wh_lock_stock_loc_id.ids)]
        )
        return super()._get_quant_domain(location_ids, products) + [
            ("location_id", "not in", lock_locations.ids)
        ]
