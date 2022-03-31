# Copyright (C) 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Location Content Template",
    "summary": "Define templates of location content and check the report for discrepancies",
    "version": "14.0.1.0.0",
    "category": "stock",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "maintainers": ["max3903"],
    "license": "AGPL-3",
    "depends": ["stock", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/stock_location_content_template.xml",
        "views/stock_location_content_template_line.xml",
        "views/stock_location_content_check_line.xml",
        "views/stock_location_content_check.xml",
        "views/stock_location.xml",
        "report/stock_location_content_report.xml",
    ],
}
