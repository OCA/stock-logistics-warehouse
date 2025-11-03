# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        res = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        warehouse = self.warehouse_id
        if warehouse.calendar_id and self.delay:
            date = warehouse.wh_plan_days(values["date_planned"], -1 * self.delay)
            res["date"] = date
        return res

    def _get_push_new_date(self, move):
        warehouse = (
            self.warehouse_id or move.warehouse_id or move.picking_type_id.warehouse_id
        )
        if warehouse and warehouse.calendar_id and self.delay:
            return fields.Datetime.to_string(
                warehouse.wh_plan_days(move.date, self.delay)
            )
        return super()._get_push_new_date(move)
