# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Stock Measuring Device",
    "summary": "Implement a common interface for measuring and weighing devices",
    "version": "13.0.1.0.0",
    "category": "Warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "component",
        "barcodes",
        "stock",
        "web_tree_dynamic_colored_field",
        "product_packaging_dimension",
        "product_packaging_type_required",
        "product_dimension",
        # For the pop-up message to tell the user to refresh.
        "web_notify",
        "web_ir_actions_act_view_reload",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/uom.xml",
        "views/assets.xml",
        "views/measuring_device_view.xml",
        "wizard/measuring_wizard.xml",
        "views/menu.xml",
    ],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["gurneyalex"],
}
