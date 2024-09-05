# Copyright 2024 Ivan Perez <iperez@coninpe.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    has_quants = fields.Boolean(
        name="Has Quants",
        compute="_compute_has_quants",
        precompute=True,
        store=True,
    )

    lot_ids = fields.One2many("stock.lot", "product_id", string="Lots", copy=False)

    @api.depends("qty_available", "incoming_qty", "outgoing_qty", "stock_quant_ids")
    def _compute_has_quants(self):
        for record in self:
            record.has_quants = record.stock_quant_ids and True or False
