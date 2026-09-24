To configure this module:

**User Groups:**
1. Go to *Settings > Users & Companies > Users*
2. For users managing non-restricted products (e.g., subsidiary users):
   - Assign them to the **Product Creation** group under Inventory
3. For users managing all products (e.g., production department):
   - Assign them to the **Product Creation - Restricted** group under Inventory

**Product Categories:**
1. Go to *Inventory > Configuration > Product Categories*
2. Open a category that should be restricted (e.g., production master data)
3. Check the **Restricted Access** field and save

**Warehouses:**
1. Go to *Inventory > Configuration > Warehouses*
2. Open a warehouse that should be restricted (e.g., main production)
3. Check the **Restricted Access** field and save

**Note:** The **Product Creation** group is useful when you remove
existing product creation access from App Administrator groups to
implement tighter security controls. This allows you to grant specific
product creation permissions without giving full administrative access.
