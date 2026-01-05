import json
import requests
import base64
from typing import Dict, Any, Optional
import sys
import secrets
import urllib.parse

# =========================================================================
# ⚙️ 1. CONFIGURATION SECTION
# =========================================================================

BASE_URL = "https://sandbox-quickbooks.api.intuit.com/v3/company"

CLIENT_ID = "ABRkOKoorArUi9XHHrbx0JfodEfzw85YfK0mx2rMu1P23qnWtN"
CLIENT_SECRET = "zMBmVt5gzUFY8HvrHretFsARjD35iJN0xTvGDuk1"

REDIRECT_URI = "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"

COMPANY_ID = "9341455502376004"

# ⚠️ Replace this with your valid OAuth token for testing
ACCESS_TOKEN = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwieC5vcmciOiJIMCJ9..AbYA9A4iJxH41i71Ett5Ow.pxNi7LCTrUg_6BHaa2RbvY4NtcqP78fD0mzWK7Of-megP-GkydRYydZtlt7wh_iS-jx90YquqnPTEq4dbg13HlV6-0kfbVLypkQlyRhEICIroLWZGtRvSFRNgb9yjTFScFkDQYOBwFvRUaS6I8-X50EP2OIh99fm0dhgGjrPXHYwFwqzRSjdRadccD8DcbfklmoMpvBydMIaaSZ2m5UhBOIbXqeNGVk7miuIw1vCFAgT7mbrPYImC_PwotkKsSeFvzfzYOgJQwYmeZLGzArG5eKm2FDiiL5MEAtqvQi3sxewXapdrgTTuAQHbGNbrtoWmKzYvzOuilL_ZDvMIBZ7wAi2Z1DNucA7MroMLQeEmjvnFza8BCxwUiteOY8pxoUQAtOh21RB8PGh7MhUL_Z-qU8urq7K33ui6fMkxrmj_iZBKTSbNHgI64Peoi1M-FvDSo8v_h7kyTSAOOjfkjwVTMu2dsWjl1QMNdakTdXczFFKgSaAS_DC-oYprY0Y1QCVcBBfBwgkxMddCSTnLk_4ajQzolc-ve8eBDsLQHuNstzg6i3lNWTh3gdRnpVzReGiwjG-7GTAaFmF6FA2YvXz9pEB-HyIgn-DKzCoT7TqVFSQcwdBI-Dsbg6AjHr7ZoB3.aq9ftcucsD2cLj-oSlbXTg"
REFRESH_TOKEN = "RT1-99-H0-1769039844n04ypfwgiqi7qvksbxi6"  # Needed for refresh flow

# ✅ Example usage:
CUSTOMER_DATA = {
    "FullyQualifiedName": "King Groceries",
    "PrimaryEmailAddr": {
        "Address": "uririnathaniel+11@gmail.com"
    },
    "DisplayName": "King's Groceries",
    "Suffix": "Jr",
    "Title": "Mr",
    "MiddleName": "B",
    "Notes": "Here are other details.",
    "FamilyName": "King",
    "PrimaryPhone": {
        "FreeFormNumber": "(555) 555-5555"
    },
    "CompanyName": "King Groceries",
    "BillAddr": {
        "CountrySubDivisionCode": "CA",
        "City": "Mountain View",
        "PostalCode": "94042",
        "Line1": "123 Main Street",
        "Country": "USA"
    },
    "GivenName": "Nathaniel"
}

# =========================================================================
# 🔐 2. GLOBAL STATE MANAGEMENT
# =========================================================================

def set_access_token(token: str):
    global ACCESS_TOKEN
    ACCESS_TOKEN = token


def headers(content_type: str = "application/json") -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": content_type
    }

# =========================================================================
# 🔑 3. AUTHENTICATION FUNCTIONS
# =========================================================================

def get_authorization_url(scope: str = "com.intuit.quickbooks.accounting") -> str:
    """
    Generates the OAuth2 authorization URL with required parameters.
    """
    base_auth_url = "https://appcenter.intuit.com/connect/oauth2"

    # Generate a random secure state value
    state = secrets.token_urlsafe(16)

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }

    # Encode query parameters properly
    query_string = urllib.parse.urlencode(params)
    return f"{base_auth_url}?{query_string}"


def exchange_code_for_token(auth_code: str) -> Dict[str, Any]:
    """
    Exchanges authorization code for access and refresh tokens.
    """
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }

    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    token_data = r.json()
    set_access_token(token_data["access_token"])
    return token_data


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Refreshes the QuickBooks OAuth access token.
    """
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    token_data = r.json()
    set_access_token(token_data["access_token"])
    print(token_data)
    return token_data

# =========================================================================
# 📦 4. QUICKBOOKS API FUNCTIONS
# =========================================================================
def create_customer(company_id: str, data: dict):
    """Create a new customer in QuickBooks Online."""
    url = f"{BASE_URL}/{company_id}/customer?minorversion=40"
    response = requests.post(url, headers=headers(), data=json.dumps(data))
    response.raise_for_status()
    return response.json()


def create_item(company_id: str, name: str, price: float, income_account_id: str) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/item"
    payload = {
        "Name": name,
        "Type": "Service",
        "IncomeAccountRef": {"value": income_account_id},
        "UnitPrice": price
    }
    r = requests.post(url, json=payload, headers=headers())
    r.raise_for_status()
    return r.json()


def create_invoice(company_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice"
    response = requests.post(url, json=data, headers=headers())
    response.raise_for_status()
    return response.json()


def send_invoice(company_id: str, invoice_id: str, email: Optional[str] = None) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice/{invoice_id}/send"
    if email:
        url += f"?sendTo={email}"
    response = requests.post(url, headers=headers())
    response.raise_for_status()
    return response.json()


def get_invoice(company_id: str, invoice_id: str, include_link: bool = False) -> Dict[str, Any]:
    url = f"{BASE_URL}/{company_id}/invoice/{invoice_id}"
    if include_link:
        url += "?include=invoiceLink"
    response = requests.get(url, headers=headers())
    response.raise_for_status()
    return response.json()


# =========================================================================
# 🚀 5. MAIN FLOW (DEMO)
# =========================================================================

if __name__ == "__main__":
    print("\n--- QuickBooks API Demo ---")

    # ⚠️ Show the authorization URL first if user doesn't have tokens yet
    if ACCESS_TOKEN == "<YOUR_INITIAL_ACCESS_TOKEN>":
        print("🔗 Visit this URL to authorize your app:")
        print(get_authorization_url())
        print("\nAfter authorizing, copy the 'code' parameter from the redirect URL and rerun:")
        print("   python quickbooks_demo.py <AUTH_CODE>")
        sys.exit()

    # Optional: Refresh token if expired
    # refresh_access_token(REFRESH_TOKEN)

    # 1️⃣ Create customer
    CUSTOMER_NAME = "Natty Corp (Demo1)"
    CUSTOMER_EMAIL = "uririnathaniel+11@example.com"
    print(f"\n1. Creating Customer: {CUSTOMER_NAME}...")
    try:
        customer_response = create_customer(COMPANY_ID, data=CUSTOMER_DATA)
        customer_id = customer_response["Customer"]["Id"]
        
        print(f"   ✅ Customer created with ID: {customer_id}")
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ Customer creation failed: {e.response.text}")
        sys.exit()

    # 2️⃣ Create item
    ITEM_NAME = "Onboarding Fee"
    ITEM_PRICE = 150.00
    INCOME_ACCOUNT_ID = "79"
    print(f"\n2. Creating Item: {ITEM_NAME}...")
    try:
        item_response = create_item(COMPANY_ID, ITEM_NAME, ITEM_PRICE, INCOME_ACCOUNT_ID)
        item_id = item_response["Item"]["Id"]
        
        print(f"   ✅ Item created with ID: {item_id}")
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ Item creation failed: {e.response.text}")
        sys.exit()

    # 3️⃣ Create invoice
    invoice_data = {
        "Line": [
            {
                "DetailType": "SalesItemLineDetail",
                "Amount": ITEM_PRICE,
                "SalesItemLineDetail": {
                    "ItemRef": {"name": ITEM_NAME, "value": item_id}
                }
            }
        ],
        "CustomerRef": {"value": customer_id},
        "TxnDate": "2025-10-13",
        "BillEmail": {"Address": CUSTOMER_EMAIL}, 
        "AllowOnlineCreditCardPayment": True,
        "AllowOnlineACHPayment": True,

    }

    print("\n3. Creating Invoice...")
    try:
        invoice_response = create_invoice(COMPANY_ID, invoice_data)
        invoice_id = invoice_response["Invoice"]["Id"]
        print(f"   ✅ Invoice created with ID: {invoice_id}")
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ Invoice creation failed: {e.response.text}")
        sys.exit()

    # 4️⃣ Send invoice
    print("\n4. Sending Invoice via Email...")
    invoice_info = get_invoice(COMPANY_ID, invoice_id, include_link=True)
    print(invoice_info)
    print(invoice_info["Invoice"].get("InvoiceLink"))

    try:
        send_invoice(COMPANY_ID, invoice_id, email=CUSTOMER_EMAIL)
        print("   ✅ Invoice sent successfully!")
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ Invoice send failed: {e.response.text}")

    # 5️⃣ Retrieve payment link
    print("\n5. Retrieving Payment Link...")
    try:
        invoice_info = get_invoice(COMPANY_ID, invoice_id, include_link=True)
        payment_link = invoice_info["Invoice"].get("InvoiceLink")
        if payment_link:
            print(f"   ✅ Payment Link: {payment_link}")
        else:
            print("   ⚠️ No payment link found in response.")
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ Failed to retrieve invoice: {e.response.text}")

    print("\n--- Demo Complete ✅ ---")
