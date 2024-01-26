# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Orderpoint Template",
    "summary": "Add a template on orderpoint to automatically create "
    "orderpoints for a location on product replenishment.",
    "version": "14.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_orderpoint_views.xml",
        "views/stock_orderpoint_template_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
