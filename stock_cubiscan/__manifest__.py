# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Cubiscan",
    "summary": "Implement inteface with Cubiscan devices for packaging",
    "version": "13.0.1.1.0",
    "category": "Warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "barcodes",
        "stock",
        "web_tree_dynamic_colored_field",
        "product_packaging_dimension",
        "product_packaging_type_required",
        "product_dimension",
    ],
    "external_dependencies": {"python": ["cubiscan"]},
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "data": [
        "data/uom.xml",
        "views/assets.xml",
        "views/cubiscan_view.xml",
        "wizard/cubiscan_wizard.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "development_status": "Alpha",
}
