.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

=============
Stock Request
=============

This module was written to allow users to request products that are
frequently stocked by the company, to be transferred to their chosen location.


Configuration
=============

Users should be assigned to the groups 'Stock Request / User' or 'Stock
Request / Manager'.

Group Stock Request / User
--------------------------

* Can see her/his own Stock Requests, and others that she/he's been granted
  permission to follow.

* Can create/update only her/his Stock Requests.

Group Stock Request / Manager
-----------------------------

* Can fully manage all Stock Requests


Usage
=====

Creation
--------
* Go to 'Stock Requests / Stock Requests' and create a new Request.
* Indicate a product, quantity and location.
* Press 'Confirm'.

Upon confirmation the request will be evaluated using the procurement rules
for the selected location.

In case that transfers are created, the user will be able to access to them
from the button 'Transfers' available in the Stock Request.

Cancel
------
When the user cancels a Stock Request, the related pending stock moves will be
also cancelled.


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

* Jordi Ballester (EFICENT) <jordi.ballester@eficent.com>.
* Enric Tobella <etobella@creublanca.es>
* Atte Isopuro <atte.isopuro@avoin.systems>

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
