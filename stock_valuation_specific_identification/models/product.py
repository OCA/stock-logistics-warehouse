# Copyright 2024 Matt Taylor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    specific_ident_cost = fields.Boolean(
        related="categ_id.property_specific_ident_cost",
        readonly=True,
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    # TODO: Handle lots/serials on change of cost method.
    #  See the superseding write() method of product.product model in file
    #  stock_account/models/product.py.

    def action_revaluation(self):
        self.ensure_one()
        if not self.specific_ident_cost or self.product_tmpl_id.tracking == "none":
            return super(ProductProduct, self).action_revaluation()
        else:
            raise UserError(_("This product must be revalued by lot/serial"))
