# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Location Last Inventory Date",
    "summary": "Show the last inventory date for a leaf location",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["product", "stock"],
    "data": ["views/stock_location_views.xml"],
}
