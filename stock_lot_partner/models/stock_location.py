from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _get_warehouse(self):
        self.ensure_one()
        warehouse_obj = self.env["stock.warehouse"]
        location = self
        while location:
            warehouse = warehouse_obj.search(
                [("view_location_id", "=", location.id)], limit=1
            )
            if warehouse:
                return warehouse
            location = location.location_id
        return warehouse_obj.browse()
