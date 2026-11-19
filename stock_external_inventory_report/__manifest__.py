# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock External Inventory Report",
    "summary": "Review and apply the stock reported by an external system",
    "version": "19.0.1.0.0",
    "category": "Warehouse",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "maintainers": ["simahawk"],
    "depends": [
        "mail",
        "stock",
        "stock_warehouse_stock_type",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/ir_sequence.xml",
        "data/mail_activity_type.xml",
        "views/stock_external_inventory_report_views.xml",
        "views/stock_external_inventory_report_line_views.xml",
    ],
    "installable": True,
}
