"""
Supabase Loader - Complete Fixed Version
Handles all database operations for loading data into Supabase.
"""

from supabase import create_client, Client
from typing import List, Dict
from datetime import datetime

class SupabaseLoader:
    """Load data into Supabase database."""
    
    def __init__(self, url: str, key: str):
        """Initialize Supabase client."""
        self.client: Client = create_client(url, key)
        print("Supabase Loader initialized")
    
    def load_mercury_accounts(self, accounts: List[Dict]) -> int:
        """Load Mercury accounts into database."""
        print(f"  → Loading {len(accounts)} Mercury accounts...")
        
        if not accounts:
            print("  ✓ No accounts to load")
            return 0
        
        # Add sync timestamp
        for account in accounts:
            account["synced_at"] = datetime.now().isoformat()
        
        # Upsert (insert or update if exists)
        response = self.client.table("mercury_accounts").upsert(
            accounts,
            on_conflict="account_id"
        ).execute()
        
        print(f"  ✓ Loaded {len(accounts)} accounts")
        return len(accounts)
    
    def load_mercury_transactions(self, transactions: List[Dict]) -> int:
        """Load Mercury transactions into database."""
        print(f"  → Loading {len(transactions)} Mercury transactions...")
        
        if not transactions:
            print("  ✓ No transactions to load")
            return 0
        
        for txn in transactions:
            txn["synced_at"] = datetime.now().isoformat()
        
        response = self.client.table("mercury_transactions").upsert(
            transactions,
            on_conflict="transaction_id"
        ).execute()
        
        print(f"  ✓ Loaded {len(transactions)} transactions")
        return len(transactions)
    
    def load_quickbooks_invoices(self, invoices: List[Dict]) -> int:
        """Load QuickBooks invoices into database."""
        print(f"  → Loading {len(invoices)} QuickBooks invoices...")
        
        if not invoices:
            print("  ✓ No invoices to load")
            return 0
        
        for invoice in invoices:
            invoice["synced_at"] = datetime.now().isoformat()
        
        response = self.client.table("quickbooks_invoices").upsert(
            invoices,
            on_conflict="invoice_id"
        ).execute()
        
        print(f"  ✓ Loaded {len(invoices)} invoices")
        return len(invoices)
    
    def load_quickbooks_payments(self, payments: List[Dict]) -> int:
        """Load QuickBooks payments into database."""
        print(f"  → Loading {len(payments)} QuickBooks payments...")
        
        if not payments:
            print("  ✓ No payments to load")
            return 0
        
        for payment in payments:
            payment["synced_at"] = datetime.now().isoformat()
        
        # Load payments one by one to handle foreign key issues gracefully
        loaded = 0
        skipped = 0
        
        for payment in payments:
            try:
                self.client.table("quickbooks_payments").upsert(
                    [payment],
                    on_conflict="payment_id"
                ).execute()
                loaded += 1
            except Exception as e:
                # Skip payments for invoices that don't exist
                error_msg = str(e).lower()
                if "foreign key constraint" in error_msg or "violates foreign key" in error_msg:
                    skipped += 1
                else:
                    print(f"  Error loading payment {payment.get('payment_id', 'unknown')}: {str(e)[:80]}")
        
        if skipped > 0:
            print(f"  ✓ Loaded {loaded} payments (skipped {skipped} with missing invoices)")
        else:
            print(f"  ✓ Loaded {loaded} payments")
        
        return loaded
    
    def load_github_commits(self, commits: List[Dict]) -> int:
        """Load GitHub commits into database."""
        print(f"  → Loading {len(commits)} GitHub commits...")
        
        if not commits:
            print("  ✓ No commits to load")
            return 0
        
        for commit in commits:
            commit["synced_at"] = datetime.now().isoformat()
        
        response = self.client.table("github_commits").upsert(
            commits,
            on_conflict="commit_sha"
        ).execute()
        
        print(f"  ✓ Loaded {len(commits)} commits")
        return len(commits)
    
    def load_github_pull_requests(self, prs: List[Dict]) -> int:
        """Load GitHub pull requests into database."""
        print(f"  → Loading {len(prs)} GitHub PRs...")

        if not prs:
            print("  ✓ No PRs to load")
            return 0

        for pr in prs:
            pr["synced_at"] = datetime.now().isoformat()

        try:
            # Try bulk upsert with composite key (pr_number + repository)
            response = self.client.table("github_pull_requests").upsert(
                prs,
                on_conflict="pr_number,repository"
            ).execute()

            print(f"  ✓ Loaded {len(prs)} pull requests")
            return len(prs)

        except Exception as e:
            # If bulk upsert fails, try individual inserts
            print(f"  ⚠ Bulk upsert failed: {str(e)[:80]}")
            print(f"  → Trying individual inserts...")

            loaded = 0
            for pr in prs:
                try:
                    self.client.table("github_pull_requests").insert(pr).execute()
                    loaded += 1
                except Exception:
                    # If duplicate, try update instead
                    try:
                        self.client.table("github_pull_requests")\
                            .update(pr)\
                            .eq("pr_number", pr["pr_number"])\
                            .eq("repository", pr["repository"])\
                            .execute()
                        loaded += 1
                    except Exception as insert_error:
                        print(f"  ⚠ Skipped PR #{pr.get('pr_number', 'unknown')}: {str(insert_error)[:60]}")

            print(f"  ✓ Loaded {loaded} pull requests")
            return loaded
    
    def get_latest_metrics(self) -> Dict:
        """Get the most recent weekly metrics."""
        response = self.client.table("weekly_metrics")\
            .select("*")\
            .order("week_start", desc=True)\
            .limit(1)\
            .execute()
        
        return response.data[0] if response.data else None