In odoo, you can update the quantity on a quant by filling the
counted quantity on the quant form view and clicking on the "Apply inventory"
button at the end of the line. Unfortunately, nothing prevents you from doing
this for a quant and location in front of which you are  standing to perform
an inventory while some quantity have already been picked from the location by
another user but not yet validated. This can lead to stock discrepancies since
the quantity you are updating is not the actual quantity in the location for the
system and when the picking will be validated, the system will decrease the
quantity you just updated by the quantity that was picked by the other user.

This module prevents this by preventing the user from updating the quantity on
a quant if some quantity has been put as done on a move line not yet validated
for the same product, location, lot and package.
