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
    'name': 'Stock available to promise',
    'version': '2.0',
    'author': u'Numérigraphe',
    'category': 'Warehouse',
    'depends': ['stock'],
    'description': """
Stock available to promise
==========================

This module proposes several options to compute the quantity available to
promise for each product.
This quantity is based on the projected stock and, depending on the
configuration, it can account for various data such as sales quotations or
immediate production capacity.
This can be configured in the menu Settings > Configuration > Warehouse.

Configuration
=============

By default, this module computes the stock available to promise as the virtual
stock.
To take davantage of the additional features, you must which information you
want to base the computation, by checking one or more boxes in the settings:
`Configuration` > `Warehouse` > `Stock available to promise`.

Usage
=====

This module adds a field named `Available for sale` on the Product form.
Various additional fields may be added, depending on which information you
chose to base the computation on.

Credits
=======

Contributors
------------

* Lionel Sausin (Numérigraphe) <ls@numerigraphe.com>
* many others contributed to sub-modules, please refer to each sub-module's
  credits

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
    'license': 'AGPL-3',
    'data': [
        'product_view.xml',
        'res_config_view.xml',
    ]
}
