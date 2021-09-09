# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import _, api, fields, models


class MeasuringWizardLine(models.TransientModel):
    _name = "measuring.wizard.line"
    _description = "measuring Wizard Line"
    _order = "sequence"

    scan_requested = fields.Boolean()
    wizard_id = fields.Many2one("measuring.wizard")
    sequence = fields.Integer()
    name = fields.Char("Packaging", readonly=True)
    qty = fields.Float("Quantity")
    max_weight = fields.Float("Weight (kg)", readonly=True)
    packaging_length = fields.Integer("Length (mm)", readonly=True)
    width = fields.Integer("Width (mm)", readonly=True)
    height = fields.Integer("Height (mm)", readonly=True)
    volume = fields.Float(
        "Volume (m³)",
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
    )
    barcode = fields.Char("GTIN")
    packaging_id = fields.Many2one(
        "product.packaging", string="Packaging (rel)", readonly=True
    )
    packaging_type_id = fields.Many2one("product.packaging.type", readonly=True)
    is_unit_line = fields.Boolean(readonly=True)
    required = fields.Boolean(related="packaging_type_id.required", readonly=True)
    is_measured = fields.Boolean()

    @api.depends("packaging_length", "width", "height")
    def _compute_volume(self):
        for line in self:
            line.volume = (
                line.packaging_length * line.width * line.height
            ) / 1000.0 ** 3

    def measuring_select_for_measure(self):
        """Current line has been selected for measurement

        This implies that the device is acquired and locked,
        and the packaging is assigned the device."""
        self.ensure_one()
        success = True
        if not self.packaging_id and not self.is_unit_line:
            pack_vals = {
                "name": self.name,
                "packaging_type_id": self.packaging_type_id.id,
                "product_id": self.wizard_id.product_id.id,
            }
            pack = self.env["product.packaging"].create(pack_vals)
            self.packaging_id = pack.id
        if self.wizard_id.device_id._is_being_used():
            self.wizard_id._notify(_("Measurement machine already in use."))
            success = False

        if success:
            self.scan_requested = True
            device = self.wizard_id.device_id
            self.packaging_id._measuring_device_assign(device)
        return success

    def measuring_select_for_measure_cancel(self):
        """Current line has been de-selected for measurement

        This implies that the packaging clears is assigned device."""
        self.ensure_one()
        self.scan_requested = False
        self.packaging_id._measuring_device_release()
        return True
