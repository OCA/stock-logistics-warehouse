Inventory --> Operations --> Import Stock Quantities

Load a csv containing the new data of stock information.

The file must contain at least two columns. Using a form, choose which column will be used to get the product Internal Reference and another one to get the amount to update.

The import process tries to run the update for all the products specified in the file; if a product isn't found, the process simply skips it.

Enabling 'Strict Mode' disables the skip, at the end no product will be updated and an error message will show which products weren't found.
