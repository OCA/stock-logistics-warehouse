.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

===============================
Stock Request Purchase Analytic
===============================

This integrates stock_request_analytic and stock_request_purchase modules. It
passes the analytic account from the stock request to the purchase order.


Usage
=====


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/11.0

Known issues / Roadmap
======================

* Potentially, more than one stock request can be satisfied with one purchase
  order line, in case those stock requests have different analytic accounts
  then last analytic account will be kept.

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

* Jordi Ballester <jordi.ballester@eficent.com>.
* Enric Tobella <etobella@creublanca.es>
* Aaron Henriquez <ahenriquez@eficent.com>.

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
