# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


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
        action_dict = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_reserve.action_stock_reservation_tree"
        )
        product_ids = self.mapped("product_variant_ids.id")
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

    def _compute_reservation_count(self):
        for product in self:
            domain = [
                ("product_id", "=", product.id),
                ("state", "in", ["draft", "assigned"]),
            ]
            reservations = self.env["stock.reservation"].search(domain)
            product.reservation_count = sum(reservations.mapped("product_qty"))

    def action_view_reservations(self):
        self.ensure_one()
        action_dict = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_reserve.action_stock_reservation_tree"
        )
        action_dict["domain"] = [("product_id", "=", self.id)]
        action_dict["context"] = {
            "search_default_draft": 1,
            "search_default_reserved": 1,
            "default_product_id": self.id,
        }
        return action_dict
