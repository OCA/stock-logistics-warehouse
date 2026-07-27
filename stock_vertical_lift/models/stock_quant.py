# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    vertical_lift_done = fields.Boolean()

    def write(self, vals):
        # A new inventory date invalidates vertical_lift_done,
        # even if inventory_date=False
        if "inventory_date" in vals and "vertical_lift_done" not in vals:
            vals["vertical_lift_done"] = False
        return super().write(vals)

    # Field used to sort lines by tray on the inventory scan screen, so entire
    # trays are processed one after the other
    vertical_lift_tray_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_vertical_lift_tray_id",
        readonly=True,
        store=True,
    )

    def _update_available_quantity(self, *args, **kwargs):
        result = super()._update_available_quantity(*args, **kwargs)
        # We cannot have fields to depends on to invalidate this computed
        # fields on vertical.lift.operation.* models. But we know that when the
        # quantity of quant changes, we can invalidate the field
        models = ("vertical.lift.operation.pick", "vertical.lift.operation.put")
        for model in models:
            self.env[model].invalidate_model(["tray_qty"])
        return result

    @api.depends("location_id.vertical_lift_kind")
    def _compute_vertical_lift_tray_id(self):
        for line in self:
            if line.location_id.vertical_lift_kind == "cell":
                # The parent of the cell is the tray.
                line.vertical_lift_tray_id = line.location_id.location_id
            else:
                line.vertical_lift_tray_id = False
