# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Safe Scrap",
    "summary": """
        This module allows to do scrap on locations that have no pickings in progress""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "maintainers": ["rousseldenis"],
    "depends": ["stock", "base_partition"],
    "data": ["views/res_config_settings.xml"],
}
