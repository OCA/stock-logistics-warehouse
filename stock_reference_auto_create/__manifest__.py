# Copyright 2017-2020 ForgeFlow, S.L.
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Reference Auto Create",
    "version": "19.0.1.0.0",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "summary": "Allows to configure the system to propose automatically new "
    "stock references during the procurement run.",
    "author": "ForgeFlow, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse",
    "depends": ["stock"],
    "data": ["data/ir_sequence_data.xml", "views/stock_rule_views.xml"],
    "external_dependencies": {"python": ["openupgradelib"]},
    "installable": True,
}
