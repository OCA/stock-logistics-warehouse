The configuration of the rules is done in "Inventory > Configuration > Stock Reservation Rules".

Creation of a rule:

Properties that define where the rule will be applied:

* Location: Define where the rule will look for goods (a parent of the move's source location).
* Fallback Location: Define where the goods are reserved if none of the removal
  rule could reserve the goods. Use it for replenishment. The source location
  move will be changed to this location if the move is not available. If the
  move is partially available, it is split and the unavailable quantity is
  sourced in this location for replenishment. If left empty, the goods are
  reserved in the move's source location / sub-locations.
* Rule Domain: The rule is used only if the Stock Move matches the domain.

Removal rules for the locations:

* Quants Domain: this domain includes/excludes quants based on a domain.
* Advanced Removal Strategy: the strategy that will be used for this location
  and sub-location when the rule is used.

The sequences have to be sorted in the view list to define the reservation priorities.
