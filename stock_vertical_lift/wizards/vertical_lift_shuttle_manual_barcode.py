# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VerticalLiftShuttleManualBarcode(models.TransientModel):
    _name = "vertical.lift.shuttle.manual.barcode"
    _description = "Action to input a barcode"

    barcode = fields.Char(string="Barcode")

    def button_save(self):
        active_id = self.env.context.get("active_id")
        model = self.env.context.get("active_model")
        assert model
        record = self.env[model].browse(active_id).exists()
        if not record:
            return
        if self.barcode:
            record.on_barcode_scanned(self.barcode)
