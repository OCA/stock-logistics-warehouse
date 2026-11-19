# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models

STOCK_TYPE_LOCK = "lock"


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def _get_stock_types(self):
        # OVERRIDE: the lock stock type is the warehouse lock location
        res = super()._get_stock_types()
        res[STOCK_TYPE_LOCK] = {
            "wh_location_field": "wh_lock_stock_loc_id",
            "missing_message": self.env._(
                "No Lock Location is set on warehouse %(warehouse)s",
                warehouse=self.display_name,
            ),
        }
        return res
