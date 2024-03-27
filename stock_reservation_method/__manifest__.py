# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Reservation Method",
    "summary": "Backport of reservation method of v15",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Stock Management",
    "maintainers": ["ChrisOForgeFlow"],
    "depends": [
        "stock",
    ],
    "demo": [],
    "data": [
        "views/stock_picking_type_view.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "license": "LGPL-3",
    "pre_init_hook": "pre_init_hook",
}
