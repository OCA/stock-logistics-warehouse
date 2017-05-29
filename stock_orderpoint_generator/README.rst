.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Order point generator
=====================

Add a wizard to configure reordering rules for multiple products in one go,
and allow to automatically update reordering rules from rule templates.

Configuration
=============

Reordering rule templates can be configured in "Inventory > Configuration >
Products > Reordering Rule Templates".

The frequency of the cron that updates the Reordering Rules can be configured
in "Settings > Technical > Actions > Scheduled Actions". The name of the
scheduled action is "Reordering Rule Templates Generator".

Usage
=====

By activating the "Create Rules Automatically" on a reordering rule template,
you are able to select a list of products. Any change on the template will then
be replicated on the products Reordering Rules. The change is not immediate as
it is processed by a scheduled action.

On a product, you can also choose one or more Reordering Rule Templates. Any
template added or removed on the product is immediately reflected on its
Reordering Rules.

Lastly, you can promptly create Reordering Rules for a product or a product
template using the "Reordering Rules Generator". Note that it will replace all
the existing rules for the product. You will usually not want to use this
feature on products that have Automatic Reordering Rules Templates.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/9.0


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

 * Yannick Vaucher <yannick.vaucher@camptocamp.com>
 * Matthieu Dietrich <matthieu.dietrich@camptocamp.com>
 * Cyril Gaudin <cyril.gaudin@camptocamp.com>
 * Guewen Baconnier <guewen.baconnier@camptocamp.com>

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
