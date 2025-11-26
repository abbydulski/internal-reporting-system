"""
ETL Scheduler
Main orchestration script that runs the entire ETL pipeline.
"""

from datetime import datetime
from etl.config import Config
from etl.extractors.mercury_extractor import MercuryExtractor
# from etl.extractors.quickbooks_extractor_MOCK import QuickBooksExtractor  # MOCK version
from etl.extractors.quickbooks_extractor import QuickBooksExtractor  # REAL API version (requires OAuth)
# from etl.extractors.quickbooks_csv_importer import QuickBooksCSVImporter as QuickBooksExtractor  # CSV version (no OAuth)
from etl.extractors.github_extractor import GitHubExtractor
from etl.loaders.supabase_loader import SupabaseLoader
from etl.analytics.metrics_calculator import MetricsCalculator
from etl.slack.slack_reporter import SlackReporter
from supabase import create_client

def run_daily_sync():
    """
    Daily ETL job: Extract data from all sources and load into Supabase.
    """
    print("\n" + "="*70)
    print("STARTING DAILY DATA SYNC")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize components
    mercury = MercuryExtractor(Config.MERCURY_API_KEY)

    # QuickBooks - REAL (using production data)
    quickbooks = QuickBooksExtractor(
        Config.QUICKBOOKS_CLIENT_ID,
        Config.QUICKBOOKS_CLIENT_SECRET,
        Config.QUICKBOOKS_REFRESH_TOKEN,
        Config.QUICKBOOKS_REALM_ID,
        is_sandbox=False  # Production mode
    )

    # Alternative options (comment/uncomment as needed):

    # MOCK version (fake data for testing):
    # from etl.extractors.quickbooks_extractor_MOCK import QuickBooksExtractor
    # quickbooks = QuickBooksExtractor("mock", "mock", "mock")

    # CSV Import (no OAuth required):
    # from etl.extractors.quickbooks_csv_importer import QuickBooksCSVImporter as QuickBooksExtractor
    # quickbooks = QuickBooksExtractor(
    #     invoices_csv="quickbooks_invoices.csv",
    #     payments_csv="quickbooks_payments.csv"
    # )

    github = GitHubExtractor(Config.GITHUB_TOKEN, Config.GITHUB_ORG)
    loader = SupabaseLoader(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    print("\n--- PHASE 1: EXTRACT ---")
    
    # Extract Mercury data
    print("\nMercury:")
    mercury_accounts = mercury.get_accounts()
    mercury_transactions = mercury.get_transactions(days_back=90)
    
    # Extract QuickBooks data
    print("\nQuickBooks:")
    qb_invoices = quickbooks.get_invoices(days_back=90)
    qb_payments = quickbooks.get_payments(days_back=90)
    
    # Extract GitHub data
    print("\nGitHub:")
    # Option 1: Track entire organization (all repos)
    if Config.GITHUB_REPO == "ALL" or Config.GITHUB_REPO == "your-repo":
        gh_commits = github.get_all_commits(days_back=90)
        gh_prs = github.get_all_pull_requests(days_back=90)
    # Option 2: Track specific repo only
    else:
        gh_commits = github.get_commits(repo=Config.GITHUB_REPO, days_back=90)
        gh_prs = github.get_pull_requests(repo=Config.GITHUB_REPO, days_back=90)
    
    print("\n--- PHASE 2: LOAD ---")
    
    # Load all data into Supabase
    print("\nLoading into Supabase:")
    loader.load_mercury_accounts(mercury_accounts)
    loader.load_mercury_transactions(mercury_transactions)
    loader.load_quickbooks_invoices(qb_invoices)
    loader.load_quickbooks_payments(qb_payments)
    loader.load_github_commits(gh_commits)
    loader.load_github_pull_requests(gh_prs)
    
    print("\n" + "="*70)
    print("DAILY SYNC COMPLETE")
    print("="*70 + "\n")

def run_weekly_report():
    """
    Weekly reporting job: Calculate metrics and send to Slack.
    """
    print("\n" + "="*70)
    print("GENERATING WEEKLY REPORT")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize components
    supabase_client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    calculator = MetricsCalculator(supabase_client)
    reporter = SlackReporter(Config.SLACK_WEBHOOK_URL, Config.SLACK_WEBHOOK_URL_2, Config.SLACK_WEBHOOK_URL_3)
    loader = SupabaseLoader(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    # Calculate metrics
    metrics = calculator.calculate_weekly_metrics()
    
    # Save to database
    calculator.save_weekly_metrics(metrics)
    
    # Send to Slack
    reporter.send_weekly_report(metrics)
    
    print("\n" + "="*70)
    print("WEEKLY REPORT COMPLETE")
    print("="*70 + "\n")

def run_full_pipeline():
    """
    Run both daily sync and weekly report.
    Useful for manual runs and testing.
    """
    run_daily_sync()
    run_weekly_report()

if __name__ == "__main__":
    # When run directly, execute full pipeline
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "sync":
            run_daily_sync()
        elif command == "report":
            run_weekly_report()
        elif command == "full":
            run_full_pipeline()
        else:
            print("Usage: python -m etl.scheduler [sync|report|full]")
    else:
        # Default: run full pipeline
        run_full_pipeline()