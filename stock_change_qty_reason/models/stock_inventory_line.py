# Copyright 2016-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockInventoryLine(models.Model):
    """Class to inherit model stock.inventory.line"""
    _inherit = "stock.inventory.line"

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        """Function to super _get_move_value"""
        res = super(StockInventoryLine, self)._get_move_values(
            qty, location_id, location_dest_id, out)
        if res.get('origin'):
            res['origin'] = ' ,'.join(
                [res.get('origin'),
                 self.env.context.get('change_quantity_reason', False)])
        else:
            res['origin'] = self.env.context.get('change_quantity_reason',
                                                 False)
        return res
