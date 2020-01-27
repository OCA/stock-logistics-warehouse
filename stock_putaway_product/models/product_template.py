# Copyright 2018 Camptocamp SA
# Copyright 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_tmpl_putaway_ids = fields.One2many(
        comodel_name="stock.fixed.putaway.strat",
        inverse_name="product_tmpl_id",
        string="Product putaway strategies by product",
    )

    product_putaway_categ_ids = fields.Many2many(
        comodel_name="stock.fixed.putaway.strat",
        string="Product putaway strategies by category",
        compute="_compute_putaway_categ_ids",
    )

    @api.depends("categ_id")
    def _compute_putaway_categ_ids(self):
        for rec in self:
            fixed_putaway_strats = self.env[
                "stock.fixed.putaway.strat"
            ].search([("category_id", "=", rec.categ_id.id), ])
            rec.product_putaway_categ_ids = fixed_putaway_strats
