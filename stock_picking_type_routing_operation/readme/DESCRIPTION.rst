Route explains the steps you want to produce whereas the “picking routing
operation” defines how operations are grouped according to their final source
and destination location.

This allows for example:

* To parallelize picking operations in two locations of a warehouse, splitting
  them in two different picking type
* To define pre-picking (wave) in some sub-locations, then roundtrip picking of
  the sub-location waves
