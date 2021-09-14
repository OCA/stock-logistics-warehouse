# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# @author: Sébastien Alix <sebastien.alix@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo import api, models


class ProductQtyByPackagingMixin(models.AbstractModel):
    """Allow displaying product qty by packaging."""

    _inherit = "product.qty_by_packaging.mixin"

    # Amazing.. unlike `api.depends`, `depends_context` cannot use a lambda
    # to delegate lookup. Hence we are forced to override and call super.
    @api.depends_context(
        "lang",
        "qty_by_pkg_total_units",
        "qty_by_packaging_type_fname",
        "qty_by_packaging_type_compact",
    )
    def _compute_product_qty_by_packaging_display(self):
        super()._compute_product_qty_by_packaging_display()
