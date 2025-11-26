"""
Metrics Calculator
Calculates business metrics from raw data stored in Supabase.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from supabase import Client

class MetricsCalculator:
    """Calculate business metrics from database."""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        print("Metrics Calculator initialized")
    
    def calculate_weekly_metrics(self, week_start: str = None) -> Dict:
        """
        Calculate all metrics for a given week.
        
        Args:
            week_start: Start date in YYYY-MM-DD format. If None, uses current week.
        
        Returns:
            Dictionary with all calculated metrics
        """
        if not week_start:
            # Get Monday of current week
            today = datetime.now()
            week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        
        week_end = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
        
        print(f"\nCalculating metrics for week: {week_start} to {week_end}")
        
        metrics = {
            "week_start": week_start,
            "week_end": week_end,
            "accounts_receivable": self._calculate_ar(),
            "cash_collected": self._calculate_cash_collected(week_start, week_end),
            "invoiced_amount": self._calculate_invoiced(week_start, week_end),
            "current_balance": self._get_current_balance(),
            "developer_commits": self._count_commits(week_start, week_end),
            "prs_merged": self._count_prs_merged(week_start, week_end),
            "prs_by_author": self._get_prs_by_author(week_start, week_end),
            "recent_transactions": self._get_recent_transactions(week_start, week_end),
            "generated_at": datetime.now().isoformat()
        }
        
        # Display metrics
        print("\n" + "="*50)
        print("CALCULATED METRICS")
        print("="*50)
        for key, value in metrics.items():
            if key not in ["week_start", "week_end", "generated_at", "prs_by_author", "recent_transactions"]:
                if isinstance(value, (int, float)) and key != "developer_commits" and key != "prs_merged":
                    print(f"  {key:.<40} ${value:>12,.2f}")
                else:
                    print(f"  {key:.<40} {value:>12}")

        # Display PRs by author separately
        if metrics.get("prs_by_author"):
            print(f"\n  PRs by Author:")
            for author, count in metrics["prs_by_author"].items():
                print(f"    • {author}: {count}")

        # Display recent transactions
        if metrics.get("recent_transactions"):
            print(f"\n  Recent Transactions ({len(metrics['recent_transactions'])}):")
            for txn in metrics["recent_transactions"][:5]:
                print(f"    {txn['date']}: {txn['description'][:30]:30} ${txn['amount']:>10,.2f}")

        print("="*50 + "\n")
        
        return metrics
    
    def _calculate_ar(self) -> float:
        """Calculate Accounts Receivable (unpaid invoice balances)."""
        print("  → Calculating Accounts Receivable...")
        
        response = self.client.table("quickbooks_invoices")\
            .select("balance")\
            .neq("status", "Paid")\
            .execute()
        
        ar = sum(float(invoice["balance"]) for invoice in response.data)
        print(f"    ✓ AR: ${ar:,.2f}")
        return round(ar, 2)
    
    def _calculate_cash_collected(self, start_date: str, end_date: str) -> float:
        """Calculate cash collected in date range."""
        print(f"  → Calculating Cash Collected ({start_date} to {end_date})...")
        
        response = self.client.table("quickbooks_payments")\
            .select("amount")\
            .gte("payment_date", start_date)\
            .lte("payment_date", end_date)\
            .execute()
        
        collected = sum(float(payment["amount"]) for payment in response.data)
        print(f"    ✓ Cash Collected: ${collected:,.2f}")
        return round(collected, 2)
    
    def _calculate_invoiced(self, start_date: str, end_date: str) -> float:
        """Calculate total amount invoiced in date range."""
        print(f"  → Calculating Invoiced Amount ({start_date} to {end_date})...")
        
        response = self.client.table("quickbooks_invoices")\
            .select("total_amount")\
            .gte("invoice_date", start_date)\
            .lte("invoice_date", end_date)\
            .execute()
        
        invoiced = sum(float(invoice["total_amount"]) for invoice in response.data)
        print(f"    ✓ Invoiced: ${invoiced:,.2f}")
        return round(invoiced, 2)
    
    def _get_current_balance(self) -> float:
        """Get current bank balance from Mercury (sum of all accounts)."""
        print("  → Getting Current Balance...")

        # Get the most recent sync timestamp
        latest_sync = self.client.table("mercury_accounts")\
            .select("synced_at")\
            .order("synced_at", desc=True)\
            .limit(1)\
            .execute()

        if not latest_sync.data:
            return 0.0

        latest_timestamp = latest_sync.data[0]["synced_at"]

        # Parse the timestamp to get just the date and time (ignore microseconds)
        # Get all accounts synced within the last minute (same batch)
        latest_dt = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
        cutoff_dt = latest_dt - timedelta(seconds=10)  # Within 10 seconds = same sync

        # Get all accounts from the most recent sync batch
        response = self.client.table("mercury_accounts")\
            .select("balance, name, synced_at")\
            .gte("synced_at", cutoff_dt.isoformat())\
            .execute()

        if response.data:
            total_balance = sum(float(acc["balance"]) for acc in response.data)
            print(f"    ✓ Total Balance across {len(response.data)} account(s): ${total_balance:,.2f}")
            return round(total_balance, 2)

        return 0.0
    
    def _count_commits(self, start_date: str, end_date: str) -> int:
        """Count commits in date range."""
        print(f"  → Counting Commits ({start_date} to {end_date})...")

        # Convert dates to ISO format for timestamp comparison
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d").isoformat()
        end_datetime = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).isoformat()

        response = self.client.table("github_commits")\
            .select("commit_sha", count="exact")\
            .gte("date", start_datetime)\
            .lt("date", end_datetime)\
            .execute()

        count = response.count if hasattr(response, 'count') else len(response.data)
        print(f"    ✓ Commits: {count}")
        return count

    def _get_commits_by_author(self, start_date: str, end_date: str) -> Dict[str, int]:
        """Get commit count grouped by author."""
        print(f"  → Counting Commits by Author ({start_date} to {end_date})...")

        # Convert dates to ISO format for timestamp comparison
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d").isoformat()
        end_datetime = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).isoformat()

        response = self.client.table("github_commits")\
            .select("author")\
            .gte("date", start_datetime)\
            .lt("date", end_datetime)\
            .execute()

        # Count commits per author
        commits_by_author = {}
        for commit in response.data:
            author = commit.get("author", "Unknown")
            commits_by_author[author] = commits_by_author.get(author, 0) + 1

        # Sort by commit count (descending)
        commits_by_author = dict(sorted(commits_by_author.items(), key=lambda x: x[1], reverse=True))

        print(f"    ✓ Found commits from {len(commits_by_author)} author(s)")
        return commits_by_author
    
    def _count_prs_merged(self, start_date: str, end_date: str) -> int:
        """Count PRs merged in date range."""
        print(f"  → Counting Merged PRs ({start_date} to {end_date})...")

        start_datetime = datetime.strptime(start_date, "%Y-%m-%d").isoformat()
        end_datetime = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).isoformat()

        response = self.client.table("github_pull_requests")\
            .select("pr_number", count="exact")\
            .eq("state", "merged")\
            .gte("merged_at", start_datetime)\
            .lt("merged_at", end_datetime)\
            .execute()

        count = response.count if hasattr(response, 'count') else len(response.data)
        print(f"    ✓ PRs Merged: {count}")
        return count

    def _get_prs_by_author(self, start_date: str, end_date: str) -> Dict[str, int]:
        """Get PR count grouped by author."""
        print(f"  → Counting PRs by Author ({start_date} to {end_date})...")

        # Convert dates to ISO format for timestamp comparison
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d").isoformat()
        end_datetime = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).isoformat()

        response = self.client.table("github_pull_requests")\
            .select("author")\
            .eq("state", "merged")\
            .gte("merged_at", start_datetime)\
            .lt("merged_at", end_datetime)\
            .execute()

        # Count PRs per author
        prs_by_author = {}
        for pr in response.data:
            author = pr.get("author", "Unknown")
            prs_by_author[author] = prs_by_author.get(author, 0) + 1

        # Sort by PR count (descending)
        prs_by_author = dict(sorted(prs_by_author.items(), key=lambda x: x[1], reverse=True))

        print(f"    ✓ Found PRs from {len(prs_by_author)} author(s)")
        return prs_by_author

    def _get_recent_transactions(self, start_date: str, end_date: str) -> List[Dict]:
        """Get recent Mercury transactions for the week."""
        print(f"  → Fetching Recent Transactions ({start_date} to {end_date})...")

        response = self.client.table("mercury_transactions")\
            .select("date, description, amount, type")\
            .gte("date", start_date)\
            .lte("date", end_date)\
            .order("date", desc=True)\
            .limit(10)\
            .execute()

        print(f"    ✓ Found {len(response.data)} transactions")
        return response.data
    
    def save_weekly_metrics(self, metrics: Dict) -> bool:
        """Save calculated metrics to database."""
        print("  → Saving metrics to database...")

        # Create a copy without non-database columns
        db_metrics = {k: v for k, v in metrics.items() if k not in ["prs_by_author", "recent_transactions"]}

        response = self.client.table("weekly_metrics").insert(db_metrics).execute()

        print(f"  ✓ Metrics saved for week {metrics['week_start']}")
        return True