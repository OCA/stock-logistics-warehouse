* A new menu item Operations > Move from location... opens a wizard
  where 2 locations can be specified.
* Select origin and destination locations and press "IMMEDIATE TRANSFER" or "PLANNED TRANSFER"
* Press `ADD ALL` button to add all products available
* Those lines can be edited. Move quantity can't be more than a max available quantity
* Move doesn't care about the reservations and will move stuff anyway
* If during your operation with the wizard the real quantity will change
  it will move only the available quantity at the button press
* Products will be moved and a form view of picking that did that will show up
* If "PLANNED TRANSFER" is used - the picking won't be validated automatically

If you want to transfer a full quant:

*  Go to `Inventory > Products > Products` and click "On hand" smart button
   or `Inventory > Reporting > Inventory`, the quants view will be
   opened.

*  Select the quantities which you want move to another location

If you go to the Inventory Dashboard you can see the button "Move from location"
in each of the picking types (only applicable to internal transfers). Press it
and you will be directed to the wizard.

If you want transfer everything from stock.location

On a draft picking, add a button to fill with moves lines for all products in
the source destination. This allows to create a picking to move all the content
of a location. If some quants are not available (i.e. reserved) the picking
will be in partially available state and reserved moves won't be listed in the
operations.
Use barcode interface to scan a location and create an empty picking. Then use
the fill with stock button.
