Known issues
~~~~~~~~~~~~
The manufacturing delays are not taken into account : this module assumes that
if you have components in stock goods, you can manufacture finished goods
quickly enough.

As a consequence, and to avoid overestimating, **only the first level** of Bill
of Materials is considered.

However Sets (a.k.a "phantom" BoMs) are taken into account: if a component must
be replaced with a set, it's the stock of the set's product which will decide
the potential.

If a product has several variants, only the variant with the biggest potential
will be taken into account when reporting the production potential. For
example, even if you actually have enough components to make 10 iPads 16Go AND
42 iPads 32Go, we'll consider that you can promise only 42 iPads.

Removed features
~~~~~~~~~~~~~~~~
Previous versions of this module used to let programmers demand to get the
potential quantity in an arbitrary Unit of Measure using the `context`. This
feature was present in the standard computations too until v8.0, but it has
been dropped from the standard from v8.0 on.

For the sake of consistency the potential quantity is now always reported in
the product's main Unit of Measure too.

Roadmap
~~~~~~~
Possible improvements for future versions:

* Take manufacturing delays into account: we should not promise goods to
  customers if they want them delivered earlier that we can make them
* Compute the quantity of finished product that can be made directly on each
  Bill of Material: this would be useful for production managers, and may make
  the computations faster by avoiding to compute the same BoM several times
  when several variants share the same BoM.
* Add an option (probably as a sub-module) to consider all raw materials as
  available if they can be bought from the suppliers in time for the
  manufacturing.
