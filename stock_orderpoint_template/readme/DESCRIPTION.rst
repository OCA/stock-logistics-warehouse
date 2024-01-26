This module helps creating orderpoints automatically using templates.
A template is similar to an orderpoint, but it is not linked to a product.

When a picking is validated, the system will look for templates that match
the product and location of the picking. If there is no orderpoint but a 
template is found, it will create an orderpoint for the product and location
of the template.

The new orderpoint is linked to the template, and a change in the template values
will propagate to the orderpoints. To avoid this, you can unlink the orderpoint
by setting its template to False.
