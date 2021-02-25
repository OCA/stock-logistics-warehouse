from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    scan_device_id = fields.Many2one(
        "cubiscan.device",
        copy=False,
        string="Device which will scan the package",
        help="Technical field set when an operator uses "
        "the device to scan this package",
    )
