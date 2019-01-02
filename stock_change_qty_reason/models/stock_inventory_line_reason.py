# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockInventoryLineReason(models.Model):

    _name = 'stock.inventory.line.reason'

    name = fields.Char('Reason Name')
    description = fields.Text('Reason Description')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)',
         'You cannot have two reason with the same name.'),
    ]
