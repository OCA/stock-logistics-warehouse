# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockLotCatalogMixin(models.AbstractModel):
    _name = "stock.lot.catalog.mixin"
    _description = "Stock Lot Catalog Mixin"

    def action_add_from_stock_lot_catalog(self):
        kanban_view_id = self.env.ref("stock_lot_catalog.lot_view_kanban_catalog").id
        search_view_id = self.env.ref("stock_lot_catalog.lot_view_search_catalog").id
        additional_context = self._get_action_add_from_stock_lot_catalog_extra_context()
        return {
            "type": "ir.actions.act_window",
            "name": _("Lots"),
            "res_model": "stock.lot",
            "views": [(kanban_view_id, "kanban"), (False, "form")],
            "search_view_id": [search_view_id, "search"],
            "domain": self._get_stock_lot_catalog_domain(),
            "context": {**self.env.context, **additional_context},
        }

    def _get_stock_lot_catalog_domain(self):
        return [
            "|",
            ("company_id", "=", False),
            ("company_id", "parent_of", self.company_id.id),
        ]

    def _get_stock_lot_catalog_record_lines(self, lot_ids, child_field=False, **kwargs):
        """Returns the record's lines grouped by lot.
        Must be overrided by each model using this mixin.

        :param list lot_ids: The ids of the lots currently displayed in the product
        catalog.
        :rtype: dict
        """
        return {}

    def _get_stock_lot_catalog_order_data(self, lots, **kwargs):
        return {
            lot.id: {
                "productType": lot.product_id.type,
                "product_tracking": lot.product_id.tracking,
                "lotId": lot.id,
                "price": lot._get_lst_price(),
            }
            for lot in lots
        }

    def _stock_lot_is_readonly(self):
        """Must be overrided by each model using this mixin.
        :return: Whether the record is read-only or not.
        :rtype: bool
        """
        return False

    def _default_stock_lot_order_line_values(self, child_field=False):
        return {
            "quantity": 0,
            "readOnly": self._stock_lot_is_readonly() if self else False,
        }

    def _get_stock_lot_catalog_order_line_info(
        self, lot_ids, child_field=False, **kwargs
    ):
        order_line_info = {}
        default_data = self._default_stock_lot_order_line_values(child_field)

        for lot, record_lines in self._get_stock_lot_catalog_record_lines(
            lot_ids, child_field=child_field, **kwargs
        ).items():
            order_line_info[lot.id] = {
                **record_lines._get_stock_lot_catalog_lines_data(
                    parent_record=self, **kwargs
                ),
                "productType": lot.product_id.type,
                "product_tracking": lot.product_id.tracking,
            }
            lot_ids.remove(lot.id)

        lots = self.env["stock.lot"].browse(lot_ids)
        lot_data = self._get_stock_lot_catalog_order_data(lots, **kwargs)
        for lot_id, data in lot_data.items():
            order_line_info[lot_id] = {**default_data, **data}
        return order_line_info

    def _get_action_add_from_stock_lot_catalog_extra_context(self):
        return {
            "lot_catalog_order_id": self.id,
            "lot_catalog_order_model": self._name,
        }
