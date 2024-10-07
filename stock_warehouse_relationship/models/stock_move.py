# Copyright (C) 2019 Akretion
# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    warehouse_id = fields.Many2one(index=True)

    @api.model
    def _get_move_default_warehouse(self, vals):
        if vals.get("picking_type_id"):
            pick_type = self.env["stock.picking.type"].browse(vals["picking_type_id"])
            wh = pick_type.warehouse_id
        else:
            locations = self.env["stock.location"].browse(
                [vals["location_id"], vals["location_dest_id"]]
            )
            whs = locations.mapped("warehouse_id")
            wh = len(whs) <= 1 and whs or self.env["stock.warehouse"]
        return wh

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("warehouse_id"):
                wh = self._get_move_default_warehouse(vals)
                vals["warehouse_id"] = wh.id or False
        return super().create(vals_list)
