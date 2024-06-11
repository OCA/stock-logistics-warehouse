# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Location Package Restriction",
    "summary": """
        Control if the location can contain products in a package""",
    "version": "16.0.1.0.0",
    "category": "Warehouse Management",
    "author": "Raumschmiede.de, BCIM, Odoo Community Association (OCA)",
    "maintainters": ["jbaudoux"],
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": ["stock"],
    "application": False,
    "installable": True,
    "data": ["views/stock_location.xml"],
}
