from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    portal_visible_products_domain = fields.Char(
        string="Portal Visible Products",
        help="Domain which defines which products can be visible on portal. "
        "By default all products.",
        config_parameter="stock_available_portal.portal_visible_products_domain",
    )
    portal_visible_users = fields.Char(
        string="Visible to Users",
        help="Domain which defines which users can see products. By default all users.",
        config_parameter="stock_available_portal.portal_visible_users",
    )
