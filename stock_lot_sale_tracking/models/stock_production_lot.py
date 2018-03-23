# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    sale_tracking_ids = fields.One2many(
        comodel_name='stock.lot.sale.tracking.report',
        string="Customers Deliveries",
        inverse_name='lot_id'
    )
