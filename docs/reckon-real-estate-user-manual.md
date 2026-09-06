# How to use this manual

This manual explains how to implement Reckon Real Estate on an existing ERPNext site and operate the module from project creation through collections, construction, handover and after-sales service. Follow the setup sequence before entering live transactions. Use individual chapters as task references after training.

The instructions describe the repository reviewed on 5 September 2026. The repository is marked under development. They have been checked against the app source, including form fields, buttons and validation rules; they have not been tested against your deployed site. Site customizations, permissions and configured workflows can change what a user sees.

## Reading the procedures

Each task gives its prerequisites, the steps to perform and the expected result. Names such as Property Booking and Collect > Installment match the app. Use Desk search to open the named record or report when a workspace link is unavailable. Save creates or updates a draft. Submit confirms a submittable document and runs its submission logic.

Screenshot captions beginning SS identify positions for later images. Insert the screenshot immediately before its caption, use inline wrapping and retain the identifier. Capture sample records and mask personal or financial information. The document remains usable without screenshots.

## Where to start

Implementers and administrators should read chapters 1 to 4, then complete the acceptance checks in chapter 22. Sales and collections staff should use chapters 5 to 11. Construction and purchasing staff should use chapters 12 to 15. Land, handover and service staff should use chapters 16 to 18. Managers should use chapters 19 and 20.

ERPNext is the accounting source of truth. Booking, agreement, budget and certification records describe operations. Submitted native invoices, payments and stock documents create the accounting or inventory effects. A saved or submitted real estate record does not always mean a corresponding ERPNext voucher has been posted.

# Contents

1  Implementation sequence
2  Install and validate the app
3  Configure users and ERPNext masters
4  Navigation and document controls
5  Create the project and property hierarchy
6  Create saleable units
7  Book a unit
8  Prepare the sales agreement
9  Build the installment plan
10  Create the invoice and collect payments
11  Check collections and correct transactions
12  Prepare the BOQ and project budget
13  Create contractor work orders
14  Certify measurements and running bills
15  Purchase materials and issue stock
16  Record land and joint venture allocations
17  Complete handover and resolve snags
18  Manage warranty and after-sales service
19  Record sales targets and commissions
20  Use reports and management dashboards
21  Troubleshooting reference
22  Acceptance testing and go live
23  Field and status quick reference
24  Screenshot register and maintenance notes

Use Word's Navigation Pane to jump to headings. Each chapter begins on a new page. The chapter numbers are stable reference identifiers; page numbers may change when screenshots are inserted.

# 1 Implementation sequence

## Prepare the rollout

1. Nominate an implementation owner and business reviewers for sales, accounts, construction and handover. Record the company, projects and users included in the first rollout.
2. Select a test site with an existing supported Frappe and ERPNext stack. Record the app revision being deployed and back up the site before installation or migration.
3. Agree company currency, fiscal periods, accounts, cost centers, warehouses, payment modes, tax settings and the Item mapping for each saleable unit.
4. Install the module and verify the Real Estate workspace, roles, forms and reports as described in chapters 2 and 3.
5. Prepare master data in dependency order: Company and native accounting masters; Real Estate Project; Building; Floor; Unit; Customer; sales transactions. Set up Suppliers and Items before construction transactions.
6. If land ownership is in scope, create Land Owners and Land Parcels, then JV Agreements and Allocations. Units must exist before allocating a flat.
7. Run the sales, construction and after-sales examples on the test site. Include rejection cases and native voucher checks, not only successful saves.
8. Confirm user permissions and operating procedures, train each team, complete the opening-data reconciliation and obtain business sign-off before live entry.

## Opening data

Prepare a mapping sheet of legacy identifiers to new project, unit, customer, booking, plan and invoice identifiers. Reconcile each existing customer's contract value, down payment, installment schedule, receipts and remaining balance. Import or enter parents before children. Submit in dependency order where required.

Do not replay historic collections through Collection Entry when their payments are already posted in ERPNext without a reviewed migration plan: submitting a collection creates another Payment Entry. The repository does not provide a general legacy-balance conversion wizard. An implementer should agree how opening invoices, receipts and operational schedules will be reconciled.

## Completion evidence

Retain the installation result, role test results, master-data mapping, sample document numbers and signed acceptance checklist. These form the implementation record and the baseline for future upgrades.

# 2 Install and validate the app

Audience: Frappe administrator. Prerequisite: a working Bench environment with ERPNext already installed on the target site. Run the commands in the server's Bash shell from the bench directory; these are not Windows PowerShell commands.

## Installation steps

1. Verify that Frappe and ERPNext have matching major versions. The app's installation check supports version 15 with 15, or version 16 with 16. It rejects unsupported or mismatched majors.
2. Back up the target site and record its current apps and versions using your normal Bench administration process.
3. Fetch the app into the bench, unless it has already been copied or fetched there.

CODE cd ~/frappe-bench
CODE bench get-app https://github.com/mzakirhossain/reckon_real_estate

4. Replace yoursite with the actual site name and run the supplied installer.

CODE bash apps/reckon_real_estate/scripts/install.sh yoursite

5. The script runs install-app, migrate, the app asset build, cache clearing and the app's installation validation. Read the output and resolve any error before continuing.
6. Run the separate validation script and retain the result.

CODE bash apps/reckon_real_estate/scripts/validate_install.sh yoursite

7. Sign in to ERPNext and open /app/real-estate. Confirm the workspace opens and the named forms and reports can be found.

## What validation covers

The app checks supported stack versions and required custom and ERPNext DocTypes. Installation and migration also set up app roles, permissions, navigation, traceability fields and workspace analytics. Validation does not certify your accounting settings, user access, balances or complete transaction flow; test those separately.

For an upgrade, back up and deploy the intended app revision through your existing Bench process, then migrate, rebuild assets, clear cache and rerun validation. Do not treat the new-install script as a complete upgrade or rollback procedure.

SS01  Insert the Real Estate workspace after successful installation.

# 3 Configure users and ERPNext masters

## Assign access

1. Open User using Desk search. Create or open the staff member's system user and assign the appropriate module role.
2. Use Reckon Real Estate User for normal entry and submission. This role receives read, create, write, submit, report, export, print and email permissions on applicable module documents.
3. Use Reckon Real Estate Manager for staff who also need cancellation, amendment, deletion, import and sharing capabilities. System Manager has the standard administrative permissions shipped with the forms.
4. Configure the native ERPNext permissions needed by each job: Customer and Item access for sales; Sales Invoice and Payment Entry access for collections; Supplier, Purchase Order, Purchase Invoice and Stock Entry access for construction and accounts.
5. Sign in as representative users and test the complete task, including linked native vouchers. App roles alone do not grant all ERPNext permissions.

The built-in User role can submit; it is not a draft-only maker role. Configure and test your own approval workflow if another person must approve transactions. Installation and migration reapply app-owned permissions, so review custom permission arrangements after an upgrade.

## Prepare shared masters

| Master | Setup to confirm |
| Company | Correct currency, fiscal configuration and default or root Cost Center |
| Accounts | Receivable, payable, cash or bank and income/expense ledgers with company defaults |
| Mode of Payment | Valid payment modes and company account configuration |
| Customer and Supplier | Correct party names, active status and account defaults |
| Item and UOM | Saleable unit mapping, construction services and stock materials |
| Warehouse | Company warehouse and stock availability if inventory is used |

Finance should validate taxes, account selection, currency and rounding on sample native vouchers. A project warehouse is needed when a mapped stock unit is to reduce stock on invoicing. Agree a convention for building and floor records even for plot or parking sales because the Unit form requires both.

SS02  Insert a sample user's roles and relevant permissions.

# 4 Navigation and document controls

## Find and open records

1. Sign in to ERPNext Desk and open Real Estate, or go to /app/real-estate.
2. Open the required list or search for the exact DocType name. Use list filters to narrow the records and open an existing record, or select New to create one.
3. Complete required fields. Link fields select an existing record; select the correct document identifier where similar display names exist.
4. Save the record and review fetched values and calculated totals. When the procedure requires submission, use Submit and confirm the action.
5. Reopen the saved record to verify Document Status, linked records and the expected business status.

## Understand the two statuses

Document Status is Draft, Submitted or Cancelled on forms that expose that field. Some forms use Status for the submission state; others also have a separate business Status, such as a Unit being Available or Booked. Changing a business-status field does not replace Submit or Cancel.

Most Create actions appear only after the source record is submitted. They may open an unsaved target form or insert a draft native voucher. Review the target and finish its own Save and Submit procedure. The Collect actions have an additional invoice-posting effect described in chapter 10.

## Correct a record

Edit a draft and Save. For a submitted document, use the permitted Cancel and Amend process where applicable. Resolve downstream documents first; the app blocks several parent cancellations while submitted children exist. Do not bypass these checks by manually changing status fields.

Land Owner, Sales Target, Snag and Service Request use Save without submission. Installment Schedule and Payment Allocation are child rows maintained within their parent forms, not separate user transactions.

Print formats Sales Agreement and Detailed Sales Agreement are supplied for agreements. Preview the selected format and check buyer, unit and commercial terms before printing. Site-specific attachments and approval rules should follow the organization's normal Frappe procedures.

SS03  Insert a submitted form showing Document Status and the Create menu.

# 5 Create the project and property hierarchy

Prerequisites: Company and its Cost Center structure exist. Enter the project and accounting mappings before creating child properties.

## Create the project

1. Open Real Estate Project > New. Enter Project Name and Company.
2. Enter Project Type, Start Date, Expected Completion Date, Location and Address as appropriate. The completion date cannot precede the start date.
3. Select an existing ERPNext Project and Cost Center if already established. They must belong to the selected Company. For new mappings, leave these links empty and verify the generated links after submission.
4. Set Project Warehouse if stock is used. Set Default Sales Income Account if the project needs a specific income ledger; it must be a non-group Income account for the same Company.
5. Save and Submit. Submission creates or links the native ERPNext Project and Cost Center when their links are empty. Check both links before invoicing or construction posting.

## Create a building and floor

1. From the submitted project, select Create > Real Estate Building. Enter Building Name and confirm Project. Add Total Floors and Notes where needed. Save and Submit.
2. From the submitted building, select Create > Real Estate Floor. Enter Floor Name and Floor Number; confirm Project and Building. Save and Submit.
3. Repeat for each building and floor. Each floor must match its selected building's project. The parent must be submitted before the child's submission.

Expected result: a submitted Project > Building > Floor hierarchy is ready for units. System-generated codes identify records; use the descriptive names and numbers for business labels.

Project Total Units is recalculated when the project is validated and excludes cancelled units. Treat it as a saved count rather than a guaranteed live dashboard value after every child change.

SS04  Insert the project showing ERPNext Project and Cost Center mappings.
SS05  Insert the building and floor hierarchy using sample records.

# 6 Create saleable units

Prerequisites: submitted project, building and floor; an ERPNext Item ready for the sale if invoicing is in scope.

## Enter the unit

1. Open the submitted floor and select Create > Real Estate Unit.
2. Enter Unit No and confirm Project, Building and Floor. The floor must belong to both the selected building and project.
3. Choose Unit Type: Apartment, Office, Shop, Plot, Parking or Other. Enter Unit Category if your organization uses one.
4. Enter Area (Sqft) and Base Rate / Sqft. Add Bedrooms, Bathrooms, Facing and Description as relevant.
5. Select ERPNext Item. Although this link is not mandatory to save the unit, the invoice generator requires it.
6. Confirm the intended availability Status, Save and review List Price. Submit after checking the full record.
7. Open Unit Availability and filter the project to confirm the unit can be found with the expected status.

## Example

For a sample unit A501, Area (Sqft) = 1,000 and Base Rate / Sqft = 5,000 produce List Price = 5,000,000. These are illustrative amounts in the site's currency. A later booking records its own contract value and discount; the unit's list price is a reference rather than a posted sale.

## Land and stock references

The Proportionate Land fields are read-only on the unit and are populated by submitting a linked JV Allocation. Follow chapter 16 to maintain those values.

Unit availability and ERPNext stock are separate controls. A linked stock Item causes an invoice stock update only when the project also has a Project Warehouse. Review warehouse availability and valuation before posting such an invoice.

Booking submission changes the unit to Booked. Handover submission changes it to Handed Over. Other selectable values should be managed under your operating procedure; do not assume every intermediate status changes automatically.

SS06  Insert Unit details showing area, rate, price, status and ERPNext Item.

# 7 Book a unit

Prerequisites: submitted Unit and an existing ERPNext Customer. Confirm the unit's availability before starting the booking.

## Booking steps

1. Open the submitted unit and select Create > Property Booking.
2. Select Customer and enter Booking Date. Confirm Project and Unit.
3. Enter Contract Value, Discount and Booking Money. Record any remaining booking information required by your organization.
4. Save and review Net Contract Value, calculated as Contract Value minus Discount. A discount greater than the contract value is rejected.
5. Confirm the customer and commercial terms, then Submit.
6. Verify that the booking is Active and the unit is Booked. Use Create > Sales Agreement for the next step.

The app checks that the customer exists and the unit belongs to the selected project. New bookings are checked against active bookings for the same unit. If a duplicate warning appears, open and review the existing booking rather than creating a workaround record.

## Worked commercial example

| Entry | Sample value |
| Contract Value | 5,000,000 |
| Discount | 100,000 |
| Net Contract Value | 4,900,000 |
| Booking Money | 900,000 |
| Balance to schedule | 4,000,000 |

Booking Money defines the down payment copied into the agreement and installment plan. Entering that amount on the booking does not record cash received and does not create a Payment Entry. Record the receipt through the collection workflow after the agreement and plan are ready.

## Cancellation

A manager must resolve submitted Sales Agreements and Installment Plans before cancelling their booking. Successful booking cancellation changes the unit back to Available. Financial reversals and refunds require separate ERPNext processing and reconciliation; cancelling the booking alone does not return customer money.

SS07  Insert a submitted Property Booking showing values and Create > Sales Agreement.

# 8 Prepare the sales agreement

Prerequisite: submitted Property Booking with reviewed commercial values.

## Agreement steps

1. Open the submitted booking and select Create > Sales Agreement.
2. Confirm Booking. On validation, the app copies Customer, Project, Unit, Company, Contract Value, Discount, Net Contract Value and Booking Money from the booking. Buyer Name is fetched from Customer.
3. Enter the Agreement Date and the required agreement particulars. Review buyer identity and address, seller information and unit details available on the form.
4. Complete the applicable commercial clauses, payment terms, possession or handover terms, notices and dispute terms, annexures and other terms. Use the organization's approved wording.
5. Save and review the entire agreement. Only one non-cancelled Sales Agreement is allowed for a booking.
6. Preview Sales Agreement or Detailed Sales Agreement using the Print view. Check the populated fields and text layout before issuing the agreement through your normal process.
7. Submit the agreement when ready. Verify Status becomes Active. Select Create > Installment Plan to continue.

## How agreement changes affect later work

The agreement copies its core financial figures from the booking when validated. To change those figures, correct the underlying commercial documents through the permitted workflow rather than treating the copied amount as an independent negotiated figure.

A submitted Installment Plan blocks cancellation of its Sales Agreement. Plan and invoice dependencies therefore need to be resolved before an agreement can be replaced. Use chapter 11 for the correction sequence and involve accounts where posting has occurred.

Agreement submission does not itself create the Sales Invoice. The next steps are to submit the Installment Plan and create its invoice, or use its Collect action with the posting behavior explained in chapter 10.

The agreement also provides Create > Handover. Use that later, after financial clearance and inspection, as described in chapter 17.

SS08  Insert agreement particulars and the selected agreement print preview.

# 9 Build the installment plan

Prerequisite: submitted Sales Agreement. The plan's booking, customer, project and unit must refer to the same sale. Only one non-cancelled plan is allowed for an agreement.

## Generate a standard schedule

1. From the agreement, select Create > Installment Plan and check the copied links.
2. Enter Plan Start Date and Number of Installments. Choose Monthly, Quarterly, Half-Yearly or Yearly.
3. Check Agreement Amount and Down Payment. These are taken from the agreement's net contract value and booking money.
4. Select Create Installment Schedule. The action replaces all existing schedule rows; review or preserve any manual edits before using it again.
5. Review Installment No, Due Date, Description, Principal and any Other Charges in every row. The first installment falls on Plan Start Date, not one period later. Later dates advance by the chosen interval.
6. Save and check Total Scheduled. It must equal Net Contract Value minus Down Payment within 0.01. Submit when the schedule is agreed.

## Custom schedules and rounding

Choose Custom and enter the schedule rows manually; automatic generation requires a standard frequency. Keep installment numbers unique and sequential and enter each due date and amount. Row Total Amount is Principal plus Other Charges. Charges are included in the required schedule total, not automatically added above the contract balance.

For the chapter 7 example, 4,000,000 divided into 10 monthly installments gives 400,000 per row. Starting 1 October 2026 produces dates from 1 October 2026 through 1 July 2027. The down payment remains separate. The generator adjusts the final row for rounding differences.

## Reading status

Paid means outstanding is at most 0.01. A row with some payment and a remaining balance shows Partial, even if overdue. Otherwise its due date determines Upcoming, Due or Overdue. A daily scheduled job refreshes installment statuses. Use date-based aging for overdue partial payments.

SS09  Insert plan settings and the generated installment rows.

# 10 Create the invoice and collect payments

Prerequisites: submitted Installment Plan; project accounting dimensions; Unit ERPNext Item; valid native account and payment settings. This procedure can post accounting entries.

## Review the sales invoice first

1. On the submitted plan, select Create > Sales Invoice. The app inserts a draft invoice for quantity 1 of the unit's mapped Item at the agreement's net contract value.
2. Review Customer, Company, Posting Date, accounts, taxes, Project, Cost Center and Payment Schedule. Posting Date comes from Plan Start Date. The payment schedule includes the down payment and installment rows.
3. Save any permitted corrections and Submit the invoice. Verify the posted receivable and the link back to the plan.

The Collect actions ensure there is a submitted invoice: they can create and submit a missing invoice, or submit an existing draft, before opening Collection Entry. Complete the invoice review first when accounts must approve the invoice before posting.

## Collect the down payment or an installment

1. On the plan choose Collect > Down Payment, or Collect > Installment and select the installment number, then Create Collection.
2. Review the new Collection Entry's date, customer, project, unit, booking and allocation. The proposed amount is the remaining down payment or selected installment outstanding.
3. Enter Payment Mode and Reference No. For a partial receipt, reduce both Amount and the allocation's Allocated Amount to the actual receipt.
4. For a receipt covering several installments, add separate Payment Allocation rows. Select the plan, Allocation Type and Installment No as applicable. Allocate the entire receipt before saving.
5. Save, check Unallocated Amount is zero and Submit. Submission creates and submits the linked ERPNext Payment Entry automatically.
6. Open ERPNext Payment Entry and confirm the amount, bank or cash account, reference and invoice allocation. Refresh the plan and check the installment's paid and outstanding values.

Amounts and allocations must be positive. Total allocations cannot exceed the receipt; allocations cannot exceed the relevant installment, down-payment remainder or invoice outstanding.

SS10  Insert the invoice payment schedule.
SS11  Insert Collection Entry allocations and its posted Payment Entry link.

# 11 Check collections and correct transactions

## Daily collection checks

1. Open Collection Entry and review today's submitted receipts. Confirm each has an ERPNext Payment Entry and Accounting Status = Posted.
2. Run Property Ledger for the Customer and, where useful, Project and Unit. Compare ERPNext Collections and ERPNext Outstanding with the native invoice and payment records.
3. Run Installment Due Collection Aging with the relevant filters and Only Outstanding selected. Review due dates and outstanding amounts, including partly paid rows.
4. Run Accounting Reconciliation by project. Investigate missing, draft or cancelled native vouchers linked to submitted operational documents.

## Correct an erroneous collection

1. Record the source and voucher identifiers and agree the correction with accounts.
2. Cancel the linked submitted Payment Entry first, using the native reversal procedure. If the linked payment is draft, the Collection Entry cancellation check requires the draft payment to be deleted first.
3. Cancel Collection Entry. This reverses its installment allocations. Cancelling Payment Entry alone updates Accounting Status but does not reverse the operational schedule allocations.
4. Recreate or amend the collection as allowed, allocate the correct amount and Submit. Recheck the native invoice and installment balances.

## Replace an erroneous sale or process a refund

For a correction requiring cancellation of the sale chain, resolve payments and collections first, then the invoice, Installment Plan, Sales Agreement and booking as required. The plan blocks cancellation while its linked invoice is not cancelled or while submitted collections reference it. Respect ERPNext's additional linked-document checks.

For a posted-sale return or cash refund, accounts uses native Credit Notes, outgoing Payment Entries and Payment Reconciliation as applicable. These are separate financial transactions; this manual does not prescribe accounting policy or a universal cancellation shortcut.

Direct ERPNext payments, journal entries, refunds and reconciliations do not automatically rebuild installment-row allocations in this app. Reconcile the operational schedule separately. Property Ledger displays linked invoices and collection-backed payments and is not a complete substitute for native account ledgers.

SS12  Insert Property Ledger and an Accounting Reconciliation exception.

# 12 Prepare the BOQ and project budget

Prerequisites: project, company, construction Items, UOMs and account mapping. BOQ means Bill of Quantities.

## Create the BOQ

1. Open BOQ > New. Select Real Estate Project, Company and Effective Date.
2. Add Items with Item Code, description, UOM, Quantity and Rate. Supply a Cost Center where the row needs one.
3. Save and verify each amount equals quantity multiplied by rate and Total Amount equals the sum of the rows.
4. Check the Company matches the project and Submit. Use the standard permitted Cancel and Amend flow for revisions.

## Create the project budget

1. From the submitted BOQ choose Create > Project Budget. The action copies the BOQ, project and company links; it does not populate the account budget rows.
2. Enter From Date and To Date and the other required budget information on the form. The end date cannot precede the start date.
3. Add budget rows with Account, Budget Amount and Cost Center where appropriate. Use accounts consistent with the expense mapping on purchase orders and invoices.
4. Save and confirm Total Budget equals the sum of the budget rows. Submit.
5. Use Create > Contractor or Create > Contractor Work Order to continue.

## Review cost control

Budget vs Actual compares submitted budget rows with posted GL actuals and qualifying open purchase-order amounts. Actuals use the budget's date range and account; commitments come from matching project and expense-account rows on open submitted purchase orders.

The commitment calculation uses the full base amount on qualifying open PO rows; it is not a guaranteed remaining unbilled balance. Review partly fulfilled orders and overlapping budgets before interpreting totals. Budget submission does not create an ERPNext GL entry, and this module's budget form does not itself impose a spending approval or hard-stop rule.

Expected result: a submitted BOQ and Project Budget ready to support work orders and reporting.

SS13  Insert BOQ items and totals.
SS14  Insert Project Budget account rows and dates.

# 13 Create contractor work orders

Prerequisites: an active ERPNext Supplier and a submitted Project Budget.

## Register the contractor

1. Open Contractor > New. Enter Contractor Name and select Supplier.
2. Enter Contractor Type, Tax ID and contact details as applicable. The linked supplier must not be disabled.
3. Save and Submit. A contractor profile uses the existing Supplier for purchasing and payment; it does not replace the native party master.

## Create the work order

1. From the submitted Project Budget select Create > Contractor Work Order. Confirm Project Budget, Project, Company and BOQ.
2. Select the submitted Contractor. Enter Start Date and End Date. The end date cannot precede the start date.
3. Enter the Items, ordered quantities, UOMs and rates. Enter Retention Percent and Terms if applicable.
4. Save and check Total Amount. The project must match the budget, and the company must match the project. The BOQ is taken from the selected budget.
5. Submit the work order. Then choose Create > Purchase Order.
6. Review the generated draft Purchase Order, including Supplier, items, rates, schedule date, expense accounts and project dimensions. Submit it through the normal ERPNext purchasing procedure.
7. Return to the work order and verify the Purchase Order link. Use Create > Measurement Sheet when work is ready to certify.

## Operating notes

Work-order submission does not itself submit a Purchase Order. A missing Create > Purchase Order button can mean an order is already linked; open the link before trying to create another order.

Keep service and stock Item mappings meaningful. Material Issue uses stock Items from the work order; it does not infer a separate material-consumption list from service quantities.

To cancel a work order, submitted Measurement Sheets must be resolved first and the linked submitted Purchase Order must be cancelled. Check all native purchasing dependencies before attempting that sequence.

SS15  Insert the contractor supplier mapping and work order Purchase Order link.

# 14 Certify measurements and running bills

Prerequisite: submitted Contractor Work Order. Use the source's Create actions to retain row links.

## Certify completed work

1. On the work order select Create > Measurement Sheet. Enter Measurement Date, Period From and Period To.
2. Enter the quantity completed in this period on each mapped work-order row. Review Certified By and remarks.
3. Save. The app copies item, UOM and rate from the work order, calculates previous and cumulative quantities, and rejects cumulative measurement above the ordered quantity.
4. Review the certification and Submit. Select Create > Running Bill.

## Prepare and invoice the bill

1. Enter the required Bill Date and contractor invoice particulars. Review copied quantities, rates and Retention Percent.
2. Enter Other Deductions if applicable. Save and review Gross Amount, Retention Amount and Net Payable.
3. Confirm the billed quantities do not exceed this Measurement Sheet and Submit the Running Bill.
4. Select Create > Purchase Invoice. Review and submit the generated native invoice after accounts has checked supplier, item amounts, taxes, deductions and project dimensions.
5. Record supplier payment against the Purchase Invoice through ERPNext. Check the invoice's actual outstanding amount after payment.

## Retention and payment example

Gross work of 100,000 with 5% retention and 2,000 other deductions gives Retention Amount = 5,000 and Net Payable = 93,000. The generated Purchase Invoice contains the gross item quantities and rates; retention is mentioned in remarks, but neither retention nor other deductions is automatically posted as a separate deduction or liability. Accounts must implement the agreed treatment in ERPNext.

The Running Bill quantity check is against the selected measurement, not a complete cumulative duplicate-billing control. Review previous bills for that measurement. Its Accounting Status may show Paid when a Payment Entry referencing the invoice is submitted, including a partial payment; native invoice outstanding is the reliable settlement check.

SS16  Insert Measurement Sheet showing previous, current and cumulative quantities.
SS17  Insert Running Bill totals and its Purchase Invoice link.

# 15 Purchase materials and issue stock

Prerequisites: stock Items, UOMs, company warehouses and the appropriate buying and stock permissions.

## Request and receive materials

1. Open a submitted BOQ and select Create > Material Request.
2. Review the draft purchase Material Request. It copies BOQ items and quantities and uses the current date as its initial schedule date. Check dates and remove or correct rows that are not appropriate for this procurement.
3. Save and Submit through the normal ERPNext process.
4. Continue the native procurement process, using quotations if required, Purchase Order, Purchase Receipt and Purchase Invoice as applicable to the item and your purchasing policy.
5. Verify project dimensions and traceability links on the downstream records. Do not assume every native conversion or manually entered voucher has the correct dimensions without checking.

## Issue construction materials

1. Open a submitted Contractor Work Order and select Create > Material Issue.
2. Select Source Warehouse in the prompt. The app creates a draft Stock Entry of type Material Issue using stock Item rows from the work order.
3. Review the draft before posting. Default quantities are the work-order quantities, not the outstanding unissued quantities or the latest measured work.
4. Adjust the quantities to the actual issue, check prior Stock Entries and confirm available stock, warehouse and expense/project dimensions.
5. Save and Submit through ERPNext. Verify the stock and valuation effect using the native stock records.

If the work order contains no stock Items, Material Issue is rejected. Repeated Material Request or Material Issue actions can create additional drafts; examine existing documents before repeating the action.

Purchase Receipt and Stock Entry own inventory quantities and valuation. A BOQ, work order or measurement does not itself move stock. For unit sales, review the stock Item and Project Warehouse combination described in chapter 6.

SS18  Insert a Material Request and a reviewed Material Issue Stock Entry.

# 16 Record land and joint venture allocations

Prerequisites: submitted Real Estate Project and verified land and owner information. Use a consistent area unit; the allocation fields do not provide automatic area-unit conversion.

## Record the parcel and owner

1. Open Land Owner > New. Enter Owner Name and Owner Type. Add National ID / Registration No, Tax ID, contact information and optional Customer or Supplier links. Save; this record is not submittable.
2. Open Land Parcel > New. Select Project and enter Parcel Name, Total Land Area, Area UOM and Acquisition Type: Owned, Joint Venture or Lease.
3. Enter Mouza, Khatian No, Dag No, acquisition date and address as available. Total Land Area must be greater than zero. Save and Submit.

## Record the JV agreement

1. Open JV Agreement > New. Select the submitted Land Parcel and Primary Land Owner and enter Agreement Date.
2. Enter Developer Share % and Owner Share %. They must total 100%; for example, 60 and 40.
3. Enter effective dates and terms. Check that Expiry Date does not precede Effective From. Save and Submit.

## Allocate a flat or other entitlement

1. Open JV Allocation > New. Select JV Agreement and Land Owner, then enter Allocation Date and Allocation Type: Flat, Land or Cash.
2. For Flat, select a Unit belonging to the JV project. Enter Proportionate Land Area, Land Share % and Allocation Value as agreed.
3. Review prior allocations and the overall owner entitlement, then Save and Submit. Negative land area and share values are rejected.
4. Open the linked unit and verify Land Parcel, Proportionate Land Area, Land Share % and JV Allocation.

Allocation submission writes the land fields whenever a Unit is supplied. Use a unit link deliberately. The app does not demonstrate an aggregate entitlement or duplicate-unit allocation check; review totals and earlier allocations manually. An allocation does not create an invoice, payment or legal title transfer.

SS19  Insert parcel title references and JV share percentages.
SS20  Insert a flat allocation and the resulting unit land fields.

# 17 Complete handover and resolve snags

Prerequisite: submitted Sales Agreement. Prepare a draft Handover before creating its Snags.

## Inspect and prepare

1. On Sales Agreement select Create > Handover. Enter Handover Date and Save the draft. Customer, booking, project and unit are derived from the agreement.
2. Open Snag > New and select this Handover. Enter Reported Date, Category, Description and Priority; assign a user and Target Date as needed. Save.
3. Track each snag as Open, In Progress, Resolved, Closed or Reopened. Enter Resolution before selecting Resolved or Closed, then Save. The app records a resolved date; reopening clears that date.
4. Reinspect the unit and ensure all snags are resolved or closed before handover submission.

## Complete financial and customer clearance

1. Ask accounts to confirm the Sales Invoice, down payment, all installment receipts and any other agreed charges are fully reconciled. Check the native invoice outstanding and Property Ledger, not only the installment rows.
2. In Handover, enter Utility Meter Reading, Keys Delivered, Documents Delivered and Acceptance Notes.
3. Obtain the required acceptance evidence and check Customer Accepted. Save and Submit.
4. Confirm the unit is Handed Over. Use Create > Warranty, Maintenance or Service Request to continue.

The automatic submission checks require a submitted agreement, no positive installment-row outstanding above 0.01, no Open/In Progress/Reopened Snag and Customer Accepted checked. They do not independently prove that a plan exists, the down payment was collected or the native invoice is fully settled. The accounts clearance in this procedure is therefore a separate required operating check.

Cancellation restores the unit to Handover Pending. A submitted Warranty blocks cancellation of its Handover. Review other linked after-sales records and the business consequences before requesting cancellation.

SS21  Insert the draft Handover and linked snag list.
SS22  Insert the submitted Handover showing customer acceptance and delivered items.

# 18 Manage warranty and after-sales service

## Register warranty coverage

1. On a submitted Handover select Create > Warranty. Confirm Handover and the derived Customer, Project and Unit.
2. Choose Warranty Type and enter Start Date, End Date and Coverage. The end date cannot precede the start date.
3. Save and Submit. Create separate records where different coverage periods or warranty types need to be tracked.

## Handle a service request

1. From Handover choose Create > Service Request, or create one from its list and select the correct Customer, Project and Unit.
2. Enter Request Date, Category, Subject and Description. Add Priority, Assigned To and Target Date. Link Handover and Warranty where applicable.
3. Save and manage Status through Open, Assigned, In Progress, On Hold, Resolved or Closed as appropriate.
4. Record Resolution before resolving or closing. The app records Resolved Date. Add chargeable status and estimated or actual costs if relevant.

A selected Warranty must be submitted, match the customer and unit, and cover Request Date. A selected Handover must match the customer and unit. Service Request is saved without submission. Cost fields record service information; no automatic invoice or payment is created by the controller.

## Set up maintenance

1. From submitted Handover choose Create > Maintenance.
2. Enter Start Date, optional End Date, Billing Frequency and Rate / Sqft / Month. Add Security Deposit and Terms if applicable.
3. Save and verify Monthly Amount, then Submit. The calculation is Unit Area (Sqft) multiplied by the monthly rate.
4. Arrange billing separately in ERPNext according to your approved process. This record does not automatically generate recurring invoices or collect a security deposit.

For a 1,000 sqft unit at 5 per sqft per month, Monthly Amount is 5,000. Selecting quarterly billing does not change that field into a quarterly total.

SS23  Insert Warranty coverage and dates.
SS24  Insert a resolved Service Request and Maintenance calculation.

# 19 Record sales targets and commissions

Prerequisites: ERPNext Sales Person master, Company and any relevant project or booking.

## Set a sales target

1. Open Sales Target > New and select Company.
2. Select Project and Sales Person if the target is specific to them.
3. Enter From Date, To Date, Target Units and Target Amount. The end date cannot precede the start date.
4. Add Notes explaining the period or scope and Save. Sales Target is not submittable.

## Record a commission

1. Open Sales Commission > New. Select Booking and Sales Person. The app derives Project and Customer from the booking.
2. Enter Commission Base and Commission Rate. Check Commission Amount = Commission Base × Commission Rate / 100.
3. Enter Paid Amount only when supported by an actual payment record. Review Payable Amount = Commission Amount minus Paid Amount; negative payable amounts are rejected.
4. Set the business Status as appropriate and record the Payment Entry link if one exists. Save, review and Submit through the permitted process.
5. When maintaining payment information, use the available permitted editing or amendment process and reconcile to the native payment record.

## Example and limits

A commission base of 4,900,000 at 1% calculates 49,000. If 20,000 has actually been paid, the payable amount is 29,000.

The form supports operational commission tracking. Its controller does not create a Payment Entry or post an accounting accrual automatically, and it does not automatically derive Paid Amount from a payment. Linking a payment is not a substitute for checking its submitted state and amount.

Use the native accounting process for commission liability and settlement according to your organization's policy. Review the Executive Dashboard's unpaid commission figure against commission records and actual posted payments.

SS25  Insert Sales Target and Sales Commission sample records.

# 20 Use reports and management dashboards

Open the exact report name through Desk search, set the filters, run or refresh it, then open linked source records to investigate the result. Export or print only where the user's permissions allow.

| Report | Main use and filters |
| Unit Availability | Find units by Project and Status |
| Property Ledger | Customer is required; narrow by Project and Unit |
| Collection Overdue | Review overdue rows by Customer, Project and Unit |
| Installment Due Collection Aging | Customer, Project, Unit, As of Date, Due From, Due To and Only Outstanding |
| Accounting Reconciliation | Check operational source and native voucher state by Project |
| Budget vs Actual | Compare budget, commitments and GL actuals by Project |
| Construction Dashboard | Review construction progress and cost forecast by Project |
| Executive Dashboard | Review operational sales, collections and forecast metrics by Project |
| Project Profitability | Review GL income and expense by Project and optional date range |

## Interpret results correctly

Installment Due Collection Aging places outstanding amounts into Current / Future, 1–30 Days, 31–60 Days, 61–90 Days and Over 90 Days. As of Date calculates aging against due dates using currently stored paid and outstanding amounts; it is not a reconstruction of historical balances at that date. Down payments are not installment rows.

Accounting Reconciliation checks whether linked native vouchers exist and are submitted. A clean result does not certify the correctness of amounts, account coding or complete balance agreement.

Project Profitability reads non-cancelled GL income and expense for the linked native Project. Date filters apply to GL amounts, while Budget is the total of submitted project budgets. Investigate missing project dimensions if posted costs do not appear.

Workspace cards and Executive Dashboard metrics use different operational and accounting sources. Booked sales are not necessarily posted revenue, and forecasts are not statutory financial statements. Reconcile management totals to the native ERPNext reports before using them for financial reporting.

SS26  Insert aging filters and buckets.
SS27  Insert project profitability and construction or executive dashboard results.

# 21 Troubleshooting reference

Use the record identifier and full error text when escalating a problem. Confirm the current user, project and document state before retrying an action.

| Symptom | Check and next action |
| Workspace or form unavailable | Verify installation, app role, native permissions and site cache; ask the administrator to rerun validation |
| Create action missing | Check source submission, permissions and whether the target voucher is already linked |
| Parent must be submitted | Open the referenced parent, review it and submit in dependency order |
| Project or company mismatch | Correct linked Project, Building, Floor, Unit, Budget or Company so the chain is consistent |
| Active booking or agreement exists | Open the existing record; resolve it through the permitted correction process |
| Schedule total rejected | Compare row totals with net contract less booking money; check rounding and Other Charges |
| Invoice creation fails | Check Unit Item, project dimensions, accounts, dates, taxes, permissions and stock if applicable |
| Collection cannot save | Allocate the full positive amount; check plan, installment and submitted invoice balances |
| Measurement exceeds order | Check earlier submitted measurements and remaining ordered quantity |
| Handover blocked | Clear outstanding installments, resolve open snags and record customer acceptance |
| Warranty request rejected | Check matching customer/unit, submitted warranty and covered Request Date |
| Parent cannot cancel | Resolve linked downstream documents and native vouchers first |

## When figures disagree

Compare native vouchers with collection allocations and installment rows. Payment cancellation alone does not reverse schedule allocations; see chapter 11. For construction, check invoice outstanding, project and expense-account dimensions, PO status and overlapping budgets. Refresh reports after corrections.

# 22 Acceptance testing and go live

Run these checks on a test site. Record the test date, tester, source/voucher identifiers, actual result and any follow-up owner. The sample amounts are illustrative and exclude taxes so the business flow is easy to verify.

| Test | Expected evidence |
| Project and hierarchy | Submitted parents and unit; native Project and Cost Center linked |
| Booking | 5,000,000 less 100,000 gives 4,900,000; unit becomes Booked |
| Plan | 900,000 down payment plus ten rows of 400,000 equals 4,900,000 |
| Invoice | Correct customer, Item, dimensions and payment schedule; submitted voucher |
| Down payment | 900,000 Collection Entry creates a posted Payment Entry; invoice outstanding becomes 4,000,000 |
| Partial installment | Receipt of 100,000 against row 1 leaves 300,000 outstanding and Partial status |
| Full installment | Further 300,000 receipt makes row 1 Paid and invoice outstanding 3,600,000 |
| Construction | BOQ through PO, measurement, bill and invoice links verified; retention reviewed separately |
| Handover | Reject with open snag or outstanding installment; allow after complete clearance and acceptance |
| After sales | Warranty dates validated; maintenance area/rate calculation confirmed |

## Test rejection and access cases

Attempt a duplicate active booking, an incorrect schedule total, an over-allocation and an over-measurement. Confirm each is rejected. Test cancellation dependencies and verify both invoice and schedule balances after a collection correction. Test a normal User's submission rights and a Manager's correction rights with native ERPNext permissions included.

## Release checklist

Confirm opening balances are reconciled; staff are trained; backups and restore procedures are established; the daily scheduler runs; required approvals and print terms are configured; report owners understand the limits in this manual; and outstanding acceptance issues have named owners. Record the deployed revision and sign-off before opening live entry.

# 23 Field and status quick reference

| Field or record | Meaning |
| Generated Code or No | System record identifier; descriptive names and Unit No are business labels |
| ERPNext Project | Native project dimension used for accounting and cost reporting |
| Cost Center | Company accounting dimension carried into generated voucher rows |
| Net Contract Value | Contract Value less Discount |
| Booking Money and Down Payment | Agreed initial amount; receipt must be recorded separately |
| Total Scheduled | Sum of installment principal and other charges; excludes down payment |
| Outstanding on installment | Row total less allocated paid amount, with a lower bound of zero |
| Unallocated Amount | Collection amount less allocation total; must be effectively zero to save |
| Retention Amount | Gross bill amount multiplied by retention percentage |
| Monthly Amount | Unit area multiplied by monthly maintenance rate |

## Submission and business state

Draft records remain editable under the user's permissions. Submitted records have passed their submission logic; use the permitted correction flow for later changes. Cancelled records are no longer active submissions. Business statuses and accounting statuses can describe a different aspect of the same record.

Unit booking submission produces Booked; booking cancellation produces Available. Handover submission produces Handed Over; handover cancellation produces Handover Pending. The app does not automatically traverse every selectable unit state.

Installment status priority is Paid, then Partial, then the due-date states. An overdue installment with a partial receipt can therefore remain Partial. Use due dates and aging amounts when planning follow-up.

Saved-only records are Land Owner, Sales Target, Snag and Service Request. Child tables include Installment Schedule, Payment Allocation, BOQ Item, Project Budget Item, Work Order Item, Measurement Item and Running Bill Item; enter these through the parent form.

# 24 Screenshot register and maintenance notes

Use sample data and retain each SS identifier when adding images. A caption may cover two related images. Keep screenshots readable at page width and avoid stretching them. Insert images inline immediately before their captions; add a page when needed rather than compressing the procedure text.

| IDs | Screens to capture |
| SS01–SS03 | Workspace, user roles and submitted form controls |
| SS04–SS06 | Project mappings, hierarchy and unit details |
| SS07–SS09 | Booking, agreement preview and installment schedule |
| SS10–SS12 | Invoice, collection/payment and ledger/reconciliation |
| SS13–SS15 | BOQ, budget and contractor/work order |
| SS16–SS18 | Measurement, running bill and material transactions |
| SS19–SS20 | Land parcel, JV shares and allocation result |
| SS21–SS24 | Handover, snags, warranty, service and maintenance |
| SS25–SS27 | Targets, commission, aging and management reports |

## Source and verification record

Prepared from the local Reckon Real Estate repository on 5 September 2026: README.md; installation scripts; setup/install.py; hooks.py; form JSON, JavaScript and Python controllers; accounting event handlers; report implementations; and the release 2, 3 and 4 architecture notes in docs. Where overview prose and current controller behavior differ, this manual follows the controller behavior.

The manual documents current module behavior rather than promising the broader roadmap in the README. Dedicated transfer/resale wizards, automatic customer reminder delivery, automatic recurring maintenance invoices and automatic retention postings are not established by the reviewed implementation. Configure separate processes where those capabilities are needed.

After each app upgrade, recheck UI labels, roles, generated voucher behavior, cancellation rules and report calculations. Update the manual revision date, repeat the acceptance checks and replace affected screenshots. Keep the previous manual with the corresponding deployed app revision for reference.
