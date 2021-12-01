# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    discrepancy_amount_threshold = fields.Monetary(
        string="Maximum Discrepancy Amount Threshold",
        currency_field="discrepancy_amount_threshold_currency_id",
        help="Maximum Discrepancy Amount allowed for any product when doing "
             "an Inventory Adjustment. Threshold defined in involved Location "
             "has preference.",
    )
    discrepancy_amount_threshold_currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
