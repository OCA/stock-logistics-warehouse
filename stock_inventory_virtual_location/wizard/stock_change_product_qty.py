# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    virtual_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Virtual Adjustment Location',
        domain=[('usage', 'like', 'inventory')],
    )

    def _action_start_line(self):
        res = super(StockChangeProductQty, self)._action_start_line()
        if self.virtual_location_id:
            res.update({'virtual_location_id': self.virtual_location_id.id})
        return res
