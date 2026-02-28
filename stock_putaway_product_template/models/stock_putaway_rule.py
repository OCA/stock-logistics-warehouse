# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Sergio Teruel - Tecnativa
# Copyright 2020 Víctor Martínez - Tecnativa

from odoo import api, fields, models


class StockPutawayRule(models.Model):
    _inherit = "stock.putaway.rule"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        compute="_compute_product_tmpl_id",
        domain="[('id', '=', context.get('active_id', False))] "
        "if context.get('active_model') == 'product.template' "
        "else [('type', '!=', 'service')]",
        store=True,
        readonly=False,
        ondelete="cascade",
    )

    @api.depends("product_id")
    def _compute_product_tmpl_id(self):
        for rec in self:
            if rec.product_id:
                rec.product_tmpl_id = rec.product_id.product_tmpl_id
            else:
                params = self.env.context.get("params", {})
                if params.get("model", "") == "product.template" and params.get("id"):
                    rec.product_tmpl_id = params.get("id")

    def _get_putaway_location(
        self, product, quantity=0, package=None, packaging=None, qty_by_location=None
    ):
        rules = self.filtered(
            lambda r: not r.product_tmpl_id
            or r.product_tmpl_id == product.product_tmpl_id
        )
        return super(StockPutawayRule, rules)._get_putaway_location(
            product, quantity, package, packaging, qty_by_location=qty_by_location
        )
