# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Stock Inventory Tier Validation",
    "summary": "Approve inventory adjustments before they update stock",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "category": "Inventory/Inventory",
    "depends": ["stock_inventory", "base_tier_validation"],
    "data": [
        "views/stock_inventory_views.xml",
        "views/stock_quant_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
