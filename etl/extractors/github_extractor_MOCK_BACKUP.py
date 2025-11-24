"""
GitHub API Extractor (Mock Implementation)
Generates realistic development metrics for testing.
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict

class GitHubExtractor:
    """Extract development metrics from GitHub API."""
    
    def __init__(self, token: str, org: str):
        self.token = token
        self.org = org
        print("GitHub Extractor initialized (MOCK MODE)")
    
    def get_commits(self, repo: str = "main-app", days_back: int = 30) -> List[Dict]:
        """Get commits from repository."""
        print(f"  → Fetching GitHub commits for {repo} (last {days_back} days)...")
        
        developers = ["alice", "bob", "charlie", "diana"]
        commit_types = [
            "Fix bug in payment processing",
            "Add new feature for user dashboard",
            "Update dependencies",
            "Refactor authentication module",
            "Improve performance of API endpoint",
            "Add tests for checkout flow",
            "Fix typo in documentation",
            "Implement user settings page"
        ]
        
        commits = []
        base_date = datetime.now()
        
        for i in range(random.randint(30, 60)):
            commit_date = base_date - timedelta(days=random.randint(0, days_back))
            
            commits.append({
                "commit_sha": f"abc{i:05d}def",
                "author": random.choice(developers),
                "date": commit_date.isoformat(),
                "repository": repo,
                "message": random.choice(commit_types),
                "additions": random.randint(5, 200),
                "deletions": random.randint(1, 100)
            })
        
        return commits
    
    def get_pull_requests(self, repo: str = "main-app", days_back: int = 30) -> List[Dict]:
        """Get pull requests from repository."""
        print(f"  → Fetching GitHub PRs for {repo} (last {days_back} days)...")
        
        developers = ["alice", "bob", "charlie", "diana"]
        pr_titles = [
            "Add payment gateway integration",
            "Fix authentication bug",
            "Update user interface components",
            "Improve database queries",
            "Add email notification system",
            "Refactor API endpoints"
        ]
        
        prs = []
        base_date = datetime.now()
        
        for i in range(random.randint(10, 20)):
            created = base_date - timedelta(days=random.randint(0, days_back))
            is_merged = random.random() > 0.2
            merged = created + timedelta(days=random.randint(1, 7)) if is_merged else None
            
            prs.append({
                "pr_number": i + 1,
                "repository": repo,
                "author": random.choice(developers),
                "title": random.choice(pr_titles),
                "state": "merged" if is_merged else "open",
                "created_at_github": created.isoformat(),
                "merged_at": merged.isoformat() if merged else None
            })
        
        return prs