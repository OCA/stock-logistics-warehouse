# Copyright 2017 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Realign Moves and Quants",
    "summary": """
        Align stock move lines and stock quants. This modules fixes the
        symptoms and not the root cause.
    """,
    "version": "12.0.1.0.0",
    "depends": ["stock"],
    "author": "Camptocamp,"
              "Coop IT Easy SCRLfs,"
              "Odoo Community Association (OCA)",
    "category": "Stocks",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "data": [
        "security/ir.model.access.csv",
        "wizard/align_move_quant_wizard_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
