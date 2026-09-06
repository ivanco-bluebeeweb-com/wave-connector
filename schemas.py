"""Pydantic schemas for Wave Connector (C27. Accounting & Bookkeeping)."""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    """Empty parameter model."""
    pass

class ConnectParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label, e.g. Acme Wave Accounting.")
    access_token: str = Field(description="Wave Apps Full Access API Token / OAuth Token.")
    business_id: str = Field(description="Wave Business ID (e.g. QnVzaW5lc3M6...) from Wave Settings > Businesses or URL.")
    base_url: str = Field(default="", description="Optional custom GraphQL endpoint (defaults to https://gql.waveapps.com/graphql/public).")

class ConnectionIdParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier (empty uses active connection).")

class ConnectionRecord(BaseModel):
    id: str
    label: str
    masked_key: str
    business_id: str
    base_url: str
    is_active: bool

class ConnectionList(BaseModel):
    connections: list[ConnectionRecord]
    total: int

class DeleteResult(BaseModel):
    id: str
    deleted: bool
    message: str

class ListCustomerParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    limit: int = Field(default=50, description="Max records to return (1-100).")
    cursor: str = Field(default="", description="Pagination cursor or page token.")

class GetCustomerParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    customer_id: str = Field(description="Unique identifier of the customer.")

class CreateCustomerParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    name: str = Field(description="Name or title of the customer.")
    details: Optional[dict[str, Any]] = Field(default=None, description="Detailed attributes and payload (email, currency, etc).")

class UpdateCustomerParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    customer_id: str = Field(description="Unique identifier of the customer.")
    fields: dict[str, Any] = Field(description="Attributes to update.")

class DeleteCustomerParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    customer_id: str = Field(description="Unique identifier of the customer.")

class CustomerRecord(BaseModel):
    id: str
    name: str
    status: str = "active"
    raw: dict[str, Any] = {}

class CustomerList(BaseModel):
    items: list[CustomerRecord]
    total: int
    next_cursor: Optional[str] = None

class ListInvoiceParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    limit: int = Field(default=50, description="Max records to return (1-100).")
    cursor: str = Field(default="", description="Pagination cursor or page token.")

class GetInvoiceParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    invoice_id: str = Field(description="Unique identifier of the invoice.")

class CreateInvoiceParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    customer_id: str = Field(description="Customer ID this invoice is billed to.")
    line_items: list[dict[str, Any]] = Field(description="Invoice line items (description, quantity, unit_price).")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional details (invoice_date, due_date, currency).")

class UpdateInvoiceParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    invoice_id: str = Field(description="Unique identifier of the invoice.")
    fields: dict[str, Any] = Field(description="Attributes to update.")

class DeleteInvoiceParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    invoice_id: str = Field(description="Unique identifier of the invoice.")

class InvoiceRecord(BaseModel):
    id: str
    customer_id: str = ""
    status: str = "draft"
    total: float = 0.0
    raw: dict[str, Any] = {}

class InvoiceList(BaseModel):
    items: list[InvoiceRecord]
    total: int
    next_cursor: Optional[str] = None

class ListBillParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    limit: int = Field(default=50, description="Max records to return (1-100).")
    cursor: str = Field(default="", description="Pagination cursor or page token.")

class GetBillParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    bill_id: str = Field(description="Unique identifier of the bill.")

class CreateBillParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    vendor_id: str = Field(description="Vendor identifier.")
    line_items: list[dict[str, Any]] = Field(description="Bill line items.")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional details.")

class UpdateBillParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    bill_id: str = Field(description="Unique identifier of the bill.")
    fields: dict[str, Any] = Field(description="Attributes to update.")

class DeleteBillParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    bill_id: str = Field(description="Unique identifier of the bill.")

class BillRecord(BaseModel):
    id: str
    vendor_id: str = ""
    status: str = "open"
    total: float = 0.0
    raw: dict[str, Any] = {}

class BillList(BaseModel):
    items: list[BillRecord]
    total: int
    next_cursor: Optional[str] = None

class ListPaymentParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    limit: int = Field(default=50, description="Max records to return (1-100).")
    cursor: str = Field(default="", description="Pagination cursor or page token.")

class GetPaymentParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    payment_id: str = Field(description="Unique identifier of the payment.")

class CreatePaymentParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    customer_id: str = Field(description="Customer or account ID.")
    amount: float = Field(description="Payment amount.")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional details.")

class UpdatePaymentParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    payment_id: str = Field(description="Unique identifier of the payment.")
    fields: dict[str, Any] = Field(description="Attributes to update.")

class DeletePaymentParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    payment_id: str = Field(description="Unique identifier of the payment.")

class PaymentRecord(BaseModel):
    id: str
    amount: float = 0.0
    status: str = "completed"
    raw: dict[str, Any] = {}

class PaymentList(BaseModel):
    items: list[PaymentRecord]
    total: int
    next_cursor: Optional[str] = None

class ListBankAccountParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    limit: int = Field(default=50, description="Max records to return (1-100).")
    cursor: str = Field(default="", description="Pagination cursor or page token.")

class GetBankAccountParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    account_id: str = Field(description="Unique identifier of the bank account.")

class CreateBankAccountParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    name: str = Field(description="Name of the bank account.")
    details: Optional[dict[str, Any]] = Field(default=None, description="Bank account details.")

class UpdateBankAccountParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    account_id: str = Field(description="Unique identifier of the bank account.")
    fields: dict[str, Any] = Field(description="Attributes to update.")

class DeleteBankAccountParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    account_id: str = Field(description="Unique identifier of the bank account.")

class BankAccountRecord(BaseModel):
    id: str
    name: str
    type: str = "checking"
    balance: float = 0.0
    raw: dict[str, Any] = {}

class BankAccountList(BaseModel):
    items: list[BankAccountRecord]
    total: int
    next_cursor: Optional[str] = None

class ListTaxRateParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    limit: int = Field(default=50, description="Max records to return (1-100).")
    cursor: str = Field(default="", description="Pagination cursor or page token.")

class GetTaxRateParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    tax_rate_id: str = Field(description="Unique identifier of the tax rate.")

class CreateTaxRateParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    name: str = Field(description="Name of the tax rate.")
    rate: float = Field(description="Tax percentage rate (e.g. 5.0).")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional tax details.")

class UpdateTaxRateParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    tax_rate_id: str = Field(description="Unique identifier of the tax rate.")
    fields: dict[str, Any] = Field(description="Attributes to update.")

class DeleteTaxRateParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier.")
    tax_rate_id: str = Field(description="Unique identifier of the tax rate.")

class TaxRateRecord(BaseModel):
    id: str
    name: str
    rate: float = 0.0
    raw: dict[str, Any] = {}

class TaxRateList(BaseModel):
    items: list[TaxRateRecord]
    total: int

class AuditAccountingHealthResult(BaseModel):
    status: str = "ok"
    total_customers: int = 0
    total_invoices: int = 0
    total_bills: int = 0
    bank_accounts_count: int = 0
    overdue_invoices_count: int = 0
    overdue_bills_count: int = 0
    summary: str = ""

class GetCashFlowSummaryResult(BaseModel):
    total_receivables: float = 0.0
    total_payables: float = 0.0
    net_cash_flow: float = 0.0
    currency: str = "USD"
    bank_accounts: list[dict[str, Any]] = []
    summary: str = ""
