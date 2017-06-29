.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Stock Cycle Count
=================

This module adds the capability to execute a cycle count strategy in a
warehouse through different rules defined by the user.


Installation
============

To install this module, you need to:

* Download this module to your addons path.
* Install the module in your database.

Configuration
=============

You can configure the rules to compute the cycle count, acting as follow:

#. Go to "Inventory > Configuration > Cycle Count Rules"
#. Create as much cycle count rules as you want.
#. Assign the rules to the Warehouse where you want to apply the rules in.
#. Set a "Cycle Count Planning Horizon" for each warehouse.

.. figure:: path/to/local/image.png
   :alt: alternative description
   :width: 600 px

Usage
=====

Once you have some rules configured for your warehouses, you can proceed as
is described below.

#. Go to "Inventory > Configuration > Warehouse Management > Warehouses".
#. Select all the warehouses you want to compute the rules in.
#. Click on "Action" and then in "Compute Cycle Count Rules".
#. Go to "Inventory Control > Cycle Counts".
#. Select a Cycle Count planned an confirm it, this will create a draft
   Inventory Adjustment.
#. In the right top corner of the form view you can access the generated
   Inventory Adjustment.
#. Proceed with the Inventory Adjustment as usual.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/9.0

.. repo_id is available in https://github.com/OCA/stock-logistics-warehouse
.. branch is "9.0" for example


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lois Rilo <lois.rilo@eficent.com>
* Jordi Ballester Alomar <jordi.ballester@eficent.com>


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
