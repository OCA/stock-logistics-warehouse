# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Available to Promise Release",
    "version": "13.0.1.0.0",
    "summary": "Release Operations based on available to promise",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "category": "Stock Management",
    "depends": ["stock"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_location_route_views.xml",
        "wizards/stock_move_release_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "application": False,
    "development_status": "Alpha",
}
