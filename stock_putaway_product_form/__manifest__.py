# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Putaway strategies on product form view",
    "summary": "Edit putaway strategies directly from the product form view",
    "version": "12.0.1.0.1",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock"],
    "external_dependencies": {
        "python": [
            "openupgradelib",
        ],
    },
    "data": ["views/product.xml"],
    "demo": ["demo/putaway_strategies.xml"],
    "maintainers": ["kevinkhao", "sebastienbeau"],
    "post_init_hook": "post_init_hook",
}
