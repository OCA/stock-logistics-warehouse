# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, product_id, product_qty, product_uom, location_id, name,
            origin, values):
        if not origin or origin == '/':
            if 'orderpoint_id' in values:
                origin = values.get('orderpoint_id').name
            elif 'orderpoint_ids' in values:
                origin = ', '.join([x.name for x in values['orderpoint_ids']])
        else:
            if 'orderpoint_id' in values:
                if values['orderpoint_id'].name not in origin:
                    origin += ', %s' % values.get('orderpoint_id').name
            elif 'orderpoint_ids' in values:
                origin = '%s, %s' % (origin, ', '.join(
                    [x.name for x in values['orderpoint_ids'] if
                        x.name not in origin]))
        return super(ProcurementGroup, self).run(product_id, product_qty,
                                                 product_uom, location_id,
                                                 name, origin, values)
