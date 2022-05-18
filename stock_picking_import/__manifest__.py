# © 2021 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "stock_picking_import from CSV",
    "version": "15.0.1.0.0",
    "category": "Hidden",
    "author": "initOS GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "summary": """Import a CSV with delivery addresses to prepare pickings
    based on a sale order""",
    "depends": [
        "sale_management",
        "stock",
    ],
    "data": [
        "views/stock_picking_view.xml",
        "wizards/stock_import_picking_wizard.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
