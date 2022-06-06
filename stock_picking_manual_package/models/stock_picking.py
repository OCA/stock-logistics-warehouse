# Copyright 2022 Sergio Teruel - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.tools import config


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def put_in_pack(self):
        if (
            config["test_enable"]
            and not self.env.context.get("test_manual_package", False)
        ) or self.env.context.get("skip_manual_package", False):
            return super().put_in_pack()
        action = self.env.ref(
            "stock_picking_manual_package.action_manual_package_wiz"
        ).read()[0]
        wiz = self.env["stock.picking.manual.package.wiz"].create(
            {"picking_id": self.id}
        )
        action["res_id"] = wiz.id
        return action

    def _put_in_pack(self, move_line_ids):
        nbr_lines_into_package = self.env.context.get("nbr_lines_into_package", False)
        if nbr_lines_into_package:
            move_line_ids = move_line_ids[:nbr_lines_into_package]
        return super()._put_in_pack(move_line_ids)
