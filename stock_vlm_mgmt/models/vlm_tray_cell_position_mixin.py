# Copyright 2019 Camptocamp SA
# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VlmTrayCellPositionMixin(models.AbstractModel):
    _name = "vlm.tray.cell.position.mixin"
    _description = "Tray position helpers"

    tray_id = fields.Many2one(comodel_name="stock.location.vlm.tray")
    tray_type_id = fields.Many2one(comodel_name="stock.location.vlm.tray.type")
    tray_matrix = fields.Serialized(compute="_compute_tray_matrix")
    pos_x = fields.Integer()
    pos_y = fields.Integer()

    @api.depends("pos_x", "pos_y", "tray_type_id", "tray_id")
    def _compute_tray_matrix(self):
        self.tray_matrix = {}
        for record in self.filtered("tray_type_id"):
            cell_not_empty = self.env["stock.quant.vlm"].search_read(
                [("tray_id", "=", record.tray_id.id)], ["pos_x", "pos_y"]
            )
            tray_matrix = {
                "selected": [record.pos_x, record.pos_y],
                "cells": record.tray_type_id._generate_cells_matrix(),
                "first_empty_cell": False,
            }
            for position in cell_not_empty:
                # Let's be gentle with positioning errors.
                try:
                    tray_matrix["cells"][position["pos_y"]][position["pos_x"]] = 1
                except IndexError:
                    pass
            for row, cells in enumerate(tray_matrix["cells"]):
                if 0 not in cells:
                    continue
                tray_matrix["first_empty_cell"] = [cells.index(0), row]
                break
            record.tray_matrix = tray_matrix

    def tray_cell_center_position(self, pos_x=None, pos_y=None):
        """Center position in mm of a cell. Used to position the laser pointer.
        @return {tuple} millimeters from bottom-left corner (left, bottom)
        """
        if not self.tray_type_id:
            return 0, 0
        pos_x = pos_x or self.pos_x
        pos_y = pos_y or self.pos_y
        cell_width = self.tray_type_id.width_per_cell
        cell_depth = self.tray_type_id.depth_per_cell
        # pos_x and pos_y start at one, we want to count from 0
        from_left = pos_x * cell_width + (cell_width / 2)
        from_bottom = pos_y * cell_depth + (cell_depth / 2)
        return int(from_left), int(from_bottom)
