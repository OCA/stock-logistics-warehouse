# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Location Trays",
    "summary": "Organize a location as a matrix of cells",
    "version": "14.0.1.1.2",
    "category": "Stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock", "base_sparse_field"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "demo": ["demo/stock_location_tray_type_demo.xml", "demo/stock_location_demo.xml"],
    "data": [
        "views/stock_location_views.xml",
        "views/stock_location_tray_type_views.xml",
        "views/stock_location_tray_templates.xml",
        "views/stock_move_line_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
