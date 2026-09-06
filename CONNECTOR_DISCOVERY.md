# Wave Connector — Connector Discovery

## Official API Landscape
Wave Apps uses a unified GraphQL API serving small businesses and freelancers:
- **Root Query:** `business(id: ID!)` resolves all child collections.
- **Customers:** `business.customers(page: Int, pageSize: Int)` with mutations `customerCreate`, `customerPatch`.
- **Invoices:** `business.invoices(page: Int, pageSize: Int)` with mutations `invoiceCreate`, `invoiceSend`.
- **Bills / Accounts Payable:** `business.bills` and money-out records.
- **Accounts:** `business.accounts` (checking, savings, credit cards).
- **Sales Taxes:** `business.salesTaxes` (rates, abbreviations).

## Authentication & Multi-Tenancy
- Token Type: Wave Full Access Token or OAuth2 bearer token.
- Tenancy Scoping: Each Wave account can contain multiple businesses; the connector stores `business_id` alongside the token.
