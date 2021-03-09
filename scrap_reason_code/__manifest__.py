# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Scrap Reason Code",
    "version": "13.0.1.1.1",
    "license": "AGPL-3",
    "summary": "Reason code for scrapping",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/reason_code_view.xml",
        "views/stock_scrap_views.xml",
        "views/stock_move_views.xml",
    ],
    "maintainers": ["bodedra"],
    "installable": True,
}
