# Copyright 2019 Camptocamp SA
# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv import expression


class StockLocationVlmTrayType(models.Model):
    _name = "stock.location.vlm.tray.type"
    _description = "VLM Tray configuration"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    rows = fields.Integer(required=True)
    cols = fields.Integer(required=True)
    width = fields.Integer(help="Width of the tray in mm")
    depth = fields.Integer(help="Depth of the tray in mm")
    height = fields.Integer(help="Height of the tray in mm")
    width_per_cell = fields.Float(compute="_compute_width_per_cell")
    depth_per_cell = fields.Float(compute="_compute_depth_per_cell")
    tray_matrix = fields.Serialized(compute="_compute_tray_matrix")

    @api.depends("width", "cols")
    def _compute_width_per_cell(self):
        for record in self:
            width = record.width
            if not width:
                record.width_per_cell = 0.0
                continue
            record.width_per_cell = width / record.cols

    @api.depends("depth", "rows")
    def _compute_depth_per_cell(self):
        for record in self:
            depth = record.depth
            if not depth:
                record.depth_per_cell = 0.0
                continue
            record.depth_per_cell = depth / record.rows

    @api.depends("rows", "cols")
    def _compute_tray_matrix(self):
        for record in self:
            # As we only want to show the disposition of
            # the tray, we generate a "full" tray, we'll
            # see all the boxes on the web widget.
            # (0 means empty, 1 means used)
            cells = self._generate_cells_matrix(default_state=1)
            record.tray_matrix = {"selected": [], "cells": cells}

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("name", operator, name), ("code", operator, name)]

        return self._search(
            expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid
        )

    def _generate_cells_matrix(self, default_state=0):
        return [[default_state] * self.cols for __ in range(self.rows)]
