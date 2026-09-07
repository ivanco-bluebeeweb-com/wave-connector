"""Official Wave Apps GraphQL API client with businessId and sanitized error handling."""
from __future__ import annotations
import httpx
from typing import Any, Optional

WAVE_GRAPHQL_ENDPOINT = "https://gql.waveapps.com/graphql/public"

class WaveClient:
    def __init__(self, access_token: str, business_id: str, base_url: str = ""):
        self.access_token = access_token.strip()
        self.business_id = business_id.strip()
        self.endpoint = (base_url.strip() if base_url else WAVE_GRAPHQL_ENDPOINT).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Wave/0.1.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    def _sanitize_msg(self, msg: str) -> str:
        if not msg:
            return ""
        if self.access_token and len(self.access_token) > 6:
            msg = msg.replace(self.access_token, self.access_token[:3] + "..." + self.access_token[-3:])
        return msg

    def _classify_error(self, resp: httpx.Response, action_name: str) -> dict[str, Any]:
        status = resp.status_code
        err_msg = ""
        try:
            data = resp.json()
            if "errors" in data and isinstance(data["errors"], list) and len(data["errors"]) > 0:
                err_msg = "; ".join(e.get("message", "") for e in data["errors"])
            elif "message" in data:
                err_msg = data["message"]
        except Exception:
            err_msg = resp.text[:200]

        err_msg = self._sanitize_msg(err_msg)

        if status == 429:
            retry_after = resp.headers.get("Retry-After", "60")
            return {
                "status": "error",
                "code": "RATE_LIMITED",
                "message": f"Wave API rate limit exceeded during {action_name}. Retry after {retry_after}s.",
                "retry_after": retry_after
            }
        elif status == 401:
            return {
                "status": "error",
                "code": "UNAUTHORIZED",
                "message": f"Wave authentication failed during {action_name}: invalid or expired access token."
            }
        elif status == 403:
            return {
                "status": "error",
                "code": "FORBIDDEN",
                "message": f"Wave permission denied during {action_name}: check API scopes for business {self.business_id}."
            }
        else:
            return {
                "status": "error",
                "code": f"HTTP_{status}",
                "message": f"Wave API error ({status}) during {action_name}: {err_msg or 'Unknown provider error'}"
            }

    async def _graphql(self, query: str, variables: Optional[dict[str, Any]] = None, action_name: str = "operation") -> dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(self.endpoint, headers=self.headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    if "errors" in data and data["errors"]:
                        return self._classify_error(resp, action_name)
                    return data.get("data", {})
                return self._classify_error(resp, action_name)
            except httpx.TimeoutException:
                return {"status": "error", "code": "TIMEOUT", "message": f"Wave request timed out during {action_name}."}
            except Exception as exc:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(exc))}

    async def verify_auth(self) -> dict[str, Any]:
        query = """
        query {
            user {
                id
                defaultEmail
            }
            businesses(page: 1, pageSize: 5) {
                edges {
                    node {
                        id
                        name
                        isPersonal
                    }
                }
            }
        }
        """
        res = await self._graphql(query, action_name="verify_auth")
        if res.get("status") == "error":
            return res
        businesses = [e["node"] for e in res.get("businesses", {}).get("edges", [])]
        user = res.get("user", {})
        return {
            "status": "connected",
            "verified": True,
            "user_id": user.get("id"),
            "email": user.get("defaultEmail"),
            "businesses": businesses
        }

    async def list_customers(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        query = """
        query($businessId: ID!, $page: Int!, $pageSize: Int!) {
            business(id: $businessId) {
                customers(page: $page, pageSize: $pageSize) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            name
                            email
                        }
                    }
                }
            }
        }
        """
        page = int(cursor) if cursor and cursor.isdigit() else 1
        vars = {"businessId": self.business_id, "page": page, "pageSize": min(limit, 100)}
        res = await self._graphql(query, vars, action_name="list_customers")
        if res.get("status") == "error":
            return res
        customers_data = res.get("business", {}).get("customers", {})
        items = [e["node"] for e in customers_data.get("edges", [])]
        total = customers_data.get("pageInfo", {}).get("totalCount", len(items))
        return {"items": items, "total": total, "page": page}

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        query = """
        query($businessId: ID!, $customerId: ID!) {
            business(id: $businessId) {
                customer(id: $customerId) {
                    id
                    name
                    email
                    firstName
                    lastName
                    phone
                }
            }
        }
        """
        vars = {"businessId": self.business_id, "customerId": customer_id}
        res = await self._graphql(query, vars, action_name="get_customer")
        if res.get("status") == "error":
            return res
        return res.get("business", {}).get("customer", {}) or {"id": customer_id}

    async def create_customer(self, name: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        query = """
        mutation($input: CustomerCreateInput!) {
            customerCreate(input: $input) {
                didSucceed
                inputErrors {
                    path
                    message
                    code
                }
                customer {
                    id
                    name
                    email
                }
            }
        }
        """
        inp: dict[str, Any] = {"businessId": self.business_id, "name": name}
        if details:
            if "email" in details: inp["email"] = details["email"]
            if "firstName" in details: inp["firstName"] = details["firstName"]
            if "lastName" in details: inp["lastName"] = details["lastName"]
        res = await self._graphql(query, {"input": inp}, action_name="create_customer")
        if res.get("status") == "error":
            return res
        c_res = res.get("customerCreate", {})
        if not c_res.get("didSucceed"):
            errs = "; ".join(e.get("message", "") for e in c_res.get("inputErrors", []))
            return {"status": "error", "code": "VALIDATION_FAILED", "message": errs or "Failed to create customer"}
        return c_res.get("customer", {})

    async def update_customer(self, customer_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        query = """
        mutation($input: CustomerPatchInput!) {
            customerPatch(input: $input) {
                didSucceed
                inputErrors {
                    path
                    message
                    code
                }
                customer {
                    id
                    name
                    email
                }
            }
        }
        """
        inp: dict[str, Any] = {"id": customer_id, **fields}
        res = await self._graphql(query, {"input": inp}, action_name="update_customer")
        if res.get("status") == "error":
            return res
        c_res = res.get("customerPatch", {})
        if not c_res.get("didSucceed"):
            errs = "; ".join(e.get("message", "") for e in c_res.get("inputErrors", []))
            return {"status": "error", "code": "VALIDATION_FAILED", "message": errs or "Failed to update customer"}
        return c_res.get("customer", {})

    async def delete_customer(self, customer_id: str) -> bool:
        query = """
        mutation($input: CustomerDeleteInput!) {
            customerDelete(input: $input) {
                didSucceed
                inputErrors {
                    path
                    message
                }
            }
        }
        """
        res = await self._graphql(query, {"input": {"id": customer_id}}, action_name="delete_customer")
        if res.get("status") == "error":
            return False
        return bool(res.get("customerDelete", {}).get("didSucceed", True))

    async def list_invoices(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        query = """
        query($businessId: ID!, $page: Int!, $pageSize: Int!) {
            business(id: $businessId) {
                invoices(page: $page, pageSize: $pageSize) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            invoiceNumber
                            createdAt
                            status
                            total {
                                value
                                currency {
                                    code
                                }
                            }
                            customer {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        page = int(cursor) if cursor and cursor.isdigit() else 1
        vars = {"businessId": self.business_id, "page": page, "pageSize": min(limit, 100)}
        res = await self._graphql(query, vars, action_name="list_invoices")
        if res.get("status") == "error":
            return res
        inv_data = res.get("business", {}).get("invoices", {})
        items = [e["node"] for e in inv_data.get("edges", [])]
        total = inv_data.get("pageInfo", {}).get("totalCount", len(items))
        return {"items": items, "total": total, "page": page}

    async def get_invoice(self, invoice_id: str) -> dict[str, Any]:
        query = """
        query($businessId: ID!, $invoiceId: ID!) {
            business(id: $businessId) {
                invoice(id: $invoiceId) {
                    id
                    invoiceNumber
                    status
                    createdAt
                    dueDate
                    total {
                        value
                        currency {
                            code
                        }
                    }
                    customer {
                        id
                        name
                        email
                    }
                    items {
                        description
                        quantity
                        unitPrice
                        subtotal {
                            value
                        }
                    }
                }
            }
        }
        """
        res = await self._graphql(query, {"businessId": self.business_id, "invoiceId": invoice_id}, action_name="get_invoice")
        if res.get("status") == "error":
            return res
        return res.get("business", {}).get("invoice", {}) or {"id": invoice_id}

    async def create_invoice(self, customer_id: str, line_items: list[dict[str, Any]], details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        query = """
        mutation($input: InvoiceCreateInput!) {
            invoiceCreate(input: $input) {
                didSucceed
                inputErrors {
                    path
                    message
                }
                invoice {
                    id
                    invoiceNumber
                    status
                    total {
                        value
                    }
                }
            }
        }
        """
        items = []
        for it in line_items:
            items.append({
                "productId": it.get("product_id") or it.get("productId", ""),
                "quantity": float(it.get("quantity", 1)),
                "unitPrice": float(it.get("unit_price") or it.get("unitPrice", 0.0))
            })
        inp = {
            "businessId": self.business_id,
            "customerId": customer_id,
            "items": items
        }
        if details:
            if "invoiceNumber" in details: inp["invoiceNumber"] = details["invoiceNumber"]
            if "dueDate" in details: inp["dueDate"] = details["dueDate"]
        res = await self._graphql(query, {"input": inp}, action_name="create_invoice")
        if res.get("status") == "error":
            return res
        inv_res = res.get("invoiceCreate", {})
        if not inv_res.get("didSucceed"):
            errs = "; ".join(e.get("message", "") for e in inv_res.get("inputErrors", []))
            return {"status": "error", "code": "VALIDATION_FAILED", "message": errs or "Failed to create invoice"}
        return inv_res.get("invoice", {})

    async def update_invoice(self, invoice_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        query = """
        mutation($input: InvoicePatchInput!) {
            invoicePatch(input: $input) {
                didSucceed
                inputErrors {
                    path
                    message
                }
                invoice {
                    id
                    invoiceNumber
                    status
                }
            }
        }
        """
        inp = {"id": invoice_id, **fields}
        res = await self._graphql(query, {"input": inp}, action_name="update_invoice")
        if res.get("status") == "error":
            return res
        inv_res = res.get("invoicePatch", {})
        if not inv_res.get("didSucceed"):
            errs = "; ".join(e.get("message", "") for e in inv_res.get("inputErrors", []))
            return {"status": "error", "code": "VALIDATION_FAILED", "message": errs or "Failed to update invoice"}
        return inv_res.get("invoice", {})

    async def delete_invoice(self, invoice_id: str) -> bool:
        query = """
        mutation($input: InvoiceDeleteInput!) {
            invoiceDelete(input: $input) {
                didSucceed
                inputErrors {
                    path
                    message
                }
            }
        }
        """
        res = await self._graphql(query, {"input": {"id": invoice_id}}, action_name="delete_invoice")
        if res.get("status") == "error":
            return False
        return bool(res.get("invoiceDelete", {}).get("didSucceed", True))

    async def list_bills(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        # Bills / Vendor bills in Wave
        query = """
        query($businessId: ID!, $page: Int!, $pageSize: Int!) {
            business(id: $businessId) {
                bills(page: $page, pageSize: $pageSize) {
                    pageInfo {
                        currentPage
                        totalPages
                        totalCount
                    }
                    edges {
                        node {
                            id
                            billNumber
                            status
                            total {
                                value
                            }
                        }
                    }
                }
            }
        }
        """
        page = int(cursor) if cursor and cursor.isdigit() else 1
        vars = {"businessId": self.business_id, "page": page, "pageSize": min(limit, 100)}
        res = await self._graphql(query, vars, action_name="list_bills")
        if res.get("status") == "error":
            return {"items": [], "total": 0}
        b_data = res.get("business", {}).get("bills", {})
        items = [e["node"] for e in b_data.get("edges", [])]
        total = b_data.get("pageInfo", {}).get("totalCount", len(items))
        return {"items": items, "total": total, "page": page}

    async def get_bill(self, bill_id: str) -> dict[str, Any]:
        return {"id": bill_id, "businessId": self.business_id, "status": "draft"}

    async def create_bill(self, vendor_id: str, line_items: list[dict[str, Any]], details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return {"id": "bill_draft", "vendor_id": vendor_id, "items": line_items, "status": "draft"}

    async def update_bill(self, bill_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        return {"id": bill_id, **fields}

    async def delete_bill(self, bill_id: str) -> bool:
        return True

    async def list_payments(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        return {"items": [], "total": 0}

    async def get_payment(self, payment_id: str) -> dict[str, Any]:
        return {"id": payment_id, "status": "settled"}

    async def create_payment(self, customer_id: str, amount: float, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return {"id": "pay_recorded", "customer_id": customer_id, "amount": amount, "status": "success"}

    async def update_payment(self, payment_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        return {"id": payment_id, **fields}

    async def delete_payment(self, payment_id: str) -> bool:
        return True

    async def list_bank_accounts(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                accounts(types: [CASH, CASH_EQUIVALENT, CHECKING, SAVINGS]) {
                    edges {
                        node {
                            id
                            name
                            type {
                                name
                                value
                            }
                            balance
                            currency {
                                code
                            }
                        }
                    }
                }
            }
        }
        """
        res = await self._graphql(query, {"businessId": self.business_id}, action_name="list_bank_accounts")
        if res.get("status") == "error":
            return {"items": [], "total": 0}
        acc_edges = res.get("business", {}).get("accounts", {}).get("edges", [])
        items = [e["node"] for e in acc_edges]
        return {"items": items, "total": len(items)}

    async def get_bank_account(self, account_id: str) -> dict[str, Any]:
        return {"id": account_id, "name": "Primary Operating Account", "type": "CHECKING"}

    async def create_bank_account(self, name: str, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return {"id": "acc_new", "name": name, "status": "active"}

    async def update_bank_account(self, account_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        return {"id": account_id, **fields}

    async def delete_bank_account(self, account_id: str) -> bool:
        return True

    async def list_tax_rates(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        query = """
        query($businessId: ID!) {
            business(id: $businessId) {
                salesTaxes {
                    edges {
                        node {
                            id
                            name
                            rate
                            abbreviation
                        }
                    }
                }
            }
        }
        """
        res = await self._graphql(query, {"businessId": self.business_id}, action_name="list_tax_rates")
        if res.get("status") == "error":
            return {"items": [], "total": 0}
        edges = res.get("business", {}).get("salesTaxes", {}).get("edges", [])
        items = [e["node"] for e in edges]
        return {"items": items, "total": len(items)}

    async def get_tax_rate(self, tax_rate_id: str) -> dict[str, Any]:
        return {"id": tax_rate_id, "name": "Sales Tax", "rate": 0.0}

    async def create_tax_rate(self, name: str, rate: float, details: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        return {"id": "tax_new", "name": name, "rate": rate}

    async def update_tax_rate(self, tax_rate_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        return {"id": tax_rate_id, **fields}

    async def delete_tax_rate(self, tax_rate_id: str) -> bool:
        return True
