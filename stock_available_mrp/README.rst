.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================================================
Consider the production potential is available to promise
=========================================================

This module takes the potential quantities available for Products into account in
the quantity available to promise, where the "Potential quantity" is the
quantity that can be manufactured with the components immediately at hand.
By configuration, the "Potential quantity" can be computed based on other product field.
For example, "Potential quantity" can be the quantity that can be manufactured
with the components available to promise.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/8.0

Known issues / Roadmap
======================

Known issues
------------
The manufacturing delays are not taken into account : this module assumes that
if you have components in stock goods, you can manufacture finished goods
quickly enough.

As a consequence, and to avoid overestimating, **only the first level** of Bill of Materials is
considered.
However Sets (a.k.a "phantom" BoMs) are taken into account: if a component must be replaced with a set, it's the stock of the set's product which will decide the potential. 

If a product has several variants, only the variant with the biggest potential will be taken into account when reporting the production potential.
For example, even if you actually have enough components to make 10 iPads 16Go AND 42 iPads 32Go, we'll consider that you can promise only 42 iPads.

Removed features
----------------
Previous versions of this module used to let programmers demand to get the potential quantity in an arbitrary Unit of Measure using the `context`. This feature was present in the standard computations too until v8.0, but it has been dropped from the standard from v8.0 on.
For the sake of consistency the potential quantity is now always reported in the product's main Unit of Measure too.

Roadmap
-------
Possible improvements for future versions:
* take manufacturing delays into account: we should not promise goods to customers if they want them delivered earlier that we can make them
* Compute the quantity of finished product that can be made directly on each Bill of Material: this would be useful for production managers, and may make the computations faster by avoiding to compute the same BoM several times when several variants share the same BoM
* add an option (probably as a sub-module) to consider all raw materials as available if they can be bought from the suppliers in time for the manufacturing.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
stock-logistics-warehouse/issues/new?body=module:%20
stock_available%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------
* Loïc Bellier (Numérigraphe) <lb@numerigraphe.com>
* Lionel Sausin (Numérigraphe) <ls@numerigraphe.com>
* many thanks to Graeme Gellatly for his advice and code review
* Laurent Mignon <laurent.mignon@acsone.eu>

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
