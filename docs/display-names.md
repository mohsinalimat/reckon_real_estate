# Names in links, lists and reports

Real Estate masters display their descriptive names in Link fields. Projects use
Project Name, buildings use Building Name, floors use Floor Name and units use
Unit No. Search supports names and document IDs. List views retain the ID column.

Transactions receive a generated Name composed of relevant customer, unit,
project, party and date values. For example: `Rahim — A501 — Lake View — 2026-09-07`.
Saving transactions refreshes this label. Updating a linked master name refreshes
affected transaction labels without resaving their business data.

The nine app reports include name columns beside supported linked ID columns.
Name lookups respect read permissions. Document IDs and stored links are unchanged.

## Apply the update

1. Deploy the updated app code to the Frappe bench using the normal release process.
2. Run `bench --site erp.reckon.tech migrate` from the bench directory.
3. Run `bench build --app reckon_real_estate` and restart bench services using the
   environment's normal process.
4. Run `bench --site erp.reckon.tech clear-cache`.
5. Sign out and back in, then refresh the browser to reload Link display settings.
6. Check Project, Building, Floor and Unit lists, then open Property Booking and
   verify that selecting a project and unit shows their names. Confirm IDs remain
   visible in lists and reports.

Migration backfills generated transaction names, including submitted records,
without changing their modified timestamps. It also enables name display for
supported shared ERPNext masters such as Customer, Supplier and Item; those
shared display settings apply wherever those masters are linked in the site.

Local tests cover metadata, label generation, migration backfill and report
permissions. Live Frappe UI verification is required after deployment.
