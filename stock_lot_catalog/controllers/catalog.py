# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import Controller, request, route


class LotCatalogController(Controller):
    @route("/stock_lot/catalog/order_lines_info", auth="user", type="json")
    def stock_lot_catalog_get_order_lines_info(
        self, res_model, order_id, lot_ids, **kwargs
    ):
        order = request.env[res_model].browse(order_id)
        return order.with_company(
            order.company_id
        )._get_stock_lot_catalog_order_line_info(
            lot_ids,
            **kwargs,
        )

    @route("/stock_lot/catalog/update_order_line_info", auth="user", type="json")
    def stock_lot_catalog_update_order_line_info(
        self, res_model, order_id, lot_id, quantity=0, **kwargs
    ):
        order = request.env[res_model].browse(order_id)
        return order.with_company(order.company_id)._update_lot_order_line_info(
            lot_id,
            quantity,
            **kwargs,
        )
