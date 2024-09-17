# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Procurement Auto Create Group By Product",
    "version": "16.0.1.1.0",
    "license": "AGPL-3",
    "summary": "Generate one picking per product on the procurement run.",
    "author": "BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["procurement_auto_create_group"],
    "data": [
        "views/stock_rule.xml",
        "views/procurement_group.xml",
    ],
    "installable": True,
}
