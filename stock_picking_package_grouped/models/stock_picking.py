# Copyright 2021 Sergio Teruel - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _put_in_pack(self, move_line_ids):
        package = False
        for picking in self:
            if picking.picking_type_id.package_grouping == "line":
                for move_line in move_line_ids:
                    package = super(StockPicking, picking)._put_in_pack(move_line)
            else:
                package = super(StockPicking, picking)._put_in_pack(move_line_ids)
        return package
