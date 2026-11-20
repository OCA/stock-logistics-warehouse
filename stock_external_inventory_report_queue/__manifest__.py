# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock External Inventory Report Queue",
    "summary": "Run the comparisons of the external inventory reports in jobs",
    "version": "19.0.1.0.0",
    "category": "Warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "maintainers": ["simahawk"],
    "depends": [
        "queue_job",
        "stock_external_inventory_report",
    ],
    "data": [
        "data/queue_job_function_data.xml",
        "views/stock_external_inventory_report_views.xml",
    ],
    "installable": True,
}
