#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

{
    "name": "Product History for CPO",
    "version": "18.0.1.0.0",
    "category": "Product",
    "author": "Akretion, Druidoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": [
        "purchase_compute_order",
        "product_history",
    ],
    "data": ["views/product_history_view.xml"],
}
