# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    tray_source_matrix = Serialized(
        string="Source Cell", compute="_compute_tray_matrix"
    )
    tray_dest_matrix = Serialized(
        string="Destination Cell", compute="_compute_tray_matrix"
    )

    @api.depends("location_id", "location_dest_id")
    def _compute_tray_matrix(self):
        for record in self:
            record.tray_source_matrix = record.location_id.tray_matrix
            record.tray_dest_matrix = record.location_dest_id.tray_matrix

    def _action_show_tray(self, location_from):
        assert location_from in ("source", "dest")
        self.ensure_one()
        view = self.env.ref("stock_location_tray.view_stock_move_line_tray")
        context = self.env.context.copy()
        if location_from == "source":
            name = _("Source Tray")
            context["show_source_tray"] = True
        else:
            name = _("Destination Tray")
            context["show_dest_tray"] = True
        return {
            "name": name,
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "stock.move.line",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": context,
        }

    def action_show_source_tray(self):
        return self._action_show_tray("source")

    def action_show_dest_tray(self):
        return self._action_show_tray("dest")
