# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockDemandEstimateSheetLine(models.TransientModel):
    _name = "stock.demand.estimate.sheet.line"
    _description = "Stock Demand Estimate Sheet Line"

    estimate_id = fields.Many2one(comodel_name="stock.demand.estimate")
    date_range_id = fields.Many2one(comodel_name="date.range", string="Period")
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Stock Location"
    )
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    value_x = fields.Char(string="Period Name")
    value_y = fields.Char(string="Product Name")
    product_uom = fields.Many2one(comodel_name="uom.uom", string="Unit of measure")
    product_uom_qty = fields.Float(string="Quantity", digits="Product UoM")
