# Copyright 2017 Trey, Kilobytes de Soluciones
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Supplier Reference",
    "version": "18.0.1.0.0",
    "category": "Stock",
    "author": "Trey, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "summary": """
        Adds a supplier reference field inside supplier's pickings and
        allows search for this reference.""",
    "depends": ["stock"],
    "data": ["views/stock_picking.xml"],
    "installable": True,
}
