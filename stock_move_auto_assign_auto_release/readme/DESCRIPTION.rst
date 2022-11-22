Automatically release stock moves when a move is set to "done" and the product
becomes available.

It uses queue jobs to release the moves in order to have a minimal impact
on the user operations.

The conditions to trigger the check are:

* A job to check the availability of stock moves has been created

At this point, jobs are generated:

* One job per product
* Any available moves releasable are processed
