# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Move Line Stock Info",
    "version": "13.0.1.0.0",
    "depends": ["stock_account"],
    "author": "Eficent," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_line_view.xml",
        "views/stock_move_view.xml",
    ],
}
