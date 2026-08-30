#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

{
    "name": "Product - History",
    "version": "18.0.1.0.0",
    "category": "Product",
    "author": "Akretion," "Druidoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "license": "AGPL-3",
    "depends": [
        "product",
        "stock",
        "product_average_consumption",
        "queue_job",
    ],
    "assets": {
        "web.assets_backend": [
            "product_history/static/src/scss/product_history.scss",
        ],
    },
    "data": [
        "security/product_history_security.xml",
        "security/ir.model.access.csv",
        "views/res_config_view.xml",
        "views/product_history_view.xml",
        "views/product_template_view.xml",
        "data/function.xml",
        "data/cron.xml",
    ],
}
