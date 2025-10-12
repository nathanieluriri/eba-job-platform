import requests
from typing import Dict, Any

BASE_URL = "https://quickbooks.api.intuit.com/v3/company"
ACCESS_TOKEN = "<YOUR_ACCESS_TOKEN>"  # replace dynamically from OAuth flow


def headers():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


# ✅ Create an invoice (allows payments)
def create_invoice(company_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice"
    response = requests.post(url, json=data, headers=headers())
    response.raise_for_status()
    return response.json()


# ✅ Send invoice (email)
def send_invoice(company_id: str, invoice_id: str, email: str = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice/{invoice_id}/send"
    if email:
        url += f"?sendTo={email}"
    response = requests.post(url, headers=headers())
    response.raise_for_status()
    return response.json()


# ✅ Get a specific invoice (with optional payment link)
def get_invoice(company_id: str, invoice_id: str, include_link: bool = False) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice/{invoice_id}"
    if include_link:
        url += "?include=invoiceLink"
    response = requests.get(url, headers=headers())
    response.raise_for_status()
    return response.json()


# ✅ Query invoices using SQL-like syntax
def query_invoices(company_id: str, query: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/query"
    params = {"query": query}
    response = requests.get(url, headers=headers(), params=params)
    response.raise_for_status()
    return response.json()


# ✅ Sparse update (e.g., update balance, customer ref, etc.)
def update_invoice(company_id: str, invoice_id: str, sync_token: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice?operation=update"
    payload = {
        "Id": invoice_id,
        "SyncToken": sync_token,
        **updates
    }
    response = requests.post(url, json=payload, headers=headers())
    response.raise_for_status()
    return response.json()


# ✅ Delete an invoice
def delete_invoice(company_id: str, invoice_id: str, sync_token: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice?operation=delete"
    payload = {"Id": invoice_id, "SyncToken": sync_token}
    response = requests.post(url, json=payload, headers=headers())
    response.raise_for_status()
    return response.json()


# ✅ Void an invoice
def void_invoice(company_id: str, invoice_id: str, sync_token: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice?operation=void"
    payload = {"Id": invoice_id, "SyncToken": sync_token}
    response = requests.post(url, json=payload, headers=headers())
    response.raise_for_status()
    return response.json()


# ✅ Download invoice as PDF
def get_invoice_pdf(company_id: str, invoice_id: str) -> bytes:
    url = f"{BASE_URL}/{company_id}/invoice/{invoice_id}/pdf"
    response = requests.get(url, headers={
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/pdf"
    })
    response.raise_for_status()
    return response.content
