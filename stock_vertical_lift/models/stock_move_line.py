# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def fetch_vertical_lift_tray_source(self):
        self.ensure_one()
        self.location_id.fetch_vertical_lift_tray()
        return {"type": "ir.actions.do_nothing"}

    def fetch_vertical_lift_tray_dest(self):
        self.ensure_one()
        self.location_dest_id.fetch_vertical_lift_tray()
        return {"type": "ir.actions.do_nothing"}
