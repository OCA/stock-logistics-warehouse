# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Move Auto Assign",
    "summary": "Try to reserve moves when goods enter in a location",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Stock Management",
    "depends": [
        "stock",
        # OCA/queue
        "queue_job",
    ],
    "data": ["data/queue_job_channel_data.xml", "data/queue_job_function_data.xml"],
    "installable": True,
    "development_status": "Beta",
    "license": "AGPL-3",
}
