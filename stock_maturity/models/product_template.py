# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    use_maturity_date = fields.Boolean()
