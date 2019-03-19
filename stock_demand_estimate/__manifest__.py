# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Demand Estimate",
    "summary": "Allows to create demand estimates.",
    "version": "12.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": [
        "stock",
        "web_widget_x2many_2d_matrix",
        "date_range",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/stock_security.xml",
        "views/stock_demand_estimate_view.xml",
        "views/date_range.xml",
        "wizards/stock_demand_estimate_wizard_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
