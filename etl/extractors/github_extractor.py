"""
GitHub API Extractor (REAL Implementation)
Connects to actual GitHub API to fetch development metrics.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict

class GitHubExtractor:
    """Extract development metrics from GitHub API."""
    
    def __init__(self, token: str, org: str):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub Personal Access Token
            org: GitHub username or organization name
        """
        self.token = token
        self.org = org
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        print(f"GitHub Extractor initialized for: {org}")
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test that the GitHub API connection works."""
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                user = response.json()
                print(f"  ✓ Connected as: {user.get('login', 'Unknown')}")
            else:
                print(f" Warning: GitHub API returned status {response.status_code}")
        except Exception as e:
            print(f" Warning: Could not verify GitHub connection: {e}")

    def get_org_repos(self) -> List[str]:
        """
        Get all repositories in the organization.

        Returns:
            List of repository names
        """
        print(f"  → Fetching repositories for organization: {self.org}...")

        repos = []
        page = 1

        try:
            while page <= 10:  # Limit to 10 pages (1000 repos max)
                url = f"{self.base_url}/orgs/{self.org}/repos"
                params = {
                    "per_page": 100,
                    "page": page,
                    "type": "all"  # all, public, private, forks, sources, member
                }

                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )

                if response.status_code != 200:
                    # If org endpoint fails, try user repos
                    url = f"{self.base_url}/users/{self.org}/repos"
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params=params,
                        timeout=10
                    )

                    if response.status_code != 200:
                        print(f"  Warning: Could not fetch repos (status {response.status_code})")
                        break

                page_repos = response.json()

                if not page_repos:
                    break

                for repo in page_repos:
                    repos.append(repo["name"])

                page += 1

            print(f"  ✓ Found {len(repos)} repositories")
            return repos

        except Exception as e:
            print(f"  Error fetching repositories: {e}")
            return []
    
    def get_all_commits(self, days_back: int = 30) -> List[Dict]:
        """
        Get commits from ALL repositories in the organization.

        Args:
            days_back: Number of days to look back

        Returns:
            List of commit dictionaries from all repos
        """
        print(f"  → Fetching commits from ALL repos in {self.org} (last {days_back} days)...")

        repos = self.get_org_repos()
        all_commits = []

        for repo in repos:
            repo_commits = self.get_commits(repo=repo, days_back=days_back)
            all_commits.extend(repo_commits)

        print(f"  ✓ Total commits across all repos: {len(all_commits)}")
        return all_commits

    def get_commits(self, repo: str = "test-metrics-repo", days_back: int = 30) -> List[Dict]:
        """
        Get commits from repository.
        
        Args:
            repo: Repository name
            days_back: Number of days to look back
            
        Returns:
            List of commit dictionaries
        """
        print(f"  → Fetching GitHub commits for {self.org}/{repo} (last {days_back} days)...")
        
        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        commits = []
        page = 1
        
        try:
            while page <= 3:  # Limit to 3 pages (300 commits max)
                url = f"{self.base_url}/repos/{self.org}/{repo}/commits"
                params = {
                    "since": since_date,
                    "per_page": 100,
                    "page": page
                }
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code != 200:
                    print(f"  GitHub API error: {response.status_code}")
                    if response.status_code == 404:
                        print(f"  Repository {self.org}/{repo} not found. Check repo name!")
                    break
                
                page_commits = response.json()
                
                if not page_commits:
                    break
                
                for commit in page_commits:
                    commits.append({
                        "commit_sha": commit["sha"],
                        "author": commit["commit"]["author"]["name"],
                        "date": commit["commit"]["author"]["date"],
                        "repository": repo,
                        "message": commit["commit"]["message"].split('\n')[0][:200],  # First line only
                        "additions": 0,  # Would need additional API call for stats
                        "deletions": 0   # Would need additional API call for stats
                    })
                
                page += 1
            
            print(f"  ✓ Found {len(commits)} commits")
            return commits
            
        except requests.exceptions.Timeout:
            print("  GitHub API timeout. Using cached data if available.")
            return []
        except Exception as e:
            print(f"  Error fetching commits: {e}")
            return []
    
    def get_all_pull_requests(self, days_back: int = 30) -> List[Dict]:
        """
        Get pull requests from ALL repositories in the organization.

        Args:
            days_back: Number of days to look back

        Returns:
            List of PR dictionaries from all repos
        """
        print(f"  → Fetching PRs from ALL repos in {self.org} (last {days_back} days)...")

        repos = self.get_org_repos()
        all_prs = []

        for repo in repos:
            repo_prs = self.get_pull_requests(repo=repo, days_back=days_back)
            all_prs.extend(repo_prs)

        print(f"  ✓ Total PRs across all repos: {len(all_prs)}")
        return all_prs

    def get_pull_requests(self, repo: str = "test-metrics-repo", days_back: int = 30) -> List[Dict]:
        """
        Get pull requests from repository.
        
        Args:
            repo: Repository name
            days_back: Number of days to look back
            
        Returns:
            List of PR dictionaries
        """
        print(f"  → Fetching GitHub PRs for {self.org}/{repo} (last {days_back} days)...")
        
        since_date = datetime.now() - timedelta(days=days_back)
        
        prs = []
        page = 1
        
        try:
            while page <= 3:  # Limit to 3 pages
                url = f"{self.base_url}/repos/{self.org}/{repo}/pulls"
                params = {
                    "state": "all",  # Get both open and closed
                    "per_page": 100,
                    "page": page,
                    "sort": "updated",
                    "direction": "desc"
                }
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code != 200:
                    print(f"  GitHub API error: {response.status_code}")
                    break
                
                page_prs = response.json()
                
                if not page_prs:
                    break
                
                for pr in page_prs:
                    created_at = datetime.fromisoformat(pr["created_at"].replace('Z', '+00:00'))
                    
                    # Only include PRs from our date range
                    if created_at.replace(tzinfo=None) < since_date:
                        continue
                    
                    merged_at = None
                    if pr.get("merged_at"):
                        merged_at = pr["merged_at"]
                    
                    prs.append({
                        "pr_number": pr["number"],
                        "repository": repo,
                        "author": pr["user"]["login"],
                        "title": pr["title"][:200],
                        "state": "merged" if pr.get("merged_at") else pr["state"],
                        "created_at_github": pr["created_at"],
                        "merged_at": merged_at
                    })
                
                page += 1
            
            print(f"  ✓ Found {len(prs)} pull requests")
            return prs
            
        except requests.exceptions.Timeout:
            print("  GitHub API timeout. Using cached data if available.")
            return []
        except Exception as e:
            print(f"  Error fetching pull requests: {e}")
            return []
    
    def get_repositories(self) -> List[str]:
        """
        Get list of repositories for the user/org.
        
        Returns:
            List of repository names
        """
        print(f"  → Fetching repositories for {self.org}...")
        
        try:
            url = f"{self.base_url}/users/{self.org}/repos"
            params = {
                "per_page": 100,
                "sort": "updated"
            }
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"  GitHub API error: {response.status_code}")
                return []
            
            repos = response.json()
            repo_names = [repo["name"] for repo in repos]
            
            print(f"  ✓ Found {len(repo_names)} repositories")
            return repo_names
            
        except Exception as e:
            print(f"  Error fetching repositories: {e}")
            return []


# Test function
def test_github_extractor():
    """Test the GitHub extractor with your credentials."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    token = os.getenv("GITHUB_TOKEN")
    org = os.getenv("GITHUB_ORG")
    
    if not token or not org:
        print("Missing GITHUB_TOKEN or GITHUB_ORG in .env file")
        return
    
    print("\n" + "="*60)
    print("TESTING GITHUB API CONNECTION")
    print("="*60 + "\n")
    
    extractor = GitHubExtractor(token, org)
    
    # List repositories
    print("\n--- Available Repositories ---")
    repos = extractor.get_repositories()
    for repo in repos[:10]:  # Show first 10
        print(f"  • {repo}")
    
    # Test with first repo or default
    test_repo = repos[0] if repos else "test-metrics-repo"
    
    print(f"\n--- Testing with repository: {test_repo} ---")
    
    # Get commits
    commits = extractor.get_commits(repo=test_repo, days_back=30)
    if commits:
        print(f"\nSample commit:")
        print(f"  SHA: {commits[0]['commit_sha'][:7]}")
        print(f"  Author: {commits[0]['author']}")
        print(f"  Message: {commits[0]['message']}")
        print(f"  Date: {commits[0]['date']}")
    
    # Get PRs
    prs = extractor.get_pull_requests(repo=test_repo, days_back=30)
    if prs:
        print(f"\nSample PR:")
        print(f"  Number: #{prs[0]['pr_number']}")
        print(f"  Title: {prs[0]['title']}")
        print(f"  Author: {prs[0]['author']}")
        print(f"  State: {prs[0]['state']}")
    
    print("\n" + "="*60)
    print("GITHUB API TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_github_extractor()