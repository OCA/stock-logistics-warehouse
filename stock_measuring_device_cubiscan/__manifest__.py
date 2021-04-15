# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Stock Measuring Device Cubiscan",
    "summary": "Implement interface with Cubiscan devices for packaging measurement",
    "version": "13.0.1.0.0",
    "category": "Warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock_measuring_device"],
    "external_dependencies": {"python": ["cubiscan"]},
    "data": ["views/measuring_device_view.xml"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["gurneyalex"],
}
