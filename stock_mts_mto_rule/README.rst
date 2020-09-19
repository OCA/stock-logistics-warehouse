.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==================
Stock MTS+MTO Rule
==================

This module add a Make To Stock + Make to Order Route.

If you choose the make to stock + make to order rule instead of the make to
order route, the creation of a purchase order will depend on the virtual stock.
There are 3 cases : 

1. The virtual stock of the product is 0 
    => It will act exactly like the make to order route.

2. The virtual stock is equal to the quantity ordered
    => It will act exactly like a make to stock route

3. The virtual stock is more than 0 but less than ordered quantity
    => On part of the products will be taken from stock and a purchase order
       will be created for the rest. So it will act like both make to order and
       make to stock rule.

Example : 
We have a virtual stock of : 1 product A
A sale Order is made for 3 products A.
2 Procurements will be created : 

1. 1 with a make to stock rule and a quantity of 1

2. 1 with a make to order rule and a quantity of 2.

After validation, a purchase order with 2 products will be created.

Configuration
=============

You have to select 'Use MTO+MTS rules' on the company's warehouse form.

Usage
=====

You have to select the mts+mto route on the product form.
You should not select both the mts+mto route and the mto route.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/13.0

Known issues
============

If you cancel a delivery order and then recreate it from Recreate
Delivery Order button in sale order form, then the stock level at the time of
the Re-Creation won't be taken into account. So if a purchase order was created
when the sale order was first validated, a similar purchase order will be created
during the Re-creation of the delivery order, even if not needed regarding the actual stock.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Florian da Costa <florian.dacosta@akretion.com>
* Jared Kipe <jared@hibou.io>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
