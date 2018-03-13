.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Putaway strategy per product
============================

This module extends the functionality of the odoo putaway strategy.
It defines a new type of putaway strategy where users can set a specific
stock location per product.

On the product form, the case, rack, location fields are replaced with a
specific putaway strategy and location id for the product.

A putaway strategy can be used to ensure that incoming products will be
stored in the location set on the product form.

A recommended set-up is to create a separate putaway strategy for each
warehouse. This will ensure that the same product will be placed in the
appropriate location in each warehouse it is received.

Installation
============

To install this module, just click the install button.

Configuration
=============

To configure this module, you need to:

#. Go to Inventory > Configuration > Settings
#. Check "Multi-Step Routes" in the Warehouse section
   Routes
#. Go to Inventory > Configuration > Warehouse Management > Locations
#. On the main inventory location of your warehouse,
   set a new putaway strategy.
#. For the new putaway strategy, select 'Fixed per product location'
   as method

Usage
=====

To use this module, you need to:

#. Select the proper stock locations for each product on the product form
   on the "Inventory" tab

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of trouble
, please check there if your issue has already been reported. If you spotted
it first, help us smashing it by providing a detailed and welcomed feedback.

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
* Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
* Denis Roussel - ACSONE SA/NV <denis.roussel@acsone.eu>
* Thomas Fossoul - WINK SA/NV <tfossoul@wink.be>
* Alexandre Saunier - Camptocamp SA <alexandre.saunier@camptocamp.com>


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

