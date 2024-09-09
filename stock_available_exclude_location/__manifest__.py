# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Available Exclude Location",
    "summary": """
        Exclude locations for product available quantities""",
    "version": "14.0.1.0.0",
    "category": "Stock",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock_available_base_exclude_location",
        "stock_location_children",
    ],
    "data": ["views/res_config_settings.xml"],
    "installable": True,
    "development_status": "Alpha",
}
