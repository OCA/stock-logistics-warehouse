# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint',
        index=True,
        string="Reordering rule"
    )
