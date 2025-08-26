# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Stock Measuring Device",
    "summary": "Implement a common interface for measuring and weighing devices",
    "version": "18.0.1.0.0",
    "category": "Warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "component",
        "barcodes",
        "stock",
        "web_tree_dynamic_colored_field",
        "product_packaging_dimension",
        "product_packaging_level",
        "product_dimension",
        # To refresh wizard screen or pop-up message on the wizard
        "web_notify",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/uom.xml",
        "views/measuring_device_view.xml",
        "wizard/measuring_wizard.xml",
        "views/menu.xml",
    ],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["gurneyalex"],
    "assets": {
        "web.assets_backend": [
            "/stock_measuring_device/static/src/scss/measuring_wizard.scss",
            "/stock_measuring_device/static/src/js/measuring_wizard.esm.js",
        ],
    },
}
