# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.osv import expression


class StockLocationVlmTray(models.Model):
    _name = "stock.location.vlm.tray"
    _description = "Individual trays in a Vertical Lift Module"

    name = fields.Char()
    location_id = fields.Many2one(
        comodel_name="stock.location", domain=[("is_vlm", "=", True)]
    )
    tray_type_id = fields.Many2one(
        comodel_name="stock.location.vlm.tray.type", required=True
    )
    tray_matrix = fields.Serialized(compute="_compute_tray_matrix")
    is_full = fields.Boolean()

    @api.depends("tray_type_id")
    def _compute_tray_matrix(self):
        """Render empty and allocated cells"""
        # TODO: Unify computes and optimize query to do it in one shot
        for tray in self:
            cell_not_empty = self.env["stock.quant.vlm"].search_read(
                [("tray_id", "=", tray.id)], ["pos_x", "pos_y", "tray_id"]
            )
            tray_matrix = {
                "selected": [],
                "cells": tray.tray_type_id._generate_cells_matrix(),
                "first_empty_cell": [],
            }
            for position in cell_not_empty:
                # Let's be gentle with positioning errors.
                try:
                    tray_matrix["cells"][position["pos_y"]][position["pos_x"]] = 1
                # pylint: disable=except-pass
                except IndexError:
                    pass
            for row, cells in enumerate(tray_matrix["cells"]):
                if 0 not in cells:
                    continue
                tray_matrix["first_empty_cell"] = [cells.index(0), row]
                break
            tray.tray_matrix = tray_matrix

    def action_tray_content(self, pos_x=None, pos_y=None):
        """See the vlm quants belonging to the tray"""
        self.ensure_one()
        domain = [("tray_id", "=", self.id)]
        if (pos_x is not None) and (pos_y is not None):
            domain = expression.AND(
                [domain, [("pos_x", "=", pos_x), ("pos_y", "=", pos_y)]]
            )
        vlm_quant = self.env["stock.quant.vlm"].search(domain)
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_vlm_mgmt.location_quant_vlm_action"
        )
        self.env.ref("stock_vlm_mgmt.view_location_form")
        action["domain"] = [("id", "in", vlm_quant.ids)]
        action["context"] = dict(
            self.env.context,
            default_tray_id=self.id,
            default_location_id=self.location_id.id,
            vlm_inventory_mode=True,
        )
        view_id = self.env.ref("stock_vlm_mgmt.view_stock_quant_inventory_tree").id
        action.update(
            {
                "view_mode": "tree",
                "views": [
                    [view_id, "tree"] for view in action["views"] if view[1] == "tree"
                ],
            }
        )
        return action

    def action_tray_call(self):
        """Send to the VLM a special command that calls this tray"""
        data = self.location_id._prepare_vlm_request(
            task_type="count",
            carrier=self.name,
            info1=_(
                "%(user)s has requested a release of the trays from Odoo",
                user=self.env.user.name,
            ),
        )
        self.location_id.with_context(vlm_tray_call=True).send_vlm_request(data)
