# Bangladesh sample agreement defaults

Deploy the app update, run site migration and clear cache. Reload Desk to load the updated Sales Agreement script. These changes are not deployed by editing this repository alone.

## Use

1. Create a Sales Agreement and select Property Booking, or use the booking's Create action.
2. Customer, company, prices, property snapshot and available party details populate from the linked records. Sample terms also load before a booking is selected.
3. Review the sample clauses, expected handover date and registration-cost allocation. Edit them for the actual transaction.
4. Complete unavailable identity, signatory and commercial details. Save, review and submit through the usual process.
5. Existing drafts can use Fill Missing Agreement Details. Existing populated fields are preserved. Submitted agreements are not backfilled.
6. Print using Sales Agreement or Detailed Sales Agreement. Both display the saved property snapshot for new agreements; older records without a snapshot retain the legacy property layout.

## Master data mapping

- Company: company name, linked address and optional `custom_authorized_signatory` or `authorized_signatory`.
- Customer: name, mobile/email, primary linked Address and Contact (otherwise most recently modified primary linked record, with name as tie-breaker).
- NID/passport: optional Customer fields `custom_nid_passport`, `custom_national_id`, `national_id`, `passport_number`, in that order. Tax ID is not substituted for identity.
- Property: project name/address, building and floor names, unit number/type/category/area/facing/rooms, Item name and land references. A saved HTML snapshot avoids later master edits changing these printed particulars.
- Facilities: Unit description, falling back to Item description. Parking is copied only if the Unit has a `parking_details` field; no parking entitlement is inferred.
- Expected possession: project expected completion date, subject to review as the contractual date.

An existing agreement cannot switch booking; create another agreement instead. On a new form, switching booking replaces party/property defaults while retaining edited general clauses. Read permissions are enforced for linked source records; grant the required master-data access to agreement preparers.

## Sample wording scope

English sample terms cover payments, default, cancellation/refunds, handover, utilities, maintenance, defects, registration/title documents, notices/disputes and annexures. They do not invent tax rates, penalties, refund periods, title approvals, warranty durations or banking instructions. Registration costs default to As Agreed in Special Terms rather than automatically charging the Buyer.

Bangladesh context reference: [Real Estate Development and Management Act 2010, official English text](https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-legislativediv/2024/12/e9a5efff93b24a12bb294eb9486676b7.pdf). Sample wording needs project-specific review before execution; it is not a legal compliance certification.

## Verification on the site

Test a customer with primary address/contact, one without contact details, an existing draft containing edited clauses, and a new form that switches bookings. Verify the unit and party details, save and print both formats. Changing master property details after saving must not change the stored property snapshot. Confirm submitted historical agreements remain untouched.
