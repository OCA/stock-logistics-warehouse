# Copyright 2017-20 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Inventory Verification Request",
    "summary": "Adds the capability to request a Slot Verification when "
    "a inventory is Pending to Approve",
    "version": "15.0.1.0.0",
    "maintainers": ["LoisRForgeFlow"],
    "author": "ForgeFlow, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": [
        "stock_inventory",
        "stock_inventory_discrepancy",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_security.xml",
        "views/stock_slot_verification_request_view.xml",
        "views/stock_inventory_view.xml",
        "views/stock_location_view.xml",
        "data/slot_verification_request_sequence.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
