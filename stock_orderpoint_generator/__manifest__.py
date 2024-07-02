# Copyright 2012-2016 Camptocamp SA
# Copyright 2019 Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Order point generator",
    "summary": "Mass configuration of stock order points",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, " "Tecnativa, " "Odoo Community Association (OCA)",
    "category": "Warehouse",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/orderpoint_template_views.xml",
        "views/res_config_settings.xml",
        "wizard/orderpoint_generator_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
