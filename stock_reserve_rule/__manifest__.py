# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Reservation Rules",
    "summary": "Configure reservation rules by location",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Stock Management",
    "depends": [
        "stock",
        "stock_helper",
    ],
    "demo": [
        "data/demo/product_demo.xml",
        "data/demo/stock_location_demo.xml",
        "data/demo/stock_reserve_rule_demo.xml",
        "data/demo/stock_inventory_demo.xml",
        "data/demo/stock_picking_demo.xml",
    ],
    "data": [
        "views/stock_reserve_rule_views.xml",
        "security/ir.model.access.csv",
        "security/stock_reserve_rule_security.xml",
    ],
    "installable": True,
    "development_status": "Beta",
    "license": "AGPL-3",
}
