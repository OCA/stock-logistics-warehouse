Validate a transfer whose lines put packages in a location set to unpack at
reception:

- the packages are unpacked, along with the containers holding them, and
  their content stays in the location without a package;
- a transfer chained to it, e.g. the receipt from a transit location, reserves
  that content without a package, so any quantity can be received;
- the validated transfer keeps its destination packages, so the packages and
  their containers stay visible in the moves history, and a note on it lists
  the packages unpacked.

Packages arriving in other locations, or already in the location when the
option is set, are not unpacked. Inventory adjustments in the location do not
unpack packages either.
