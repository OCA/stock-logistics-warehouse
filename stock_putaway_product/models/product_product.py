# Copyright 2018 Camptocamp SA
# Copyright 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_product_putaway_ids = fields.One2many(
        comodel_name="stock.fixed.putaway.strat",
        inverse_name="product_id",
        string="Product putaway strategies by product",
    )
