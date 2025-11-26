"""
QuickBooks CSV Importer
Import QuickBooks data from CSV exports (no API required).
"""

import csv
from datetime import datetime
from typing import List, Dict

class QuickBooksCSVImporter:
    """Import QuickBooks data from CSV files."""
    
    def __init__(self, invoices_csv: str = None, payments_csv: str = None):
        """
        Initialize CSV importer.
        
        Args:
            invoices_csv: Path to invoices CSV file
            payments_csv: Path to payments CSV file
        """
        self.invoices_csv = invoices_csv
        self.payments_csv = payments_csv
        print("💼 QuickBooks CSV Importer initialized")
    
    def get_invoices(self, days_back: int = 90) -> List[Dict]:
        """
        Import invoices from CSV.
        
        Expected CSV columns:
        - Invoice Number
        - Customer Name
        - Invoice Date
        - Due Date
        - Total Amount
        - Balance
        - Status
        """
        if not self.invoices_csv:
            print("  ⚠️  No invoices CSV file specified")
            return []
        
        print(f"  → Importing invoices from {self.invoices_csv}...")
        
        invoices = []
        try:
            with open(self.invoices_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    invoices.append({
                        "invoice_id": row.get("Invoice Number", ""),
                        "customer_id": row.get("Customer ID", ""),
                        "customer_name": row.get("Customer Name", ""),
                        "invoice_date": row.get("Invoice Date", ""),
                        "due_date": row.get("Due Date", ""),
                        "total_amount": float(row.get("Total Amount", 0)),
                        "balance": float(row.get("Balance", 0)),
                        "status": row.get("Status", "Unknown")
                    })
            
            print(f"  ✓ Imported {len(invoices)} invoices")
            return invoices
            
        except Exception as e:
            print(f"  ❌ Error importing invoices: {e}")
            return []
    
    def get_payments(self, days_back: int = 90) -> List[Dict]:
        """
        Import payments from CSV.
        
        Expected CSV columns:
        - Payment Number
        - Customer Name
        - Payment Date
        - Amount
        - Payment Method
        """
        if not self.payments_csv:
            print("  ⚠️  No payments CSV file specified")
            return []
        
        print(f"  → Importing payments from {self.payments_csv}...")
        
        payments = []
        try:
            with open(self.payments_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    payments.append({
                        "payment_id": row.get("Payment Number", ""),
                        "customer_id": row.get("Customer ID", ""),
                        "customer_name": row.get("Customer Name", ""),
                        "payment_date": row.get("Payment Date", ""),
                        "amount": float(row.get("Amount", 0)),
                        "payment_method": row.get("Payment Method", "Unknown")
                    })
            
            print(f"  ✓ Imported {len(payments)} payments")
            return payments
            
        except Exception as e:
            print(f"  ❌ Error importing payments: {e}")
            return []


# Instructions for exporting from QuickBooks
EXPORT_INSTRUCTIONS = """
HOW TO EXPORT DATA FROM QUICKBOOKS:

1. INVOICES:
   - Go to Sales → Invoices
   - Click "Export" or "Print/Export"
   - Select "Export to Excel" or "Export to CSV"
   - Save as: quickbooks_invoices.csv

2. PAYMENTS:
   - Go to Sales → Customers
   - Click "Receive Payment"
   - Export payment history
   - Save as: quickbooks_payments.csv

3. Place CSV files in the project root directory

4. Update scheduler.py to use CSV importer:
   
   from etl.extractors.quickbooks_csv_importer import QuickBooksCSVImporter
   
   quickbooks = QuickBooksCSVImporter(
       invoices_csv="quickbooks_invoices.csv",
       payments_csv="quickbooks_payments.csv"
   )
"""

if __name__ == "__main__":
    print(EXPORT_INSTRUCTIONS)

