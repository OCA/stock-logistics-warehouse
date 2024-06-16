# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "stock_location_orderpoint",
    "author": "MT Software, BCIM, Odoo Community Association (OCA)",
    "summary": "Declare orderpoint on a location "
    "allowing to replenish any product with the same criteria.",
    "version": "14.0.1.1.2",
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/ir_sequence.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "views/stock_location_orderpoint_views.xml",
        "views/stock_location.xml",
        "views/menu.xml",
        "demo/stock_location.xml",
        "demo/stock_picking_type.xml",
        "demo/stock_route.xml",
        "demo/stock_location_orderpoint.xml",
    ],
    "depends": [
        "stock_helper",
        "queue_job",
    ],
    "license": "AGPL-3",
    "maintainers": ["mt-software-de"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
}
