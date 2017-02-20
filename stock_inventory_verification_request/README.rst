.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
Stock Inventory Verification Request
====================================

Adds the capability to request a Slot Verification when a inventory is
'Pending to Approve'. When asked from Inventory Adjustment, which have
discrepancies over the threshold for the location, a Slot Verification
Request will be created for each line that exceed the maximum discrepancy
allowed.

A SVR must be created when warehouse operation (e.g. an inventory adjustment,
a cycle count...) uncovers a count discrepancy within a slot (a small stock
location), and the discrepancy is greater than the pre-defined acceptable
variance threshold. A stock manager should accept the SVR and assign it to
someone to perform it.

The aim of SVR is to find and fix errors before they are transferred to
another location, so they will not be found again in similar stock operations.
In other words, a SVR helps to correct an already existing error in our stock
records the earliest possible. Many times, a SVR will likely lead to manual
actions (before being marked as solved) in order to fix the problems uncovered.

Usage
=====

In order to use this module act as follow:

* From a Inventory Adjustment in state 'Pending to Approve' click in the
  button 'Request Verification'. This will create all the Slot Verification
  Request needed.
* Go to 'Inventory / Inventory Control / Slot Verification Request'
* Go to a Slot Verification Request 'Waiting Actions' and confirm it.
* You can now check the involved lines and moves to help you.
* Once you have found the problem and you have fixed it 'Mark as Solved' the
  Verification.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/9.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lois Rilo Antelo <lois.rilo@eficent.com>


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
