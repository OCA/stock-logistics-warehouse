# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Reservation Rules",
    "summary": "Configure reservation rules by location",
    "version": "13.0.1.2.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Stock Management",
    "depends": ["stock", "product_packaging_type"],  # OCA/product-attribute
    "demo": [
        "demo/product_demo.xml",
        "demo/stock_location_demo.xml",
        "demo/stock_reserve_rule_demo.xml",
        "demo/stock_inventory_demo.xml",
        "demo/stock_picking_demo.xml",
    ],
    "data": [
        "views/stock_reserve_rule_views.xml",
        "security/ir.model.access.csv",
        "security/stock_reserve_rule_security.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
    "license": "AGPL-3",
}
