from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_length = fields.Float(help="Length of the picking")
    picking_height = fields.Float(help="Height of the picking")
    picking_width = fields.Float(help="Width of the picking")
    dimension_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Dimensions Unit of Measure",
        help="UoM for length, height, width",
        domain=lambda self: self._get_dimension_uom_domain(),
        default=lambda self: self._get_dimension_uom_default(),
    )
    dimension_uom_name = fields.Char(related="dimension_uom_id.name")
    volume = fields.Float(
        help="Computed volume for the picking",
        compute="_compute_volume",
        readonly=True,
        store=False,
    )

    def _get_dimension_uom_domain(self):
        domain = [("category_id", "=", self.env.ref("uom.uom_categ_length").id)]
        return domain

    def _get_dimension_uom_default(self):
        uom = self.env["product.template"]._get_length_uom_id_from_ir_config_parameter()
        return uom

    @api.depends(
        "picking_length",
        "picking_height",
        "picking_width",
        "dimension_uom_id",
    )
    def _compute_volume(self):
        meter_uom = self.env.ref("uom.product_uom_meter")
        meter3_uom = self.env.ref("uom.product_uom_cubic_meter")
        for p in self:
            volume = 0.0
            if p.picking_length and p.picking_height and p.picking_width:
                # compute volume in a known uom (meters3)
                # and then convert the result to the selected uom
                m_length = p.dimension_uom_id._compute_quantity(
                    p.picking_length, meter_uom
                )
                m_width = p.dimension_uom_id._compute_quantity(
                    p.picking_width, meter_uom
                )
                m_heigth = p.dimension_uom_id._compute_quantity(
                    p.picking_height, meter_uom
                )

                volume_m3 = m_length * m_width * m_heigth
                volume = meter3_uom._compute_quantity(volume_m3, p.volume_uom_id)
            p.volume = volume
