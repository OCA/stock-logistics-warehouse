# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class VerticalLiftOperationInventory(models.Model):
    _name = 'vertical.lift.operation.inventory'
    _inherit = 'vertical.lift.operation.base'
    _description = 'Vertical Lift Operation Inventory'
