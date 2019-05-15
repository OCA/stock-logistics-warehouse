# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MakeProcurementOrderpointItem(models.TransientModel):
    _inherit = 'make.procurement.orderpoint.item'

    @api.model
    def _prepare_item(self, orderpoint):
        res = super(MakeProcurementOrderpointItem, self)._prepare_item(
            orderpoint)
        if orderpoint.location_dest_id:
            res['location_id'] = orderpoint.location_dest_id.id
        return res

