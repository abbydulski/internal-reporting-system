"""Quick test to verify Slack webhook works."""

from etl.config import Config
from etl.slack.slack_reporter import SlackReporter

def test_slack():
    reporter = SlackReporter(Config.SLACK_WEBHOOK_URL)
    reporter.send_test_message()

if __name__ == "__main__":
    test_slack()