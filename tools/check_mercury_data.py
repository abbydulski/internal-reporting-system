"""
Quick diagnostic to check Mercury data in Supabase
"""

from etl.config import Config
from supabase import create_client

def check_mercury_data():
    """Check what Mercury data is in Supabase."""
    
    print("\n" + "="*70)
    print("CHECKING MERCURY DATA IN SUPABASE")
    print("="*70 + "\n")
    
    client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    # Check accounts
    print("--- Mercury Accounts ---")
    accounts_response = client.table("mercury_accounts")\
        .select("*")\
        .order("synced_at", desc=True)\
        .execute()
    
    if accounts_response.data:
        print(f"Found {len(accounts_response.data)} account records:\n")
        for acc in accounts_response.data[:5]:  # Show first 5
            print(f"  Account: {acc.get('name', 'Unknown')}")
            print(f"  Balance: ${acc.get('balance', 0):,.2f}")
            print(f"  Synced: {acc.get('synced_at', 'Unknown')}")
            print()
    else:
        print("❌ NO ACCOUNTS FOUND IN DATABASE!")
        print("   Run: python -m etl.scheduler sync")
        print()
    
    # Check transactions
    print("--- Mercury Transactions ---")
    txn_response = client.table("mercury_transactions")\
        .select("*", count="exact")\
        .order("date", desc=True)\
        .limit(5)\
        .execute()
    
    count = txn_response.count if hasattr(txn_response, 'count') else len(txn_response.data)
    print(f"Total transactions: {count}\n")
    
    if txn_response.data:
        print("Recent transactions:")
        for txn in txn_response.data:
            print(f"  {txn.get('date')}: {txn.get('description', 'Unknown')[:40]:40} ${txn.get('amount', 0):>10,.2f}")
    else:
        print("❌ NO TRANSACTIONS FOUND IN DATABASE!")
        print()
    
    # Check what the report would calculate
    print("\n--- What Report Would Show ---")
    balance_response = client.table("mercury_accounts")\
        .select("balance")\
        .order("synced_at", desc=True)\
        .limit(1)\
        .execute()
    
    if balance_response.data:
        balance = float(balance_response.data[0]["balance"])
        print(f"Current Balance (from most recent account): ${balance:,.2f}")
    else:
        print("Current Balance: $0.00 (no data)")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    check_mercury_data()

