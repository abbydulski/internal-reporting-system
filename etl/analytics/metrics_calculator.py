"""
Metrics Calculator
Calculates business metrics from raw data stored in Supabase.
"""

from datetime import datetime, timedelta
from typing import Dict
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
            "generated_at": datetime.now().isoformat()
        }
        
        # Display metrics
        print("\n" + "="*50)
        print("CALCULATED METRICS")
        print("="*50)
        for key, value in metrics.items():
            if key not in ["week_start", "week_end", "generated_at"]:
                if isinstance(value, (int, float)) and key != "developer_commits" and key != "prs_merged":
                    print(f"  {key:.<40} ${value:>12,.2f}")
                else:
                    print(f"  {key:.<40} {value:>12}")
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
        """Get current bank balance from Mercury."""
        print("  → Getting Current Balance...")
        
        response = self.client.table("mercury_accounts")\
            .select("balance")\
            .order("synced_at", desc=True)\
            .limit(1)\
            .execute()
        
        if response.data:
            balance = float(response.data[0]["balance"])
            print(f"    ✓ Balance: ${balance:,.2f}")
            return round(balance, 2)
        
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
    
    def save_weekly_metrics(self, metrics: Dict) -> bool:
        """Save calculated metrics to database."""
        print("  → Saving metrics to database...")
        
        response = self.client.table("weekly_metrics").insert(metrics).execute()
        
        print(f"  ✓ Metrics saved for week {metrics['week_start']}")
        return True