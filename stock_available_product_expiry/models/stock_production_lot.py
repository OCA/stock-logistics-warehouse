# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    removal_date = fields.Datetime(
        index=True,
    )
