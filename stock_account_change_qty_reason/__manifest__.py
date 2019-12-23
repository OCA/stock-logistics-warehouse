# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Account Change Quantity Reason",
    "summary": """
        Stock Account Change Quantity Reason """,
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["stock_account", "stock_change_qty_reason"],
    "data": ["views/stock_inventory_line_reason_view.xml", "views/stock_move_view.xml"],
    "installable": True,
}
