This is an example scenario with two warehouses. WH2 will be allways supplied
through WH1.

Common steps to `mrp` and `purchase` procurements:

#. Go to *Inventory > Configuration > Settings > Warehouse* and set *Multi-Step
   Routes* on.
#. Go to *Inventory > Configuration > Warehouse Management > Warehouses*
#. Create **WH1** with either *Manufacture to Resupply* or *Buy to
   Resupply* this warehouse or both set.
#. Create **WH2** setting off *Manufacture to Resupply* and *Buy to
   Resupply*. Set **WH1** as the *Resupply Warehouse*.
#. Go to *Inventory > Configuration > Warehouse Management > Routes* and click
   on the *Make To Order* one.
#. Add a new *Procurement Rule* with these settings and save:

   - Name: *WH1 -> WH2-MTO*
   - Action: *Pull From*
   - Operation Type: *WH1: Internal Transfers*
   - Source Location: *WH1/Stock*
   - Destination Location: *WH2/Stock*
   - Move Supply Method: *Take From Stock*
   - Propagation of Procurement Group: *Propagate*
   - Propagate cancel and split: `True`
   - Warehouse to Propagate: *WH1*

Now if you want to trigger a manufacture:

   - Create a stockable product product with a BoM list.
   - In the product's *Inventory > Routes section* set *Make To Order* and
     *Manufacture* on.

Or if you want to trigger a purchase:

   - Create a stockable product product with a supplier.
   - In the product's *Inventory > Routes section* set *Make To Order* and
     *Purchase* on.
