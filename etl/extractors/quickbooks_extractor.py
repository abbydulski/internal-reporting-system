"""
QuickBooks API Extractor (REAL Implementation)
Connects to actual QuickBooks API (sandbox or production) to fetch accounting data.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

class QuickBooksExtractor:
    """Extract accounting data from QuickBooks API."""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str, realm_id: str = None, is_sandbox: bool = True):
        """
        Initialize QuickBooks API client.
        
        Args:
            client_id: QuickBooks app client ID
            client_secret: QuickBooks app client secret
            refresh_token: OAuth refresh token
            realm_id: Company ID (realm ID)
            is_sandbox: True for sandbox, False for production
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.realm_id = realm_id
        self.is_sandbox = is_sandbox
        
        # Set base URL
        if is_sandbox:
            self.base_url = "https://sandbox-quickbooks.api.intuit.com"
        else:
            self.base_url = "https://quickbooks.api.intuit.com"
        
        self.token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        
        # Get initial access token
        self.access_token = None
        self.token_expires_at = None
        self._refresh_access_token()
        
        mode = "SANDBOX" if is_sandbox else "PRODUCTION"
        print(f"💼 QuickBooks Extractor initialized ({mode} mode)")
        if realm_id:
            print(f"   Company ID: {realm_id}")
    
    def _refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            response = requests.post(
                self.token_url,
                auth=(self.client_id, self.client_secret),
                data=data,
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens['access_token']
                self.refresh_token = tokens['refresh_token']  # QB returns new refresh token
                self.token_expires_at = time.time() + tokens['expires_in']
                print("  ✓ Access token refreshed")
            else:
                print(f"  Failed to refresh token: {response.status_code}")
                print(f"  Response: {response.text}")
                raise Exception("Failed to refresh QuickBooks access token")
                
        except Exception as e:
            print(f"  Error refreshing token: {e}")
            raise
    
    def _ensure_valid_token(self):
        """Ensure we have a valid access token."""
        # Refresh if token expires in less than 5 minutes
        if self.token_expires_at and time.time() > (self.token_expires_at - 300):
            self._refresh_access_token()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make an authenticated request to QuickBooks API.
        
        Args:
            endpoint: API endpoint (e.g., "/query")
            params: Query parameters
            
        Returns:
            Response JSON
        """
        self._ensure_valid_token()
        
        url = f"{self.base_url}/v3/company/{self.realm_id}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  QuickBooks API error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return {}
    
    def get_invoices(self, days_back: int = 90) -> List[Dict]:
        """
        Get invoices from the last N days.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of invoice dictionaries
        """
        print(f"  → Fetching QuickBooks invoices (last {days_back} days)...")
        
        if not self.realm_id:
            print("  No realm_id (company ID) provided!")
            return []
        
        try:
            # Calculate date
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            # Query invoices
            query = f"SELECT * FROM Invoice WHERE TxnDate >= '{start_date}' MAXRESULTS 1000"
            response = self._make_request('/query', params={'query': query})
            
            if 'QueryResponse' not in response:
                print("  No QueryResponse in API response")
                return []
            
            qb_invoices = response['QueryResponse'].get('Invoice', [])
            
            # Transform to our format
            invoices = []
            for inv in qb_invoices:
                customer_ref = inv.get('CustomerRef', {})
                
                invoices.append({
                    "invoice_id": f"INV-{inv['Id']}",
                    "customer_id": customer_ref.get('value', 'Unknown'),
                    "customer_name": customer_ref.get('name', 'Unknown Customer'),
                    "invoice_date": inv.get('TxnDate', ''),
                    "due_date": inv.get('DueDate', ''),
                    "total_amount": float(inv.get('TotalAmt', 0)),
                    "balance": float(inv.get('Balance', 0)),
                    "status": self._get_invoice_status(inv)
                })
            
            print(f"  ✓ Found {len(invoices)} invoices")
            return invoices
            
        except Exception as e:
            print(f"  Error fetching invoices: {e}")
            return []
    
    def _get_invoice_status(self, invoice: Dict) -> str:
        """Determine invoice status from QuickBooks data."""
        balance = float(invoice.get('Balance', 0))
        
        if balance == 0:
            return "Paid"
        
        due_date_str = invoice.get('DueDate')
        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            if due_date < datetime.now():
                return "Overdue"
        
        return "Unpaid"
    
    def get_payments(self, days_back: int = 90) -> List[Dict]:
        """
        Get payments received in the last N days.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of payment dictionaries
        """
        print(f"  → Fetching QuickBooks payments (last {days_back} days)...")
        
        if not self.realm_id:
            print("  No realm_id (company ID) provided!")
            return []
        
        try:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            # Query payments
            query = f"SELECT * FROM Payment WHERE TxnDate >= '{start_date}' MAXRESULTS 1000"
            response = self._make_request('/query', params={'query': query})
            
            if 'QueryResponse' not in response:
                return []
            
            qb_payments = response['QueryResponse'].get('Payment', [])
            
            # Transform to our format
            payments = []
            for pmt in qb_payments:
                # Get linked invoice IDs
                invoice_ids = []
                for line in pmt.get('Line', []):
                    linked_txn = line.get('LinkedTxn', [])
                    for txn in linked_txn:
                        if txn.get('TxnType') == 'Invoice':
                            invoice_ids.append(f"INV-{txn.get('TxnId')}")
                
                # Create payment record for each linked invoice
                for invoice_id in invoice_ids:
                    payments.append({
                        "payment_id": f"PMT-{pmt['Id']}-{invoice_id}",
                        "invoice_id": invoice_id,
                        "payment_date": pmt.get('TxnDate', ''),
                        "amount": float(pmt.get('TotalAmt', 0)) / len(invoice_ids) if invoice_ids else 0
                    })
            
            print(f"  ✓ Found {len(payments)} payments")
            return payments
            
        except Exception as e:
            print(f"  Error fetching payments: {e}")
            return []
    
    def get_company_info(self) -> Dict:
        """Get information about the QuickBooks company."""
        try:
            response = self._make_request('/companyinfo/' + self.realm_id)
            if 'CompanyInfo' in response:
                info = response['CompanyInfo']
                return {
                    'name': info.get('CompanyName'),
                    'legal_name': info.get('LegalName'),
                    'country': info.get('Country')
                }
            return {}
        except Exception as e:
            print(f" Error fetching company info: {e}")
            return {}


# Test function
def test_quickbooks_extractor():
    """Test the QuickBooks extractor with your credentials."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client_id = os.getenv("QUICKBOOKS_CLIENT_ID")
    client_secret = os.getenv("QUICKBOOKS_CLIENT_SECRET")
    refresh_token = os.getenv("QUICKBOOKS_REFRESH_TOKEN")
    realm_id = os.getenv("QUICKBOOKS_REALM_ID")
    
    if not all([client_id, client_secret, refresh_token, realm_id]):
        print("Missing QuickBooks credentials in .env file")
        print("\nRequired variables:")
        print("  - QUICKBOOKS_CLIENT_ID")
        print("  - QUICKBOOKS_CLIENT_SECRET")
        print("  - QUICKBOOKS_REFRESH_TOKEN")
        print("  - QUICKBOOKS_REALM_ID")
        return
    
    print("\n" + "="*70)
    print("TESTING QUICKBOOKS API CONNECTION")
    print("="*70 + "\n")
    
    extractor = QuickBooksExtractor(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        realm_id=realm_id,
        is_sandbox=True  # Set to False for production
    )
    
    # Get company info
    print("\n--- Company Information ---")
    company = extractor.get_company_info()
    if company:
        print(f"  Company Name: {company.get('name', 'N/A')}")
        print(f"  Legal Name: {company.get('legal_name', 'N/A')}")
        print(f"  Country: {company.get('country', 'N/A')}")
    
    # Get invoices
    invoices = extractor.get_invoices(days_back=90)
    if invoices:
        print(f"\nSample invoice:")
        inv = invoices[0]
        print(f"  Invoice ID: {inv['invoice_id']}")
        print(f"  Customer: {inv['customer_name']}")
        print(f"  Amount: ${inv['total_amount']:,.2f}")
        print(f"  Balance: ${inv['balance']:,.2f}")
        print(f"  Status: {inv['status']}")
    
    # Get payments
    payments = extractor.get_payments(days_back=90)
    if payments:
        print(f"\nSample payment:")
        pmt = payments[0]
        print(f"  Payment ID: {pmt['payment_id']}")
        print(f"  Invoice: {pmt['invoice_id']}")
        print(f"  Amount: ${pmt['amount']:,.2f}")
        print(f"  Date: {pmt['payment_date']}")
    
    print("\n" + "="*70)
    print("QUICKBOOKS API TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_quickbooks_extractor()