This module prevents the user from applying an inventory on a quant if some
quantity has been put as done on a move line not yet validated for the same
product, location, lot and package.

Setting the counted quantity remains allowed (e.g. by automated processes
requesting a count), but quants being picked are flagged with an icon in the
inventory list view. Clicking on it opens the move lines in progress.
