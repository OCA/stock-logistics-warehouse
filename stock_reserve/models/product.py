# Copyright 2013 Camptocamp SA - Guewen Baconnier
# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    reservation_count = fields.Float(
        compute="_compute_reservation_count", string="# Sales"
    )

    def _compute_reservation_count(self):
        for product in self:
            product.reservation_count = sum(
                product.product_variant_ids.mapped("reservation_count")
            )

    def action_view_reservations(self):
        self.ensure_one()
        ref = "stock_reserve.action_stock_reservation_tree"
        product_ids = self.mapped("product_variant_ids.id")
        action_dict = self.env["ir.actions.act_window"]._for_xml_id(ref)
        action_dict["domain"] = [("product_id", "in", product_ids)]
        action_dict["context"] = {
            "search_default_draft": 1,
            "search_default_reserved": 1,
            "default_product_id": self.product_variant_ids[0].id,
        }
        return action_dict


class ProductProduct(models.Model):
    _inherit = "product.product"

    reservation_count = fields.Float(
        compute="_compute_reservation_count", string="# Sales"
    )
    reserve_qty = fields.Float(
        string="Reserve Quantity",
        compute="_compute_reserve_qty",
        search="_search_reserve_qty",
        digits="Product Unit of Measure",
        compute_sudo=False,
    )

    def _compute_reservation_count(self):
        for product in self:
            domain = [
                ("product_id", "=", product.id),
                ("state", "in", ["draft", "assigned"]),
            ]
            reservations = self.env["stock.reservation"].search(domain)
            product.reservation_count = sum(reservations.mapped("product_qty"))

    def _compute_reserve_qty(self):
        domain = [("product_id", "in", self.ids), ("state", "=", "assigned")]
        reservation_model = self.env["stock.reservation"]
        data = {
            item["product_id"][0]: item["product_uom_qty"]
            for item in reservation_model.read_group(
                domain, ["product_id", "product_uom_qty"], ["product_id"], orderby="id"
            )
        }
        for item in self:
            item.reserve_qty = float_round(
                data.get(item.id, 0.0), precision_rounding=item.uom_id.rounding
            )

    @api.depends("reserve_qty")
    def _compute_quantities(self):
        """Reduce from available the reserved quantity."""
        super()._compute_quantities()
        for item in self:
            item.qty_available -= item.reserve_qty

    def _search_reserve_qty(self, operator, value):
        return self._search_product_quantity(operator, value, "reserve_qty")

    def action_view_reservations(self):
        self.ensure_one()
        ref = "stock_reserve.action_stock_reservation_tree"
        action_dict = self.env["ir.actions.act_window"]._for_xml_id(ref)
        action_dict["domain"] = [("product_id", "=", self.id)]
        action_dict["context"] = {
            "search_default_draft": 1,
            "search_default_reserved": 1,
            "default_product_id": self.id,
        }
        return action_dict
