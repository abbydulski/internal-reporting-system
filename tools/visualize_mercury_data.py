"""
Mercury Data Visualizer
Shows what data is being collected from Mercury API in a readable format.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path so we can import from etl
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.extractors.mercury_extractor import MercuryExtractor

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_section(title):
    """Print a section divider."""
    print(f"\n--- {title} ---")

def visualize_accounts(accounts):
    """Display accounts in a readable format."""
    print_section("BANK ACCOUNTS")
    
    if not accounts:
        print("  No accounts found")
        return
    
    total_balance = sum(acc['balance'] for acc in accounts)
    total_available = sum(acc['available_balance'] for acc in accounts)
    
    print(f"\n  Total Accounts: {len(accounts)}")
    print(f"  Total Balance: ${total_balance:,.2f}")
    print(f"  Total Available: ${total_available:,.2f}\n")
    
    for i, acc in enumerate(accounts, 1):
        print(f"  [{i}] {acc['name']}")
        print(f"      ID: {acc['account_id']}")
        print(f"      Type: {acc['type'].title()}")
        print(f"      Balance: ${acc['balance']:,.2f}")
        print(f"      Available: ${acc['available_balance']:,.2f}")
        print(f"      Status: {acc['status'].title()}")
        print()

def visualize_transactions(transactions):
    """Display transactions in a readable format."""
    print_section("RECENT TRANSACTIONS")
    
    if not transactions:
        print("  No transactions found")
        return
    
    # Summary statistics
    total_credits = sum(t['amount'] for t in transactions if t['amount'] > 0)
    total_debits = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
    net_change = total_credits - total_debits
    
    print(f"\n  Total Transactions: {len(transactions)}")
    print(f"  Total Credits (Money In): ${total_credits:,.2f}")
    print(f"  Total Debits (Money Out): ${total_debits:,.2f}")
    print(f"  Net Change: ${net_change:,.2f}")
    
    # Category breakdown
    categories = {}
    for txn in transactions:
        cat = txn['category']
        if cat not in categories:
            categories[cat] = {'count': 0, 'amount': 0}
        categories[cat]['count'] += 1
        categories[cat]['amount'] += txn['amount']
    
    print(f"\n  Breakdown by Category:")
    for cat, data in sorted(categories.items(), key=lambda x: abs(x[1]['amount']), reverse=True):
        print(f"    {cat:20} {data['count']:3} transactions  ${data['amount']:>12,.2f}")
    
    # Show recent transactions
    print(f"\n  Most Recent Transactions (showing first 10):")
    print(f"  {'Date':<12} {'Description':<40} {'Category':<15} {'Amount':>12}")
    print(f"  {'-'*12} {'-'*40} {'-'*15} {'-'*12}")
    
    for txn in transactions[:10]:
        desc = txn['description'][:40]
        amount_str = f"${txn['amount']:,.2f}"
        if txn['amount'] < 0:
            amount_str = f"-${abs(txn['amount']):,.2f}"
        
        print(f"  {txn['date']:<12} {desc:<40} {txn['category']:<15} {amount_str:>12}")

def visualize_transaction_timeline(transactions):
    """Show a simple timeline of transaction activity."""
    print_section("TRANSACTION TIMELINE")
    
    if not transactions:
        print("  No transactions to display")
        return
    
    # Group by date
    daily_totals = {}
    for txn in transactions:
        date = txn['date']
        if date not in daily_totals:
            daily_totals[date] = {'credits': 0, 'debits': 0, 'count': 0}
        
        if txn['amount'] > 0:
            daily_totals[date]['credits'] += txn['amount']
        else:
            daily_totals[date]['debits'] += abs(txn['amount'])
        daily_totals[date]['count'] += 1
    
    print(f"\n  {'Date':<12} {'Transactions':>12} {'Credits':>15} {'Debits':>15} {'Net':>15}")
    print(f"  {'-'*12} {'-'*12} {'-'*15} {'-'*15} {'-'*15}")
    
    for date in sorted(daily_totals.keys(), reverse=True):
        data = daily_totals[date]
        net = data['credits'] - data['debits']
        net_str = f"${net:,.2f}" if net >= 0 else f"-${abs(net):,.2f}"
        
        print(f"  {date:<12} {data['count']:>12} ${data['credits']:>14,.2f} ${data['debits']:>14,.2f} {net_str:>15}")

def export_to_csv(accounts, transactions):
    """Export data to CSV files."""
    print_section("EXPORT TO CSV")
    
    import csv
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export accounts
    accounts_file = f"mercury_accounts_{timestamp}.csv"
    with open(accounts_file, 'w', newline='') as f:
        if accounts:
            writer = csv.DictWriter(f, fieldnames=accounts[0].keys())
            writer.writeheader()
            writer.writerows(accounts)
    print(f"  ✓ Accounts exported to: {accounts_file}")
    
    # Export transactions
    transactions_file = f"mercury_transactions_{timestamp}.csv"
    with open(transactions_file, 'w', newline='') as f:
        if transactions:
            writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
            writer.writeheader()
            writer.writerows(transactions)
    print(f"  ✓ Transactions exported to: {transactions_file}")

def main():
    """Main visualization function."""
    load_dotenv()
    
    api_key = os.getenv("MERCURY_API_KEY")
    
    if not api_key or api_key.startswith("mock") or api_key.startswith("your_"):
        print("❌ No valid Mercury API key found in .env file")
        print("\nPlease set MERCURY_API_KEY in your .env file")
        return
    
    print_header("MERCURY DATA VISUALIZATION")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize extractor
    extractor = MercuryExtractor(api_key)
    
    # Fetch data
    print("\n🔄 Fetching data from Mercury API...")
    accounts = extractor.get_accounts()
    transactions = extractor.get_transactions(days_back=30)
    
    # Visualize
    visualize_accounts(accounts)
    visualize_transactions(transactions)
    visualize_transaction_timeline(transactions)
    
    # Ask if user wants to export
    print("\n" + "="*80)
    export = input("\nWould you like to export this data to CSV files? (y/n): ").lower().strip()
    if export == 'y':
        export_to_csv(accounts, transactions)
    
    print("\n" + "="*80)
    print("  VISUALIZATION COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

