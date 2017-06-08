# -*- encoding: utf-8 -*-
###############################################################################
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
###############################################################################

{
    'name': 'Stock Skid Management',
    "version": "7.0.1.0.0",
    'author': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'depends': [
        'product',
        'stock',
        'mrp',
    ],
    'category': 'Warehouse',
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========
Stock Skid
==========

This module allow you to reprint skid labels in your warehouse including
partial ones.

A skid is a pallet with no bottom deck boards.

Usage
=====

To use this module, you need to:

* go to Manufacturing > Partial Label Reprint

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* ...

Credits
=======

Contributors
------------

* Vincent Vinet (vincent.vinet@savoirfairelinux.com)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
    """,
    'data': [
        'reprint_label.xml',
    ],
    'active': False,
    'installable': True
}
