# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    last_inventory_date = fields.Datetime(
        "Last Inventory Date",
        compute="_compute_last_inventory_date",
        store=True,
        help="Indicates the last inventory date for the location (only for "
        "validated inventories). It is only computed for leaf locations.",
    )

    # This field reuses the Many2many already defined in the model
    # stock.inventory, so this definition adds little overhead, and
    # allows to create the list of depends needed by the field for the
    # Last Inventory Date.
    validated_inventory_ids = fields.Many2many(
        "stock.inventory",
        relation="stock_inventory_stock_location_rel",
        column1="stock_location_id",
        column2="stock_inventory_id",
        string="Stock Inventories",
        help="Stock inventories in state validated for this location.",
        domain="[('location_ids', 'in', id), ('state', '=', 'done')]",
    )

    @api.depends(
        "usage",
        "child_ids",
        "validated_inventory_ids",
        "validated_inventory_ids.date",
        "validated_inventory_ids.state",
        "validated_inventory_ids.location_ids.usage",
        "validated_inventory_ids.location_ids.child_ids",
    )
    def _compute_last_inventory_date(self):
        """Store date of the last inventory for each leaf location"""
        for loc in self:
            if (
                loc.usage != "view"
                and not loc.child_ids
                and loc.validated_inventory_ids
            ):
                loc.last_inventory_date = loc.validated_inventory_ids.sorted(
                    lambda inventory: inventory.date
                )[-1].date
            else:
                loc.last_inventory_date = False
