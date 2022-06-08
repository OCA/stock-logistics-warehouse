# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Secondary Unit",
    "summary": "Get product quantities in a secondary unit",
    "version": "15.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "stock",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock", "product_secondary_unit"],
    "data": [
        "views/product_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "report/report_deliveryslip.xml",
    ],
}
