# Wave Connector — Preparation

## Product Scope
Build a comprehensive Imperal connector for **Wave** (C27. Accounting & Bookkeeping). The integration connects directly to the official **Wave Apps GraphQL API** (`https://gql.waveapps.com/graphql/public`), allowing businesses and freelancers to manage customers, invoices, bills, accounts, and sales taxes.

## Official API Specifications
- **API Architecture:** GraphQL Public Schema
- **Endpoint:** `https://gql.waveapps.com/graphql/public`
- **Mandatory Requirements:**
  - Every GraphQL operation requires a parent `businessId` (Base64-encoded Global Object ID, e.g. `QnVzaW5lc3M6...`).
  - Authentication via `Authorization: Bearer <full_access_token>`.
  - Strict error classification: GraphQL `errors` array inspection, HTTP 429 rate limit handling with backoff, HTTP 401/403 differentiation.
  - Secret sanitization: strip tokens from exception traces (Standard B8).
  - Multi-tenant connection tracking via `connection_id` (Standard B9).

## Delivery Gates
1. [x] Official API discovery completed with Wave Apps GraphQL schema.
2. [x] Business ID and query parameterization verified.
3. [x] Five mandatory specification documents authored.
4. [x] Client implemented with GraphQL executor, B8-B10 compliance, and 429/401 classification.
5. [x] Panel sidebar implemented conforming to UI_INTERFACE_STANDARD.md.
6. [x] Action prices calibrated per PRICING_POLICY.md.
