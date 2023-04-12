# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class StockStorageCategoryCapacity(models.Model):

    _inherit = "stock.storage.category.capacity"

    def _get_display_name_attributes(self):
        """
        Adds the storage capacity attributes to compose the display name
        """
        self.ensure_one()
        attributes = []
        if self.product_id:
            attributes.append(_("Product: ") + self.product_id.name)
        if self.package_type_id:
            attributes.append(_("Package: ") + self.package_type_id.name)
        return attributes

    @api.model
    def _compute_display_name_depends(self):
        return [
            "storage_category_id.name",
            "quantity",
            "product_id.name",
            "package_type_id.name",
        ]

    @api.depends(lambda self: self._compute_display_name_depends())
    def _compute_display_name(self):
        for capacity in self:
            name = " ".join(
                [str(capacity.storage_category_id.name), "x " + str(capacity.quantity)]
            )
            attributes = capacity._get_display_name_attributes()
            if attributes:
                name += " ({attributes_display})".format(
                    attributes_display=" - ".join(attributes)
                )
            capacity.display_name = name
