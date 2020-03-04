#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

{
    'name': 'Product History for CPO',
    'version': '12.0.1.0.0',
    'category': 'Product',
    'description':
"""
Give access to Product History information in CPO process
=======================================================

Functionnality :
----------------
In the cpo_line, a button can popup the product history. You can then
see all history lines and mark some of them as "ignored".

""",
    'author': 'Akretion, Druidoo',
    'website': 'http://www.akretion.com/fr',
    'license': 'AGPL-3',
    'depends': [
        'purchase_compute_order',
        'product_history',
    ],
    'data': [
        'views/product_history_view.xml'
    ],
}
