# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Product Security Restricted",
    "version": "17.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "stock",
    ],
    "data": [
        "security/stock_product_security_restricted.xml",
        "security/ir.model.access.csv",
        "views/product_category_view.xml",
        "views/stock_warehouse_view.xml",
    ],
    "installable": True,
}
