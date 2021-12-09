# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.osv import expression

from odoo.addons.base_sparse_field.models.fields import Serialized


class StockLocationTrayType(models.Model):
    _name = "stock.location.tray.type"
    _description = "Stock Location Tray Type"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    rows = fields.Integer(required=True)
    cols = fields.Integer(required=True)

    width = fields.Integer(help="Width of the tray in mm")
    depth = fields.Integer(help="Depth of the tray in mm")
    height = fields.Integer(help="Height of the tray in mm")

    width_per_cell = fields.Float(compute="_compute_width_per_cell")
    depth_per_cell = fields.Float(compute="_compute_depth_per_cell")

    active = fields.Boolean(default=True)
    tray_matrix = Serialized(compute="_compute_tray_matrix")
    location_ids = fields.One2many(
        comodel_name="stock.location", inverse_name="tray_type_id"
    )

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

    @api.constrains("active")
    def _location_check_active(self):
        for record in self:
            if record.active:
                continue
            if record.location_ids:
                location_bullets = [
                    " - {}".format(location.display_name)
                    for location in record.location_ids
                ]
                raise exceptions.ValidationError(
                    _(
                        "The tray type {} is used by the following locations "
                        "and cannot be archived:\n\n{}"
                    ).format(record.name, "\n".join(location_bullets))
                )

    @api.constrains("rows", "cols")
    def _location_check_rows_cols(self):
        for record in self:
            if record.location_ids:
                location_bullets = [
                    " - {}".format(location.display_name)
                    for location in record.location_ids
                ]
                raise exceptions.ValidationError(
                    _(
                        "The tray type {} is used by the following locations, "
                        "it's size cannot be changed:\n\n{}"
                    ).format(record.name, "\n".join(location_bullets))
                )

    def open_locations(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_location_form"
        )
        action["domain"] = [("tray_type_id", "in", self.ids)]
        if len(self.ids) == 1:
            action["context"] = {"default_tray_type_id": self.id}
        return action
