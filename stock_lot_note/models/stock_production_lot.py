# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    notes = fields.Text()
