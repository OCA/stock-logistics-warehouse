# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Inventory Revaluation MRP",
    "summary": "Adds impacted BoM's and MO's to cost adjustments.",
    "version": "16.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Stock",
    "license": "AGPL-3",
    "depends": [
        "stock_inventory_revaluation_adjustment",
        "mrp_account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/cost_adjustment_detail.xml",
        "views/cost_adjustment_line.xml",
        "views/cost_adjustment.xml",
        "views/res_config_settings.xml",
        "views/product_template.xml",
        "report/report_mrp.xml",
        "report/report_mrp_bom.xml",
        "views/mrp_bom.xml",
    ],
    "maintainers": ["patrickrwilson"],
    "application": False,
    "installable": True,
    "development_status": "Beta",
    "assets": {
        "web.assets_backend": [
            'stock_inventory_revaluation_mrp/static/src/xml/mrp_report_bom_structure.xml',
        ],
    }
}
