# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
#    Alex Duan <alex.duan@elico-corp.com>,Liu Lixia <liu.lixia@elico-corp.com>
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

{'name': 'Kit Product Inventory',
 'version': '1.0',
 'category': 'Generic Modules',
 'depends': ['stock', 'product', 'mrp', 'sale'],
 'author': 'Elico Corp,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'website': 'www.openerp.net.cn',
 'description': """
 .. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Kit Product Inventory
=====================

This module aims to add more flexibility on product inventory.
  * Allowing user to add kit products and manage those kit products inventory.

  * Allowing user to know the quantity on hand of kit products.

Please note that this module re-defines the create and write method of mrp.bom.

Installation
============

To install this module, you need to:

 * have basic modules installed (stock, product, mrp, sale)

Configuration
=============

To configure this module, you need to:

 * No specific configuration needed.

Usage
=====


For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================


Credits
=======


Contributors
------------

* Alex Duan <alex.duan@elico-corp.com>
* Liu Lixia <liu.lixia@elico-corp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
    whose mission is to support the collaborative development of Odoo features
        and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
""",
 'images': [],
 'demo': [],
 'data': ['product_view.xml'],
 'installable': True,
 'application': False,
 }
