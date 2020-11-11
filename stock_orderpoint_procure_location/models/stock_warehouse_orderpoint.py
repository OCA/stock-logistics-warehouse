# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    procure_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Procurement Location",
        domain="[('usage', '=', 'internal')]",
    )

    def _prepare_procurement_values(
        self, product_qty, date=False, group=False
    ):
        """ Set the procure location
        """
        res = super(Orderpoint, self)._prepare_procurement_values(
            product_qty, date, group
        )
        if self.procure_location_id:
            res["procure_location_id"] = self.procure_location_id
        return res
