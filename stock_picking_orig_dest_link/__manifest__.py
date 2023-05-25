# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Origin Destination Link",
    "summary": """
        This addon link the pickings with their respective Origin and Destination Pickings.
    """,
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": ["views/stock_picking_views.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
