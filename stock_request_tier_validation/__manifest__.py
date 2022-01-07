# Copyright 2019-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Request Tier Validation",
    "summary": "Extends the functionality of Stock Requests to "
    "support a tier validation process.",
    "version": "14.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock_request", "base_tier_validation"],
    "data": [
        "data/stock_request_tier_definition.xml",
        "views/stock_request_order_view.xml",
        "views/stock_request_view.xml",
    ],
}
