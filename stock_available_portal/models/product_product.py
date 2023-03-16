from odoo import api, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "portal.mixin"]

    def _compute_access_url(self):
        """Compute access url for portal view"""
        for rec in self:
            rec.access_url = "/my/products/{}".format(rec.id)

    @api.model
    def get_config_domain(self, key):
        """Get domain using config key"""
        try:
            return safe_eval(self.env["ir.config_parameter"].sudo().get_param(key, []))
        except (TypeError, SyntaxError, NameError, ValueError):
            return []

    @api.model
    def check_product_portal_access(self):
        """Check access to portal products for user"""
        self = self.sudo()
        user_has_group = self.env.user.has_group
        if not (
            user_has_group("base.group_system") or user_has_group("base.group_portal")
        ):
            return False
        domain = self.get_config_domain("stock_available_portal.portal_visible_users")
        return (
            bool(
                self.env["res.users"].search(
                    expression.AND([domain, [("id", "=", self.env.user.id)]]), limit=1
                )
            )
            if domain or domain == []
            else False
        )

    @api.model
    def get_portal_products(self, filter_domain, **kwargs):
        """Get portal products"""
        self = self.sudo()
        if not self.check_product_portal_access():
            return self
        domain = self.get_config_domain(
            "stock_available_portal.portal_visible_products_domain"
        )
        if not domain and domain != []:
            return self
        return self.search(expression.AND([domain, filter_domain]), **kwargs)
