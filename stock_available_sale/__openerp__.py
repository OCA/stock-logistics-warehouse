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
    'name': 'Quotations in quantity available to promise',
    'version': '2.0',
    'author': u'Numérigraphe SÀRL',
    'category': 'Hidden',
    'depends': [
        'stock_available',
        'sale_order_dates',
        'sale_stock',
    ],
    'description': """
Quotations in quantity available to promise
===========================================

This module computes the quoted quantity of each Product, and subtracts it from
the quantity available to promise.

"Quoted" is defined as the sum of the quantities of this Product in
Sale Quotations, taking the context's shop or warehouse into account.

Known issues / Roadmap
======================

This module does not warn salespersons when the quantity available to promise
is insufficient to deliver a sale order line.

Work to add this feature is underway:
https://github.com/OCA/stock-logistics-warehouse/pull/25

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
        'test/quoted_qty.yml',
    ],
    'license': 'AGPL-3',
}
