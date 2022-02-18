# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Demand Estimate Matrix",
    "summary": "Allows to create demand estimates.",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "development_status": "Production/Stable",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock_demand_estimate", "web_widget_x2many_2d_matrix", "date_range"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_demand_estimate_view.xml",
        "views/date_range.xml",
        "wizards/stock_demand_estimate_wizard_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
