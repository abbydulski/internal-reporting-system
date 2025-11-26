"""
Slack Reporter
Sends formatted reports to Slack via webhook.
"""

import requests
from typing import Dict
from datetime import datetime

class SlackReporter:
    """Send reports to Slack."""

    def __init__(self, webhook_url: str, webhook_url_2: str = "", webhook_url_3: str = ""):
        """
        Initialize Slack reporter.

        Args:
            webhook_url: Primary Slack webhook URL
            webhook_url_2: Optional second Slack webhook URL for another channel
            webhook_url_3: Optional third Slack webhook URL for another channel
        """
        self.webhook_url = webhook_url
        self.webhook_url_2 = webhook_url_2
        self.webhook_url_3 = webhook_url_3

        channel_count = 1 + (1 if webhook_url_2 else 0) + (1 if webhook_url_3 else 0)
        print("Slack Reporter initialized")
        print(f"  → Will send to {channel_count} channel(s)")
    
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
        
        # Send to primary channel
        response = requests.post(
            self.webhook_url,
            json=message,
            headers={"Content-Type": "application/json"}
        )

        success = False
        if response.status_code == 200:
            print("  ✓ Report sent to primary channel successfully!")
            success = True
        else:
            print(f"  ✗ Failed to send to primary channel. Status: {response.status_code}")

        # Send to second channel if configured
        if self.webhook_url_2:
            response2 = requests.post(
                self.webhook_url_2,
                json=message,
                headers={"Content-Type": "application/json"}
            )

            if response2.status_code == 200:
                print("  ✓ Report sent to second channel successfully!")
            else:
                print(f"  ✗ Failed to send to second channel. Status: {response2.status_code}")

        # Send to third channel if configured
        if self.webhook_url_3:
            response3 = requests.post(
                self.webhook_url_3,
                json=message,
                headers={"Content-Type": "application/json"}
            )

            if response3.status_code == 200:
                print("  ✓ Report sent to third channel successfully!")
            else:
                print(f"  ✗ Failed to send to third channel. Status: {response3.status_code}")

        return success
    
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
        prs_by_author = metrics.get("prs_by_author", {})
        recent_transactions = metrics.get("recent_transactions", [])
        
        # Calculate some derived metrics
        collection_rate = (collected / invoiced * 100) if invoiced > 0 else 0

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Weekly Report: {week_start} to {week_end}",
                    "emoji": True
                }
            }
        ]

        blocks.extend([
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
                            "text": f"*Total Commits:*\n{commits}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*PRs Merged:*\n{prs}"
                        }
                    ]
                }
            ])

        # Add PRs by author breakdown if available
        if prs_by_author:
            author_lines = []
            for author, count in prs_by_author.items():
                author_lines.append(f"• *{author}*: {count} PR{'s' if count != 1 else ''}")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*PRs by Developer:*\n" + "\n".join(author_lines)
                }
            })

        # Add recent transactions if available
        if recent_transactions:
            blocks.append({
                "type": "divider"
            })

            txn_lines = []
            for txn in recent_transactions[:5]:  # Show top 5
                amount = txn.get("amount", 0)
                desc = txn.get("description", "Unknown")[:35]  # Truncate long descriptions
                date = txn.get("date", "")
                sign = "+" if amount > 0 else ""
                txn_lines.append(f"• `{date}` {desc}: {sign}${amount:,.2f}")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Recent Transactions (This Week):*\n" + "\n".join(txn_lines)
                }
            })

        # Add timestamp
        blocks.extend([
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
        ])

        return {"blocks": blocks}
    
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