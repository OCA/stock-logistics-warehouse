# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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
    'name': 'Consider the production potential is available to promise',
    'version': '2.0',
    'author': u'Numérigraphe',
    'category': 'Hidden',
    'depends': ['stock_available', 'mrp'],
    'description': """
Consider the production potential is available to promise
=========================================================

This module takes the potential quantities available for Products in account in
the quantity available to promise, where the "Potential quantity" is the
quantity that can be manufactured with the components immediately at hand.

Known issues
============

The manufacturing delays are not taken into account : this module assumes that
if you have components in stock goods, you can manufacture finished goods
quickly enough.
To avoid overestimating, **only the first level** of Bill of Materials is
considered.

Roadmap
-------

* include all levels of BoM, using `bom_explode`. @gdgellatly gave an example
  of how to do it here:
  https://github.com/OCA/stock-logistics-warehouse/pull/5#issuecomment-66902191
   Ideally, we will want to take manufacturing delays into account: we can't
   promiss goods to customers if they want them delivered earlier that we can
   make them
* add an option (probably as a sub-module) to consider all raw materials as
  available if they can be bought from the suppliers in time for the
  manufacturing.

Credits
=======

Contributors
------------
* Loïc Bellier (Numérigraphe) <lb@numerigraphe.com>
* Lionel Sausin (Numérigraphe) <ls@numerigraphe.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.""",
    'data': [
        'product_view.xml',
    ],
    'test': [
        'test/potential_qty.yml',
    ],
    'license': 'AGPL-3',
}
