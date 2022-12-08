# Copyright 2019 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Inventory(models.Model):
    _inherit = "stock.inventory"

    exclude_sublocation = fields.Boolean(
        string="Exclude Sublocations",
        default=False,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _get_all_quants(self, locations):
        res = super()._get_all_quants(locations)
        if not self.exclude_sublocation:
            return res
        return self.env["stock.quant"].search(
            [("location_id", "in", locations.mapped("id"))]
        )

    def _get_manual_quants(self, locations):
        res = super()._get_manual_quants(locations)
        if not self.exclude_sublocation:
            return res
        return self.env["stock.quant"].search(
            [
                ("product_id", "in", self.product_ids.ids),
                ("location_id", "in", locations.mapped("id")),
            ]
        )

    def _get_one_quant(self, locations):
        res = super()._get_one_quant(locations)
        if not self.exclude_sublocation:
            return res
        return self.env["stock.quant"].search(
            [
                ("product_id", "in", self.product_ids.ids),
                ("location_id", "in", locations.mapped("id")),
            ]
        )

    def _get_lot_quants(self, locations):
        res = super()._get_lot_quants(locations)
        if not self.exclude_sublocation:
            return res
        return self.env["stock.quant"].search(
            [
                ("product_id", "in", self.product_ids.ids),
                ("lot_id", "in", self.lot_ids.ids),
                ("location_id", "in", locations.mapped("id")),
            ]
        )

    def _get_category_quants(self, locations):
        res = super()._get_category_quants(locations)
        if not self.exclude_sublocation:
            return res
        return self.env["stock.quant"].search(
            [
                ("location_id", "in", locations.mapped("id")),
                "|",
                ("product_id.categ_id", "=", self.category_id.id),
                ("product_id.categ_id", "in", self.category_id.child_id.ids),
            ]
        )
