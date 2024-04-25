# Copyright 2024 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    serial_auto_reserve = fields.Boolean(
        string="Do auto-reserve this product", default=False
    )
