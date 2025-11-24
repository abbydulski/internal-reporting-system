"""
QuickBooks API Extractor (Mock Implementation)
Generates realistic accounting data for testing.
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict

class QuickBooksExtractor:
    """Extract accounting data from QuickBooks API."""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        print("💼 QuickBooks Extractor initialized (MOCK MODE)")
    
    def get_invoices(self, days_back: int = 90) -> List[Dict]:
        """Get invoices from the last N days."""
        print(f"  → Fetching QuickBooks invoices (last {days_back} days)...")
        
        customers = [
            "Acme Corp", "Tech Solutions Inc", "Global Industries",
            "Startup Labs", "Enterprise Co", "Innovation Partners"
        ]
        
        invoices = []
        base_date = datetime.now()
        
        for i in range(random.randint(15, 30)):
            invoice_date = base_date - timedelta(days=random.randint(0, days_back))
            due_date = invoice_date + timedelta(days=30)
            total = random.uniform(5000, 50000)
            
            # Some invoices are paid, some aren't
            is_paid = random.random() > 0.3
            balance = 0 if is_paid else total
            status = "Paid" if is_paid else ("Overdue" if due_date < base_date else "Unpaid")
            
            invoices.append({
                "invoice_id": f"INV-{i+1:04d}",
                "customer_id": f"CUST-{random.randint(1, 6):03d}",
                "customer_name": random.choice(customers),
                "invoice_date": invoice_date.strftime("%Y-%m-%d"),
                "due_date": due_date.strftime("%Y-%m-%d"),
                "total_amount": round(total, 2),
                "balance": round(balance, 2),
                "status": status
            })
        
        return invoices
    
    def get_payments(self, days_back: int = 90) -> List[Dict]:
        """Get payments received."""
        print(f"  → Fetching QuickBooks payments (last {days_back} days)...")
        
        # Generate payments for some invoices
        invoices = self.get_invoices(days_back)
        paid_invoices = [inv for inv in invoices if inv["status"] == "Paid"]
        
        payments = []
        for i, invoice in enumerate(paid_invoices):
            payment_date = datetime.strptime(invoice["invoice_date"], "%Y-%m-%d") + timedelta(days=random.randint(1, 20))
            
            payments.append({
                "payment_id": f"PMT-{i+1:04d}",
                "invoice_id": invoice["invoice_id"],
                "payment_date": payment_date.strftime("%Y-%m-%d"),
                "amount": invoice["total_amount"]
            })
        
        return payments