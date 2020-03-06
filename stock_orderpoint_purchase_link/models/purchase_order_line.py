# Copyright 2018-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    orderpoint_ids = fields.Many2many(
        comodel_name="stock.warehouse.orderpoint",
        string="Orderpoints",
        copy=False,
        readonly=True,
    )
