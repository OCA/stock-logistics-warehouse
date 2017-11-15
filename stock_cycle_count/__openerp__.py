# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Cycle Count",
    "summary": "Adds the capability to schedule cycle counts in a "
               "warehouse through different rules defined by the user",
    "version": "9.0.1.2.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock",
                "mail",
                "stock_inventory_discrepancy",
                "stock_inventory_exclude_sublocation"],
    "external_dependencies": {
        "python": ['numpy'],
    },
    "data": [
        'views/stock_cycle_count_view.xml',
        'views/stock_cycle_count_rule_view.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_inventory_view.xml',
        'views/stock_location_view.xml',
        'data/cycle_count_sequence.xml',
        'data/cycle_count_ir_cron.xml',
        'reports/stock_location_accuracy_report.xml',
        'reports/stock_cycle_count_report.xml',
        'security/ir.model.access.csv',
    ],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
