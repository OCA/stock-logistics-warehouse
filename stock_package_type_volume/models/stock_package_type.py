# Copyright 2024 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    volume = fields.Float(
        digits=(8, 4),
        compute='_compute_volume',
        readonly=True,
        help='The Packaging volume',
    )

    volume_uom_id = fields.Many2one('uom.uom', string='Volume Units of Measure', compute='_compute_volume_uom')
    volume_uom_name = fields.Char(compute='_compute_volume_uom')

    def _compute_volume_uom(self):
        for package_id in self:
            package_id.volume_uom_id = self.env['product.template']._get_volume_uom_id_from_ir_config_parameter()
            package_id.volume_uom_name = package_id.volume_uom_id.name

    def convert_to_meters(self, measure, dimensional_uom):
        return dimensional_uom._compute_quantity(
            qty=measure,
            to_unit=self.env.ref('uom.product_uom_meter'),
            round=False,
        )

    def convert_to_volume_uom(self, measure, volume_uom_id):
        return self.env.ref('uom.product_uom_cubic_meter')._compute_quantity(
            qty=measure,
            to_unit=volume_uom_id,
            round=False,
        )

    @api.model
    def _calc_volume(self, packaging_length, height, width, length_uom_id, volume_uom_id):
        volume_m3 = 0

        if packaging_length and height and width and length_uom_id:
            length_m = self.convert_to_meters(packaging_length, length_uom_id)
            height_m = self.convert_to_meters(height, length_uom_id)
            width_m = self.convert_to_meters(width, length_uom_id)
            volume_m3 = length_m * height_m * width_m

        return self.convert_to_volume_uom(volume_m3, volume_uom_id)

    @api.depends('packaging_length', 'width', 'height', 'volume_uom_id')
    def _compute_volume(self):
        for package_id in self:
            package_id.volume = package_id._calc_volume(
                package_id.packaging_length,
                package_id.height,
                package_id.width,
                self.env['product.template']._get_length_uom_id_from_ir_config_parameter(),
                package_id.volume_uom_id,
            )
