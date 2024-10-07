# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    stock_excluded_location_ids = fields.Many2many(
        comodel_name="stock.location",
        related="company_id.stock_excluded_location_ids",
        string="Excluded Locations for Product Availability",
        help="Fill in this field to exclude locations for product available quantities.",
        readonly=False,
    )
