# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Location Release Channel Restriction",
    "summary": """This module allows to restrict location content to products
     that are in the same release channel (moves).""",
    "version": "16.0.1.1.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "maintainers": ["rousseldenis"],
    "depends": [
        "base_partition",
        "stock_location_pending_move",
        "stock_location_children",
        "stock_picking_delivery_link",
        "stock_release_channel",
    ],
    "data": [
        "security/security.xml",
        "views/stock_location.xml",
        "wizards/stock_location_reset_channel.xml",
    ],
}
