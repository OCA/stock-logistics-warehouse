This module introduces an automatic and transparent solution to this problem. Upon confirming a component's move for a manufacturing order with only partial stock, the module splits the original move as follows:

* **Make to Stock (MTS) Move**: A move is created for the quantity that is available in the warehouse. This move is set to **"Assigned"** status, ready to be consumed by the manufacturing order.
* **Make to Order (MTO) Move**: A second, entirely new move is created for the missing quantity. This move is set to **"Confirmed"** status or "Waiting Availability," generating a clear and traceable purchase requirement (or a new manufacturing order if it's a sub-assembly) for the purchasing team.
