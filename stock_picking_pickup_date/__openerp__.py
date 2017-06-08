# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Stock Picking Pickup Date',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'summary': 'Adds a pickup date on Delivery Orders',
    'description': """
This module adds a date field on the delivery order to set the date it will be
picked up by the carrier.

It also adds filters on the 'Deliver Products' based on the pickup date.

Usage
-----

As a Warehouse User, go to Warehouse > Delivery Orders

* Edit a delivery order
* Set the pickup date
* Save it

Saving the pickup date on the DO updates the pickup date field (readonly) on
all the delivery order lines with the same value.

As a Warehouse User, go to Warehouse > Receive/Deliver Product > Deliver
Products

* There is new columns with the delivery order number and the pickup date
* There is new filters in the search pane
** "Today" filters using the pickup date = today
** "2 days" filters using the pickup date = today or tomorrow
** "3 days" filters using the pickup date = today or tomorrow or the day after
   tomorrow
** "4 days" ...
** "7 days" ...
** "14 days" ...

Contributors
------------
* Mathieu Benoit <mathieu.benoit@savoirfairelinux.com>
* Vincent Vinet <vincent.vinet@savoirfairelinux.com>
""",
    'depends': [
        'stock',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'stock_move_view.xml',
        'stock_picking_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
