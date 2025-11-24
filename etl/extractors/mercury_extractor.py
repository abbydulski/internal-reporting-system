"""
Mercury API Extractor (Mock Implementation)
Generates realistic banking data for testing.
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict

class MercuryExtractor:
    """Extract financial data from Mercury API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        print("Mercury Extractor initialized (MOCK MODE)")
    
    def get_accounts(self) -> List[Dict]:
        """Get all bank accounts."""
        print("  → Fetching Mercury accounts...")
        
        return [
            {
                "account_id": "merc_acc_001",
                "name": "Operating Account",
                "type": "checking",
                "balance": 125430.75,
                "available_balance": 120430.75,
                "currency": "USD",
                "status": "active"
            },
            {
                "account_id": "merc_acc_002",
                "name": "Savings Account",
                "type": "savings",
                "balance": 50000.00,
                "available_balance": 50000.00,
                "currency": "USD",
                "status": "active"
            }
        ]
    
    def get_transactions(self, days_back: int = 30) -> List[Dict]:
        """Get recent transactions."""
        print(f"  → Fetching Mercury transactions (last {days_back} days)...")
        
        transaction_templates = [
            {"desc": "Stripe Payment - Invoice #", "amount_range": (2000, 15000), "category": "Revenue"},
            {"desc": "AWS Services", "amount_range": (-2000, -500), "category": "Infrastructure"},
            {"desc": "Payroll - Employee", "amount_range": (-8000, -5000), "category": "Payroll"},
            {"desc": "Office Rent", "amount_range": (-3500, -2500), "category": "Rent"},
            {"desc": "SaaS Subscription", "amount_range": (-500, -50), "category": "Software"},
            {"desc": "Client Wire Transfer", "amount_range": (10000, 50000), "category": "Revenue"},
            {"desc": "Contractor Payment", "amount_range": (-6000, -3000), "category": "Contractors"},
            {"desc": "Marketing Campaign", "amount_range": (-2000, -500), "category": "Marketing"},
        ]
        
        transactions = []
        base_date = datetime.now()
        
        for i in range(random.randint(20, 40)):
            template = random.choice(transaction_templates)
            amount = random.uniform(*template["amount_range"])
            date = base_date - timedelta(days=random.randint(0, days_back))
            
            transactions.append({
                "transaction_id": f"merc_txn_{i+1:05d}",
                "account_id": "merc_acc_001",
                "date": date.strftime("%Y-%m-%d"),
                "amount": round(amount, 2),
                "description": f"{template['desc']}{random.randint(1000, 9999)}",
                "category": template["category"],
                "status": random.choice(["posted"] * 9 + ["pending"]),
                "type": "credit" if amount > 0 else "debit"
            })
        
        return sorted(transactions, key=lambda x: x["date"], reverse=True)