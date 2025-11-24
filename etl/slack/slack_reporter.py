"""
Slack Reporter
Sends formatted reports to Slack via webhook.
"""

import requests
from typing import Dict
from datetime import datetime

class SlackReporter:
    """Send reports to Slack."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        print("Slack Reporter initialized")
    
    def send_weekly_report(self, metrics: Dict) -> bool:
        """
        Send weekly metrics report to Slack.
        
        Args:
            metrics: Dictionary with calculated metrics
        
        Returns:
            True if sent successfully
        """
        if not self.webhook_url or self.webhook_url == "":
            print("  No Slack webhook URL configured. Skipping report.")
            return False
        
        print("  → Sending weekly report to Slack...")
        
        # Format the message
        message = self._format_weekly_report(metrics)
        
        # Send to Slack
        response = requests.post(
            self.webhook_url,
            json=message,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("  ✓ Report sent to Slack successfully!")
            return True
        else:
            print(f"  ✗ Failed to send report. Status: {response.status_code}")
            return False
    
    def _format_weekly_report(self, metrics: Dict) -> Dict:
        """Format metrics into Slack Block Kit message."""
        
        week_start = metrics.get("week_start", "N/A")
        week_end = metrics.get("week_end", "N/A")
        
        # Format currency values
        ar = metrics.get("accounts_receivable", 0)
        collected = metrics.get("cash_collected", 0)
        invoiced = metrics.get("invoiced_amount", 0)
        balance = metrics.get("current_balance", 0)
        
        # Format developer metrics
        commits = metrics.get("developer_commits", 0)
        prs = metrics.get("prs_merged", 0)
        
        # Calculate some derived metrics
        collection_rate = (collected / invoiced * 100) if invoiced > 0 else 0
        
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Weekly Report: {week_start} to {week_end}",
                        "emoji": True
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Financial Metrics*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Accounts Receivable:*\n${ar:,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Cash Collected:*\n${collected:,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Invoiced This Week:*\n${invoiced:,.2f}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Current Balance:*\n${balance:,.2f}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"_Collection Rate: {collection_rate:.1f}%_"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Development Metrics*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Commits:*\n{commits}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*PRs Merged:*\n{prs}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Generated on {datetime.now().strftime('%Y-%m-%d at %I:%M %p')}"
                        }
                    ]
                }
            ]
        }
    
    def send_test_message(self) -> bool:
        """Send a test message to verify webhook works."""
        if not self.webhook_url:
            print("  No Slack webhook URL configured.")
            return False
        
        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Test Message*\n\nYour reporting system is connected!"
                    }
                }
            ]
        }
        
        response = requests.post(self.webhook_url, json=message)
        
        if response.status_code == 200:
            print("  ✓ Test message sent successfully!")
            return True
        else:
            print(f"  ✗ Failed to send test message. Status: {response.status_code}")
            return False