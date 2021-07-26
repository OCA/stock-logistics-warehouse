# Copyright 2015 Mikel Arregi - AvanzOSC
# Copyright 2017 ForgeFlow - Jordi Ballester
# Copyright 2018 Fanha Giang
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2021 ForgeFlow - Lois Rilo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Stock - Manual Quant Assignment",
    "version": "14.0.1.0.0",
    "category": "Warehouse",
    "license": "AGPL-3",
    "author": "AvanzOSC, "
    "Tecnativa, "
    "ForgeFlow, "
    "Fanha Giang, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "depends": ["stock"],
    "data": [
        "wizard/assign_manual_quants_view.xml",
        "wizard/res_config_settings_views.xml",
        "views/stock_move_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
