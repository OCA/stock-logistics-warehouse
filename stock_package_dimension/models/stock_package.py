# Copyright 2026 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockPackage(models.Model):
    _inherit = "stock.package"

    _positive_height = models.Constraint(
        "CHECK(height>=0)",
        "Height must be positive",
    )
    _positive_width = models.Constraint(
        "CHECK(width>=0)",
        "Width must be positive",
    )
    _positive_length = models.Constraint(
        "CHECK(packaging_length>=0)",
        "Length must be positive",
    )
    _positive_weight = models.Constraint(
        "CHECK(weight>=0)",
        "Weight must be positive",
    )
    height = fields.Integer()
    width = fields.Integer()
    packaging_length = fields.Integer(string="Length")

    length_uom_id = fields.Many2one(
        "uom.uom",
        "Dimensions Units of Measure",
        help="UoM for packaging length, height, width (based on lenght UoM)",
        default=lambda self: self.env[
            "product.template"
        ]._get_length_uom_id_from_ir_config_parameter(),
    )
    length_uom_name = fields.Char(
        string="Length unit of measure label",
        related="length_uom_id.name",
    )

    weight = fields.Float()
    weight_uom_id = fields.Many2one(
        "uom.uom",
        string="Weight Units of Measure",
        help="Weight Unit of Measure",
        default=lambda self: self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter(),
    )

    weight_uom_name = fields.Char(
        string="Weight unit of measure label",
        related="weight_uom_id.name",
    )

    volume = fields.Float(
        digits=(8, 4),
        compute="_compute_volume",
        help="The Packaging volume",
    )

    volume_uom_id = fields.Many2one(
        "uom.uom",
        string="Volume Units of Measure",
        help="Packaging volume unit of measure",
        default=lambda self: self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter(),
    )

    volume_uom_name = fields.Char(
        string="Volume Unit of Measure label",
        related="volume_uom_id.name",
    )

    @api.depends(
        "packaging_length", "width", "height", "length_uom_id", "volume_uom_id"
    )
    def _compute_volume(self):
        for packaging in self:
            packaging.volume = packaging._calculate_volume(
                packaging.packaging_length,
                packaging.height,
                packaging.width,
                packaging.length_uom_id,
                packaging.volume_uom_id,
            )

    def _calculate_volume(
        self, packaging_length, height, width, length_uom_id, volume_uom_id
    ):
        volume_m3 = 0
        if packaging_length and height and width and length_uom_id:
            length_m = self.convert_to_meters(packaging_length, length_uom_id)
            height_m = self.convert_to_meters(height, length_uom_id)
            width_m = self.convert_to_meters(width, length_uom_id)
            volume_m3 = length_m * height_m * width_m
        volume_in_volume_uom = self.convert_to_volume_uom(volume_m3, volume_uom_id)
        return volume_in_volume_uom

    def convert_to_meters(self, measure, length_uom_id):
        uom_meters = self.env.ref("uom.product_uom_meter")
        return length_uom_id._compute_quantity(
            qty=measure,
            to_unit=uom_meters,
            round=False,
        )

    def convert_to_volume_uom(self, measure, volume_uom_id):
        uom_m3 = self.env.ref("uom.product_uom_cubic_meter")
        return uom_m3._compute_quantity(
            qty=measure,
            to_unit=volume_uom_id,
            round=False,
        )
