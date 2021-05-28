# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _packaging_name_getter(self, packaging):
        return packaging.packaging_type_id.name

    def _qty_by_packaging_as_str(self, packaging, qty):
        # By default use packaging type code
        qty_by_packaging_type_fname = self.env.context.get(
            "qty_by_packaging_type_fname", "code"
        )
        compact_mode = self.env.context.get("qty_by_packaging_type_compact", True)
        sep = "" if compact_mode else " "
        # Override to use packaging type code
        if packaging and packaging.packaging_type_id:
            name = packaging.packaging_type_id[qty_by_packaging_type_fname]
            return f"{qty}{sep}{name}"
        else:
            return super()._qty_by_packaging_as_str(packaging, qty)
