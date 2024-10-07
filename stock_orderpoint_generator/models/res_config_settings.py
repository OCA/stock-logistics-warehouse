# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_product_domain = fields.Boolean(
        config_parameter="stock_orderpoint_generator.use_product_domain",
        string="Use product domain in Reordering Rule Templates",
        help="If checked, the product domain will be used to filter the products "
        "for which the reordering rules will be created.",
    )
