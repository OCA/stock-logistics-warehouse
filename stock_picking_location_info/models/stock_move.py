# Copyright 2019  Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    location_putaway_dest_id = fields.Many2one(
        'stock.location',
        string='Final Location',
        compute='compute_location_putaway_dest_id',
        readonly=True)

    @api.multi
    def compute_location_putaway_dest_id(self):
        for record in self:
            if record.location_dest_id and record.product_id:
                record.location_putaway_dest_id = \
                    record.location_dest_id.get_putaway_strategy(
                        record.product_id) or record.location_dest_id
