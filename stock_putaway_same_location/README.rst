.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Stock Putaway Same Location
===========================

The goal of this module is to define the new putaway strategy, according to
which each product is placed in last known move destination. In case when Odoo
has no information on this product's movements (namely those having an internal
location as their destination), an empty location is used.

Regarding products tracked by lots, Odoo tries to keep only one lot in a given
location at a time (this should work fine in case your warehouse is configured
to use two steps reception strategy).

Configuration
=============
You may want to set **Warehouse > Warehouse configuration > Incoming Shipments**
to **Unload in input location then go to stock (2 steps)** for the sake of
enabling the feature of separating products of different lots.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcomed feedback.

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Artem Kostyuk <a.kostyuk@mobilunity.com>

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
