# Copyright (C) 2019 Akretion
# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Multi-Warehouse Security",
    "version": "16.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Akretion, Pierre Verkest, Odoo Community Association (OCA)",
    "maintainers": ["petrus-v"],
    "license": "AGPL-3",
    "installable": True,
    "summary": "Restrict user access in multi-warehouse environment",
    "depends": [
        "stock_warehouse_relationship",
    ],
    "data": [
        "security/stock_security.xml",
        "views/res_users.xml",
    ],
    "development_status": "Alpha",
}
