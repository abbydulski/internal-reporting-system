# Real API Integration Guide

This guide explains how to switch from mock data to real API integrations for Mercury and QuickBooks.

## Current Status

- ✅ **QuickBooks**: Already using real API (sandbox mode)
- ✅ **GitHub**: Already using real API
- ❌ **Mercury**: Currently using mock data

## Step 1: Update Your `.env` File

Replace the placeholder Mercury API key with your real one:

```bash
# Mercury API (PRODUCTION - Real API)
MERCURY_API_KEY=your_actual_mercury_api_key_here
```

### How to Get Your Mercury API Key:
1. Log into Mercury: https://app.mercury.com
2. Go to Settings → API
3. Generate a new API key
4. Copy it to your `.env` file

## Step 2: Test Mercury API Connection

Before integrating, test that your API key works:

```bash
# Activate your virtual environment
source venv/bin/activate

# Run the Mercury test
python etl/extractors/mercury_extractor_REAL.py
```

This will:
- Connect to Mercury API
- Fetch your accounts
- Fetch recent transactions
- Display sample data

## Step 3: Switch to Real Mercury Extractor

Once the test passes, replace the mock extractor:

```bash
# Backup the mock version
mv etl/extractors/mercury_extractor.py etl/extractors/mercury_extractor_MOCK_BACKUP.py

# Use the real version
mv etl/extractors/mercury_extractor_REAL.py etl/extractors/mercury_extractor.py
```

Or manually update `etl/extractors/mercury_extractor.py` with the real implementation.

## Step 4: Test the Full Pipeline

Run a test sync to make sure everything works:

```bash
python -m etl.scheduler sync
```

This will:
1. Extract data from Mercury (REAL)
2. Extract data from QuickBooks (REAL - sandbox)
3. Extract data from GitHub (REAL)
4. Load everything into Supabase

## Step 5: Switch QuickBooks to Production (Optional)

Your QuickBooks is currently in **sandbox mode**. To use production data:

1. Update `etl/extractors/quickbooks_extractor.py` line 285:
   ```python
   is_sandbox=False  # Change from True to False
   ```

2. Make sure your QuickBooks credentials in `.env` are for production (not sandbox)

3. Test the connection:
   ```bash
   python etl/extractors/quickbooks_extractor.py
   ```

## Environment Variables Summary

Your `.env` should have:

```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Mercury (REAL API)
MERCURY_API_KEY=your_real_mercury_api_key

# QuickBooks (Sandbox or Production)
QUICKBOOKS_CLIENT_ID=your_client_id
QUICKBOOKS_CLIENT_SECRET=your_client_secret
QUICKBOOKS_REFRESH_TOKEN=your_refresh_token
QUICKBOOKS_REALM_ID=your_company_id

# GitHub (REAL API)
GITHUB_TOKEN=your_github_token
GITHUB_ORG=your_org_name

# Slack
SLACK_WEBHOOK_URL=your_slack_webhook

# Environment
ENVIRONMENT=production  # or development
```

## Testing Checklist

- [ ] Mercury API key is set in `.env`
- [ ] Mercury test script runs successfully
- [ ] Real Mercury extractor is in place
- [ ] Full sync runs without errors
- [ ] Data appears in Supabase
- [ ] Weekly report generates correctly
- [ ] QuickBooks switched to production (if desired)

## Troubleshooting

### Mercury API Errors

**401 Unauthorized**: Your API key is invalid or expired
- Regenerate the key in Mercury settings
- Make sure there are no extra spaces in `.env`

**403 Forbidden**: Your API key doesn't have the right permissions
- Check API key permissions in Mercury settings

**Rate Limiting**: Too many requests
- Mercury has rate limits; the code includes delays
- Consider caching data if you run syncs frequently

### QuickBooks API Errors

**Token Expired**: Refresh token needs renewal
- QuickBooks refresh tokens expire after 100 days
- Re-authenticate through QuickBooks OAuth flow

**Sandbox vs Production**: Wrong environment
- Make sure `is_sandbox` matches your credentials
- Sandbox and production use different company IDs

## Next Steps

Once real APIs are working:

1. **Schedule Regular Syncs**: Set up cron jobs or use a scheduler
   ```bash
   # Daily sync at 6 AM
   0 6 * * * cd /path/to/project && source venv/bin/activate && python -m etl.scheduler sync
   
   # Weekly report on Monday at 9 AM
   0 9 * * 1 cd /path/to/project && source venv/bin/activate && python -m etl.scheduler report
   ```

2. **Monitor Data Quality**: Check Supabase regularly for data accuracy

3. **Set Up Alerts**: Configure Slack notifications for errors

4. **Backup Strategy**: Export Supabase data regularly

## Support

- **Mercury API Docs**: https://docs.mercury.com/reference
- **QuickBooks API Docs**: https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/invoice
- **GitHub API Docs**: https://docs.github.com/en/rest

