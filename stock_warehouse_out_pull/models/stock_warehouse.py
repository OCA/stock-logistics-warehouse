# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    delivery_pull = fields.Boolean(
        string="Outgoing Pull Rules",
        help="Configure the outgoing route with pull rules (ship -> pack -> pick).",
        default=False,
    )

    def get_rules_dict(self):
        # Override to adapt multi-steps delivery routing
        res = super().get_rules_dict()
        customer_loc, supplier_loc = self._get_partner_locations()
        for warehouse in self:
            if not warehouse.delivery_pull:
                continue
            # Values coming from Odoo 17.0
            res[warehouse.id]["pick_ship"] = [
                self.Routing(
                    warehouse.lot_stock_id,
                    warehouse.wh_output_stock_loc_id,
                    warehouse.pick_type_id,
                    "pull",
                ),
                self.Routing(
                    warehouse.wh_output_stock_loc_id,
                    customer_loc,
                    warehouse.out_type_id,
                    "pull",
                ),
            ]
            res[warehouse.id]["pick_pack_ship"] = [
                self.Routing(
                    warehouse.lot_stock_id,
                    warehouse.wh_pack_stock_loc_id,
                    warehouse.pick_type_id,
                    "pull",
                ),
                self.Routing(
                    warehouse.wh_pack_stock_loc_id,
                    warehouse.wh_output_stock_loc_id,
                    warehouse.pack_type_id,
                    "pull",
                ),
                self.Routing(
                    warehouse.wh_output_stock_loc_id,
                    customer_loc,
                    warehouse.out_type_id,
                    "pull",
                ),
            ]
        return res

    def _get_routes_values(self):
        # Override to trigger the delivery route config update when
        # `delivery_pull` field is updated
        res = super()._get_routes_values()
        if "delivery_route_id" in res:
            res["delivery_route_id"]["depends"].append("delivery_pull")
        return res
