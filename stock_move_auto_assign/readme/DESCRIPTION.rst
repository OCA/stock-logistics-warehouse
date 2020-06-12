Automatically check availability of stock moves when a move is set to "done".

It uses queue jobs to verify the availability in order to have a minimal impact
on the user operations.

The conditions to trigger the check are:

* A move is marked as done
* The destination locations of the move lines are internal
* The move doesn't have successors in a chain of moves

At this point, jobs are generated:

* One job per product
* Any move waiting for stock in a parent (or same) location of the internal
  destination locations from the done move has its availability checked

Only one job is generated for an identical set of (product, locations).
