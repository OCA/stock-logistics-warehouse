.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Procurement Auto Create Group
=============================

This module allows the system to propose automatically new procurement groups
in procurement orders.

This capability is important when you want to make sure that all the stock
moves resulting from this procurement will never be mixed with moves from
other groups in stock transfers.

The stock transfers resulting from the execution of these procurements will
only contain stock moves created from that procurement.


Configuration
=============

#. Go to *Inventory / Configuration / Settings* and check the option 'Advanced
   routing of products using rules' and press the 'Apply' button.
#. Activate the developer mode.
#. Go to *Inventory / Configuration / Routes / Routes* and check the option
   'Auto-create Procurement Group' to the pull rules where you want the
   procurement groups to be automatically proposed.

Usage
=====

#. Go to *Inventory / Reports / Procurement Exceptions*.
#. Create a new procurement order and make sure that it determines a pull rule
   with the option 'Auto-create Procurement Group' set.
#. When you save the procurement order, a procurement group with format
   'PG/000001' will be created.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/10.0

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
* Jordi Ballester <jordi.ballester@eficent.com>
* Lois Rilo <lois.rilo@eficent.com>

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
