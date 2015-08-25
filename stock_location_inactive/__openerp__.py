# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 - Present Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Stock Location Inactive',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'category': 'Others',
    'description': """
    This module allows you to check that:

    * a location is empty (no product)
    * a location has no active sub-locations

before setting it as inactive.

It also modify the Inventory Analysis report to hide inactive locations.

Contributors
------------
* Maxime Chambreuil (maxime.chambreuil@savoirfairelinux.com)
* El Hadji Dem (elhadji.dem@savoirfairelinux.com)
""",
    'depends': [
        'stock',
    ],
    'data': [
        "views/stock_view.xml",
    ],
    'application': False,
    'installable': True,
    'active': False,
}
