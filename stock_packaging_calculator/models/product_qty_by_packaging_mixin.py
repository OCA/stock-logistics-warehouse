# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# @author: Sébastien Alix <sebastien.alix@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo import api, fields, models


class ProductQtyByPackagingMixin(models.AbstractModel):
    """Allow displaying product qty by packaging."""

    _name = "product.qty_by_packaging.mixin"
    _description = "Product Qty By Packaging (Mixin)"

    _qty_by_pkg__product_field_name = "product_id"
    _qty_by_pkg__qty_field_name = None

    product_qty_by_packaging_display = fields.Char(
        compute="_compute_product_qty_by_packaging_display", string="Qty by packaging"
    )

    def _product_qty_by_packaging_display_depends(self):
        depends = []
        if self._qty_by_pkg__product_field_name:
            depends.append(self._qty_by_pkg__product_field_name)
        if self._qty_by_pkg__qty_field_name:
            depends.append(self._qty_by_pkg__qty_field_name)
        return depends

    @api.depends_context("lang", "qty_by_pkg_total_units", "qty_by_pkg_only_packaging")
    @api.depends(lambda self: self._product_qty_by_packaging_display_depends())
    def _compute_product_qty_by_packaging_display(self):
        include_total_units = self.env.context.get("qty_by_pkg_total_units", False)
        only_packaging = self.env.context.get("qty_by_pkg_only_packaging", False)
        for record in self:
            value = ""
            product = record._qty_by_packaging_get_product()
            if product:
                value = product.product_qty_by_packaging_as_str(
                    record._qty_by_packaging_get_qty(),
                    include_total_units=include_total_units,
                    only_packaging=only_packaging,
                )
            record.product_qty_by_packaging_display = value

    def _qty_by_packaging_get_product(self):
        return self[self._qty_by_pkg__product_field_name]

    def _qty_by_packaging_get_qty(self):
        return self[self._qty_by_pkg__qty_field_name]
