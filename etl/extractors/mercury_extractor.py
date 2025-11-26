"""
Mercury API Extractor (REAL Implementation)
Connects to actual Mercury API to fetch banking data.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class MercuryExtractor:
    """Extract financial data from Mercury API."""
    
    def __init__(self, api_key: str):
        """
        Initialize Mercury API client.
        
        Args:
            api_key: Mercury API key
        """
        self.api_key = api_key
        self.base_url = "https://api.mercury.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        print("🏦 Mercury Extractor initialized (PRODUCTION MODE)")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make an authenticated request to Mercury API.
        
        Args:
            endpoint: API endpoint (e.g., "/accounts")
            params: Query parameters
            
        Returns:
            Response JSON
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  Mercury API error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return {}
                
        except Exception as e:
            print(f"  Error making request to {endpoint}: {e}")
            return {}
    
    def get_accounts(self) -> List[Dict]:
        """Get all bank accounts."""
        print("  → Fetching Mercury accounts...")
        
        try:
            response = self._make_request("/accounts")
            
            if not response or "accounts" not in response:
                print("  No accounts found in response")
                return []
            
            mercury_accounts = response["accounts"]
            
            # Transform to our format
            accounts = []
            for acc in mercury_accounts:
                accounts.append({
                    "account_id": acc.get("id", ""),
                    "name": acc.get("name", "Unknown Account"),
                    "type": acc.get("type", "checking").lower(),
                    "balance": float(acc.get("currentBalance", 0)),
                    "available_balance": float(acc.get("availableBalance", 0)),
                    "currency": "USD",
                    "status": acc.get("status", "active").lower()
                })
            
            print(f"  ✓ Found {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            print(f"  Error fetching accounts: {e}")
            return []
    
    def get_transactions(self, days_back: int = 30) -> List[Dict]:
        """
        Get recent transactions.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of transaction dictionaries
        """
        print(f"  → Fetching Mercury transactions (last {days_back} days)...")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Mercury API expects dates in ISO format
            params = {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "limit": 1000  # Adjust as needed
            }
            
            response = self._make_request("/transactions", params=params)
            
            if not response or "transactions" not in response:
                print("  No transactions found in response")
                return []
            
            mercury_transactions = response["transactions"]
            
            # Transform to our format
            transactions = []
            for txn in mercury_transactions:
                try:
                    amount = float(txn.get("amount", 0))

                    # Safely get date - handle None values
                    posted_at = txn.get("postedAt") or txn.get("createdAt") or ""
                    date_str = posted_at[:10] if posted_at else datetime.now().strftime("%Y-%m-%d")

                    # Safely get description
                    description = txn.get("note") or txn.get("counterpartyName") or "Unknown"

                    # Safely get status
                    status = (txn.get("status") or "posted").lower()

                    transactions.append({
                        "transaction_id": txn.get("id", ""),
                        "account_id": txn.get("accountId", ""),
                        "date": date_str,
                        "amount": amount,
                        "description": description,
                        "category": self._categorize_transaction(txn),
                        "status": status,
                        "type": "credit" if amount > 0 else "debit"
                    })
                except Exception as e:
                    print(f"  ⚠ Skipping transaction due to error: {e}")
                    continue

            print(f"  ✓ Found {len(transactions)} transactions")
            return sorted(transactions, key=lambda x: x["date"], reverse=True)
            
        except Exception as e:
            print(f"  Error fetching transactions: {e}")
            return []
    
    def _categorize_transaction(self, transaction: Dict) -> str:
        """
        Categorize a transaction based on available data.

        Args:
            transaction: Mercury transaction object

        Returns:
            Category string
        """
        # Mercury may provide category information
        if "category" in transaction:
            return transaction["category"]

        # Otherwise, try to infer from description/note
        note = (transaction.get("note") or "").lower()
        counterparty = (transaction.get("counterpartyName") or "").lower()
        combined = f"{note} {counterparty}"
        
        # Simple categorization logic
        if any(word in combined for word in ["payroll", "salary", "wage"]):
            return "Payroll"
        elif any(word in combined for word in ["aws", "azure", "gcp", "cloud"]):
            return "Infrastructure"
        elif any(word in combined for word in ["stripe", "payment", "invoice"]):
            return "Revenue"
        elif any(word in combined for word in ["rent", "lease"]):
            return "Rent"
        elif any(word in combined for word in ["contractor", "freelance"]):
            return "Contractors"
        elif any(word in combined for word in ["marketing", "ads", "advertising"]):
            return "Marketing"
        elif any(word in combined for word in ["software", "saas", "subscription"]):
            return "Software"
        else:
            return "Other"
    
    def get_account_balance(self, account_id: str) -> Optional[Dict]:
        """
        Get balance for a specific account.
        
        Args:
            account_id: Mercury account ID
            
        Returns:
            Account balance information
        """
        try:
            response = self._make_request(f"/account/{account_id}")
            
            if not response:
                return None
            
            return {
                "account_id": account_id,
                "balance": float(response.get("currentBalance", 0)),
                "available_balance": float(response.get("availableBalance", 0)),
                "currency": "USD"
            }
            
        except Exception as e:
            print(f"  Error fetching account balance: {e}")
            return None


# Test function
def test_mercury_extractor():
    """Test the Mercury extractor with your credentials."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("MERCURY_API_KEY")
    
    if not api_key or api_key == "mock_mercury_key" or api_key == "your_real_mercury_api_key_here":
        print("❌ Missing real Mercury API key in .env file")
        print("\nPlease set MERCURY_API_KEY in your .env file")
        print("Get your API key from: https://app.mercury.com/settings/api")
        return
    
    print("\n" + "="*70)
    print("TESTING MERCURY API CONNECTION")
    print("="*70 + "\n")
    
    extractor = MercuryExtractor(api_key=api_key)
    
    # Get accounts
    print("\n--- Accounts ---")
    accounts = extractor.get_accounts()
    if accounts:
        for acc in accounts:
            print(f"  {acc['name']}: ${acc['balance']:,.2f} ({acc['type']})")
    
    # Get transactions
    print("\n--- Recent Transactions ---")
    transactions = extractor.get_transactions(days_back=30)
    if transactions:
        print(f"\nShowing first 5 of {len(transactions)} transactions:")
        for txn in transactions[:5]:
            print(f"  {txn['date']}: {txn['description'][:40]:40} ${txn['amount']:>10,.2f}")
    
    print("\n" + "="*70)
    print("MERCURY API TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_mercury_extractor()

