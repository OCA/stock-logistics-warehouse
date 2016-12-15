.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Stock Reorder Forecast
======================


Allows to predict date when stock levels will reach minimum by
analizying sales volume in a period and therefore to trigger RFQ's ahead
of time

Extends stock to calculate period turnover and  ultimate date of order 
(the date where we reach minimum stock)
This module allows to create RFQ's by checking the product form and 
examining the ultimate purchase value.

The ultimate purchase value is the date we forecast this product will not be
available. It is obtained by calculating the average sales rate of this 
product and predicting at this rate how long will it take for the 
stock to reach 0 at this speed.

The period upon wich we calculate this average rate  be personalized, default is:

TURNOVER_PERIOD = Amount of time to calculate average (default 365)
TURNOVER_AVERAGE = Average sale rate in that period.
Ultimate Purchase = Day in the future where stock should finish at current
rate.

All values are  (period, average) are kept on (in order of importance):
            * Supplier Info
            * Partner
            * Category

if the values are not set on supplier info it will default to values on
partner, if not set on supplier will default to category, if not set anywhere 
will default to Hardcoded values (ir.config.parameters period=365 days).  

The turnover average and the ultimate purchase derived by it are calculated in
bulk by a daily cron job.


Configuration
=============

To configure this module, you need to:
set turnover_period stock_period_max , stock_period_min on:
            
            * Product
            * Supplier Infos
            * Partners
            * Categories
            * Default value

These values will be taken in this order of priority (highest to lowest) 
if the values in product, Supplier Info, Partners, Categories are all not 
set it will revert to Default Value, defined in installation data is a 
company parameter.

Also set the frequency of turnover and purchase date calculation by setting 
in Automatic Actions the execution of cron job "Purchase Proposal Refresh"  
(by default set at once a day).


Usage
=====

Set on product and/or partner(supplier) and/or product category the values 
of turnover period.

Make sure the cron job  "Purchase Proposal Refresh" is activated, launch it
manually the first time in order to have all "ultimate dates" for products
calculated. Set the cron job time/date at a convenient time and frequency, this
job will refresh all stats used for forcasting ultimate purchase date. If you
have a high volume of sales and do frequent resupplies it is advisable to
launch it multiple times a day.


View products to see all products with an ultimate order date, for that
interface you can generate a RFQ to desired date.

You can also view from the partner/supplier form all products ordered by this
partner.

#. Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "9.0" for example


Known issues / Roadmap
======================
Does not support Multicompany, calculatuion of stats will allways work on
cross-company products purchases and pickings. It will only calculate outgoing
moves , not internal moves. So the stats will be representative of all
companies global stats (all sales from all companies/turnover period of
product).

Implementing a full multicompany support will require additional support
datastrutures.

from a functional stand point, the global stats may be still usefull in some
multicompany configurations, not all.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Giovanni Francesco Capalbo <giovanni@therp.nl> 
* Holger Brunn <hbrunn@therp.nl>
* Hans Van Dijk <hvd400@gmail.com>
* Ronald Portier <rportier@therp.nl>

Funders
-------

The development of this module has been financially supported by:

* Therp B.V.

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

.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
