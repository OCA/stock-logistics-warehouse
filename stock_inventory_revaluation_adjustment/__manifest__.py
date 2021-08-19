# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Revaluation",
    "summary": "Adds a workflow to adjusting costs on products",
    "version": "14.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Stock",
    "license": "AGPL-3",
    "depends": ["stock_account", "mrp"],
    "data": [
        "report/report_financials.xml",
        "security/ir.model.access.csv",
        "security/stock_inventory_security.xml",
        "views/cost_adjustment_line.xml",
        "views/cost_adjustment_type.xml",
        "views/cost_adjustment.xml",
        "views/product_template_view.xml",
        "views/assets_backend.xml",
        "wizard/add_multi_products.xml",
    ],
    "qweb": [
        "static/src/xml/cost_inventory_products.xml",
    ],
    "application": False,
    "installable": True,
    "maintainers": ["patrickrwilson"],
}
