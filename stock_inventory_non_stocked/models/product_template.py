# Copyright 2024 Ivan Perez <iperez@coninpe.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    has_quants = fields.Boolean(
        name="Has Quants",
        compute="_compute_has_quants",
        store=True,
    )

    @api.depends("qty_available", "incoming_qty", "outgoing_qty")
    def _compute_has_quants(self):
        for record in self:
            record.has_quants = (
                self.env["stock.quant"].search_count([("product_id", "=", record.id)])
                > 0
            )

    lot_ids = fields.One2many("stock.lot", "product_id", string="Lots", copy=False)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockQuant, self).create(vals_list)
        res.product_id._compute_has_quants()
        return res
