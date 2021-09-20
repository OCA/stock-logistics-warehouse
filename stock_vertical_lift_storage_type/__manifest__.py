# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vertical Lift - Storage Type",
    "summary": "Compatibility layer for storage types on vertical lifts",
    "version": "14.0.1.0.0",
    "category": "Stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock_vertical_lift",  # OCA/stock-logistics-warehouse
        "stock_storage_type",  # OCA/wms
    ],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "data": [
        "views/stock_location_tray_type_views.xml",
        "views/stock_location_views.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
