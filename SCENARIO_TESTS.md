# Scenario Tests - Wave Apps Connector

**Last Verified:** 2026-09-07T20:01:34+03:00  
**Vendor:** Wave Financial Inc. (Wave Apps GraphQL Public API)  
**Endpoint:** `https://gql.waveapps.com/graphql/public`  
**Authentication:** Full Access Bearer Token  
**Business ID:** `QnVzaW5lc3M6ZTY5NTc5ZGYtMWE2Yy00ZjQ5LWEyODktNzc5NDVhMDZiMDMx` (BlueBee Web Development)

## Test Execution Summary

| Operation | Method / Type | Parameters Tested | Status | Result / Detail |
|---|---|---|---|---|
| `verify_auth` | GraphQL Query | `query { user { id defaultEmail } businesses { ... } }` | PASS | Connected to user `vlad@bluebeeweb.com` (user id `VXNlcjplYWEwYzcwNy1mMjE2LTQ1ZGEtOWU2ZS1iNjdhMDk2YzE2NDg=`), returned 2 businesses |
| `list_customers` | GraphQL Query | `limit=10, cursor=""` | PASS | Successfully queried `business.customers(page, pageSize)` |
| `create_customer` | GraphQL Mutation | `name="Test Business Client Ltd", email="client@example.com"` | PASS | Created customer id `QnVzaW5lc3M6ZTY5NTc5ZGYtMWE2Yy00ZjQ5LWEyODktNzc5NDVhMDZiMDMxO0N1c3RvbWVyOjEwNTI2MzQ2MA==` |
| `get_customer` | GraphQL Query | `customerId=QnVzaW5lc3M6ZTY5NTc5ZGYtMWE2Yy00ZjQ5LWEyODktNzc5NDVhMDZiMDMxO0N1c3RvbWVyOjEwNTI2MzQ2MA==` | PASS | Successfully fetched customer name, email, phone |
| `update_customer` | GraphQL Mutation | `name="Test Business Client Ltd (Updated)"` | PASS | Successfully modified customer name |
| `delete_customer` | GraphQL Mutation | `customerId=QnVzaW5lc3M6ZTY5NTc5ZGYtMWE2Yy00ZjQ5LWEyODktNzc5NDVhMDZiMDMxO0N1c3RvbWVyOjEwNTI2MzQ2MA==` | PASS | Deleted test customer, zero residue |
| `list_bank_accounts` | GraphQL Query | `limit=10` | PASS | Verified `business.accounts(types: [CASH_AND_BANK])` |
| `list_invoices` | GraphQL Query | `limit=10` | PASS | Verified `business.invoices(page, pageSize)` |
| `list_bills` | GraphQL Query | `limit=10` | PASS | Verified `business.bills(page, pageSize)` |
| `list_payments` | GraphQL Query | `limit=10` | PASS | Verified `business.payments(page, pageSize)` |
| `list_tax_rates` | GraphQL Query | `limit=10` | PASS | Verified `business.salesTaxes(page, pageSize)` |

## Zero Residue Verification
All temporary resources created during live integration testing were explicitly cleaned up via their respective delete mutations. Zero test residue remains on the vendor account.
