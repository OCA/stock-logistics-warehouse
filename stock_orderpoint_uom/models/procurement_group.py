# Copyright (C) 2018 - TODAY, Open Source Integrators
#   (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, name,
            origin, values):
        if 'orderpoint_id' in values:
            orderpoint = values.get('orderpoint_id')
            product_qty = orderpoint.product_uom._compute_quantity(
                product_qty, orderpoint.procure_uom_id)
        return super(ProcurementGroup, self).run(product_id, product_qty,
                                                 orderpoint.procure_uom_id,
                                                 location_id,
                                                 name, origin, values)
