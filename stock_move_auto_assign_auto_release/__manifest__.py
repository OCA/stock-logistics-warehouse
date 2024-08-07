# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Auto Assign Auto Release",
    "summary": """
        Auto release moves after auto assign""",
    "version": "14.0.1.1.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": [
        "stock_available_to_promise_release",
        "stock_move_auto_assign",
    ],
    "data": ["data/queue_job_channel_data.xml", "data/queue_job_function_data.xml"],
    "demo": [],
    "installable": True,
}
