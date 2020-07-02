Compatibility layer between Stock Vertical Lift and Putaway Storage Types (OCA/wms).

In the vertical lift's Putaway screen, when a good is scanned for a putaway, the
user has to scan the tray type of the corresponding size, so an empty place in a
matching tray is found. When we use storage types, we should know what tray is
compatible with the storage type.

Changes with this module:

* The storage types of trays cannot be selected in the locations form, they have
  to be set in the Tray types.
* In the lift put-away screen, when a package has a storage type, the user isn't
  asked to scan a tray type, instead, the putaway of the Package Storage Type is
  applied.
