# Copyright 2024 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockReserveAreaInit(models.TransientModel):
    _name = "stock.reserve.area.init"
    _description = "Stock Reserve Area Init"

    def action_reserve_area_init(self):
        self.env["stock.reserve.area"].action_initialize_reserve_area_data()
        return {"type": "ir.actions.act_window_close"}
