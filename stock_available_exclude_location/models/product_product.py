# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    excluded_location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Locations to Exclude as Available",
        compute="_compute_excluded_location_ids",
        readonly=True,
    )

    @api.depends()
    def _compute_excluded_location_ids(self):
        self.update({"excluded_location_ids": False})
        stock_quants = self.env["stock.quant"].search(
            [
                ("product_id", "in", self.ids),
                ("on_hand", "=", True),
            ]
        )
        for product in self:
            product_quants = stock_quants.filtered(lambda x: x.product_id == product)
            if product_quants:
                company_ids = product_quants.mapped(lambda x: x.company_id)
                excluded_ids = company_ids.mapped(
                    lambda x: x.stock_excluded_location_ids
                )
                if excluded_ids:
                    for excluded_location in excluded_ids:
                        excluded_ids |= excluded_location.children_ids
                    product.excluded_location_ids = excluded_ids

    def _compute_quantities_dict(
        self, lot_id, owner_id, package_id, from_date=False, to_date=False
    ):
        context = dict(self._context, excluded_location_ids=self.excluded_location_ids)
        return super(
            ProductProduct, self.with_context(context)
        )._compute_quantities_dict(lot_id, owner_id, package_id, from_date, to_date)
