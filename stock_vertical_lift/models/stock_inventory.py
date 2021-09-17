# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    vertical_lift_done = fields.Boolean(default=False)
    # Field used to sort lines by tray on the inventory scan screen, so entire
    # trays are processed one after the other
    vertical_lift_tray_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_vertical_lift_tray_id",
        readonly=True,
        store=True,
    )

    @api.depends("location_id.vertical_lift_kind")
    def _compute_vertical_lift_tray_id(self):
        for line in self:
            if line.location_id.vertical_lift_kind == "cell":
                # The parent of the cell is the tray.
                line.vertical_lift_tray_id = line.location_id.location_id
            else:
                line.vertical_lift_tray_id = False
