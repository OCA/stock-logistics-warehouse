.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

====================
Stock Request Kanban
====================

On most companies there is products that must be purchased often but cannot be
stored as a usual product because no consumption moves are made.
Usually, they are stored as consumables or putaway rules are defined.
In both cases, reordering rules cannot be used.
This module allows to use stock request as reordering rules for this kind of
products.

It is created following the concept of lean kanban cards.

Usage
=====

Creation
--------
* Go to 'Stock Requests / Stock Requests Kanban' and create a new Kanban.
* Indicate a product, quantity and location.
* Press 'Save'.
* Print the kanban and put it in the storage of the product

Request kanban
--------------

This should be used if you want to create the kanban when the card is consumed.

* Once the product is consumed, take the card
* Go to 'Stock Requests / Order Kanban Card'
* Scan the card
* The stock request is created

Request kanban batch
--------------------

This should be used when you will store the cards and create request orders
for kanbans later.

* Once the product is consumed, take the card and store it
* Create a store request order
* Press the scan button
* Scan all the pending kanban cards

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/11.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Enric Tobella <etobella@creublanca.es>

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
