This is an example scenario with two warehouses. WH2 will be allways supplied
through WH1.

Common steps to `mrp` and `purchase` procurements:

#. Go to *Inventory > Configuration > Settings > Warehouse* and set *Multi-Step
   Routes* on.
#. Go to *Inventory > Configuration > Warehouse Management > Warehouses*
#. Create **WH1** with either *Manufacture in this Warehouse* or *Purchase to
   resupply this warehouse* or both set.
#. Create **WH2** setting off *Manufacture in this Warehouse* and *Purchase to
   resupply this warehouse*. Set **WH1** as the *Resupply Warehouse*.
#. Go to *Inventory > Configuration > Warehouse Management > Routes* and click
   on the *Make To Order* one.
#. Add a new *Procurement Rule* with these settings and save:

   - Name: *WH1 -> WH2-MTO*
   - Action: *Move From Another Location*
   - Procurement Location: *WH2/Stock*
   - Served Warehouse: *WH2*
   - Source Location: *WH1/Stock*
   - Move Supply Method: *Create Procurement*
   - Operation Type: *WH1: Internal Transfers*
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
