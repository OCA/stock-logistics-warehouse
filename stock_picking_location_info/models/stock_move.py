# Copyright 2019  Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    location_putaway_dest_id = fields.Many2one(
        'stock.location',
        string='Final Location',
        compute='compute_location_putaway_dest_id',
        readonly=True)

    def compute_location_putaway_dest_id(self):
        if self.location_dest_id and self.product_id:
            self.location_putaway_dest_id = \
                self.location_dest_id.get_putaway_strategy(self.product_id) \
                or self.location_dest_id
