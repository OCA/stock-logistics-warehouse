# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        context = self.env.context
        if context.get("product_id") or context.get("lot_id"):
            quants = self.env["stock.quant"].search(
                [
                    ("product_id", "=", context.get("product_id")),
                    ("lot_id", "=", context.get("lot_id")),
                ]
            )
            locations = quants.mapped("location_id")
            if not locations:
                company_id = context.get("default_company_id") or self.env.company.id
                warehouse = self.env["stock.warehouse"].search(
                    [("company_id", "=", company_id)], limit=1
                )
                locations = warehouse.lot_stock_id
            args += [("id", "in", locations.ids)]
        return super(StockLocation, self)._search(
            args, offset, limit, order, count=count, access_rights_uid=access_rights_uid
        )
