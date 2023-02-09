from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    kanban_card_count = fields.Integer(
        "# Kanban Cards", compute="_compute_kanban_card_count", compute_sudo=False
    )

    def _compute_kanban_card_count(self):
        for product in self:
            count = 0
            for variant in product.product_variant_ids:
                count += self.env["stock.request.kanban"].search_count(
                    [("product_id", "=", variant.id)]
                )
            product.kanban_card_count = count

    def action_view_kanban_cards(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_request_kanban.stock_request_kanban_action"
        )
        action["context"] = {"default_product_id": self.product_variant_id.id}
        action["domain"] = [
            ("active", "=", True),
            ("product_template_id", "=", self.id),
        ]
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    kanban_card_count = fields.Integer(
        "# Kanban Cards", compute="_compute_kanban_card_count", compute_sudo=False
    )

    def _compute_kanban_card_count(self):
        for product in self:
            product.kanban_card_count += self.env["stock.request.kanban"].search_count(
                [("product_id", "=", product.id)]
            )

    def action_view_kanban_cards(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_request_kanban.stock_request_kanban_action"
        )
        action["context"] = {"default_product_id": self.id}
        action["domain"] = [("active", "=", True), ("product_id", "=", self.id)]
        return action
