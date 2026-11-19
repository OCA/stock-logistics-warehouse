# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.exceptions import UserError

STOCK_TYPE_FREE = "free"
STOCK_TYPE_QUALITY = "quality"


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def _get_stock_types(self):
        """Return the stock types of the warehouse and how to find their location.

        Override it to add stock types.

        :return: dict ``{stock_type: {"wh_location_field": field name,
            "missing_message": error raised when the field is empty}}``
        """
        self.ensure_one()
        return {
            STOCK_TYPE_FREE: {
                "wh_location_field": "lot_stock_id",
                "missing_message": self.env._(
                    "No Stock Location is set on warehouse %(warehouse)s",
                    warehouse=self.display_name,
                ),
            },
            STOCK_TYPE_QUALITY: {
                "wh_location_field": "wh_qc_stock_loc_id",
                "missing_message": self.env._(
                    "No Quality Control Location is set on warehouse %(warehouse)s",
                    warehouse=self.display_name,
                ),
            },
        }

    def _get_stock_type_location(self, stock_type, required=False):
        """Return the location of ``stock_type`` in the warehouse.

        :param stock_type: a key of ``_get_stock_types()``
        :param required: raise if the warehouse has no location for it
        :return: ``stock.location`` record, empty when not set
        """
        stock_types = self._get_stock_types()
        if stock_type not in stock_types:
            raise UserError(
                self.env._(
                    "Unrecognized stock type: %(stock_type)s", stock_type=stock_type
                )
            )
        spec = stock_types[stock_type]
        location = self[spec["wh_location_field"]]
        if required and not location:
            raise UserError(spec["missing_message"])
        return location

    def _get_location_stock_type(self, location):
        """Return the stock type of ``location`` in the warehouse, or ``None``."""
        for stock_type, spec in self._get_stock_types().items():
            type_location = self[spec["wh_location_field"]]
            if type_location and type_location == location:
                return stock_type
        return None
