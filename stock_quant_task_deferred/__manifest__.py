# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Quant Task Deferred",
    "summary": """This module allows to defer quant tasks (merge, delete)""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "maintainers": ["rousseldenis"],
    "depends": ["stock", "queue_job"],
    "data": ["views/res_config_settings.xml", "data/ir_cron.xml"],
}
