# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Vertical Lift Packaging type",
    "summary": "Provides integration with Vertical Lifts and packaging types",
    "version": "14.0.1.0.0",
    "category": "Stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock_vertical_lift",
        # OCA / product-attribute
        "product_packaging_type",
    ],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "data": ["views/shuttle_screen_templates.xml"],
    "installable": True,
    "auto_install": True,
    "development_status": "Alpha",
}
