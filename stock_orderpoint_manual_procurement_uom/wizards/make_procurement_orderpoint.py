# Copyright 2018-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class MakeProcurementOrderpoint(models.TransientModel):
    _inherit = "make.procurement.orderpoint"

    @api.model
    def _prepare_item(self, orderpoint):
        vals = super(MakeProcurementOrderpoint, self)._prepare_item(orderpoint)
        if orderpoint.procure_uom_id:
            product_uom = orderpoint.procure_uom_id
            vals["uom_id"] = product_uom.id
        return vals


class MakeProcurementOrderpointItem(models.TransientModel):
    _inherit = "make.procurement.orderpoint.item"

    @api.onchange("uom_id")
    def onchange_uom_id(self):
        for rec in self:
            uom = rec.orderpoint_id.procure_uom_id or rec.orderpoint_id.product_uom
            rec.qty = uom._compute_quantity(
                rec.orderpoint_id.procure_recommended_qty, rec.uom_id
            )
