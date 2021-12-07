# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "No Automatic Stock Reservation",
    "summary": "Do not auto-reserve stock for Inventory Transfers",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Inventory/Inventory",
    "depends": ["stock"],
    "data": ["views/stock_picking_views.xml"],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["dreispt"],
}
