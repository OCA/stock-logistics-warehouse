Changed features
~~~~~~~~~~~~~~~~
The quoted quantity is now returned as a positive value, whereas it was
returned as a negative value before v8.0.

This change was made to ensure consistency with the standard, which used to
present outgoing quantities as negative numbers until v8.0, and now presents
them as positive numbers instead.

Removed features
~~~~~~~~~~~~~~~~
Previous versions of this module used to let programmers demand to get the
quoted quantity in an arbitrary Unit of Measure using the `context`. This
feature was present in the standard computations too until v8.0, but it has
been dropped from the standard from v8.0 on.

For the sake of consistency the quoted quantity is now always reported in the
product's main Unit of Measure too.
