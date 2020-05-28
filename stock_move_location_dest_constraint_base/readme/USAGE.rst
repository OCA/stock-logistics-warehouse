To define new constraints on stock location, function
`check_move_dest_constraint` on `stock.location` must be overriden to throw a
ValidationError if the location is not allowed for selected product or stock
move line.
