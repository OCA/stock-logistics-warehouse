##############################################################################
#
#    Product - Average Consumption Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Product - Average Consumption',
    'version': '12.0.1.0.0',
    'category': 'Product',
    'description': """
Shows figures in the product form about the average consumption of products
There are settings in Inventory/settings to define the calculation range and
the display range.
===========================================================================

Copyright, Author and Licence :
-------------------------------
    * Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
    * Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
    * Copyright : 2013-Today, Groupement Régional Alimentaire de Proximité;
    * Author :
        * Druidoo
        * Julien WESTE;
        * Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'Druidoo',
    'website': 'https://www.druidoo.io',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'stock',
    ],
    'data': [
        'views/product_template_view.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
}
