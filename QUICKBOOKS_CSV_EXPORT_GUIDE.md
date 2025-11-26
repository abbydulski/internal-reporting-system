# QuickBooks CSV Export Guide

This guide shows you how to export real data from QuickBooks without using OAuth/API.

## Why Use CSV Export?

- ✅ No OAuth setup required
- ✅ No API tokens to manage
- ✅ Real data from your QuickBooks account
- ❌ Manual process (not automated)
- ❌ Need to re-export periodically for fresh data

## Step 1: Export Invoices from QuickBooks

### QuickBooks Online:

1. **Go to Reports**
   - Click "Reports" in the left menu
   - Search for "Invoice List" or "Sales by Customer Detail"

2. **Customize the Report**
   - Click "Customize"
   - Set date range (e.g., Last 90 days)
   - Make sure these columns are included:
     - Invoice Number
     - Customer Name
     - Invoice Date
     - Due Date
     - Total Amount
     - Balance
     - Status

3. **Export to Excel/CSV**
   - Click "Export" (top right)
   - Select "Export to Excel" or "Export to CSV"
   - Save as: `quickbooks_invoices.csv`
   - Move file to your project root directory

### QuickBooks Desktop:

1. **Go to Reports → Customers & Receivables → Invoice List**
2. **Customize Report**
   - Set date range
   - Include necessary columns
3. **Export**
   - Click "Excel" button
   - Save as CSV
   - Save as: `quickbooks_invoices.csv`

## Step 2: Export Payments from QuickBooks

### QuickBooks Online:

1. **Go to Reports**
   - Search for "Payment Method List" or "Deposit Detail"

2. **Customize the Report**
   - Set date range (e.g., Last 90 days)
   - Include columns:
     - Payment Number (or Transaction ID)
     - Customer Name
     - Payment Date
     - Amount
     - Payment Method

3. **Export to Excel/CSV**
   - Click "Export"
   - Save as: `quickbooks_payments.csv`
   - Move to project root directory

### QuickBooks Desktop:

1. **Go to Reports → Customers & Receivables → Customer Payment List**
2. **Customize and Export**
3. **Save as: `quickbooks_payments.csv`**

## Step 3: Format Your CSV Files

Your CSV files should have these columns:

### quickbooks_invoices.csv:
```csv
Invoice Number,Customer ID,Customer Name,Invoice Date,Due Date,Total Amount,Balance,Status
INV-001,CUST-001,Acme Corp,2024-01-15,2024-02-15,5000.00,0.00,Paid
INV-002,CUST-002,Tech Solutions,2024-01-20,2024-02-20,7500.00,7500.00,Unpaid
```

### quickbooks_payments.csv:
```csv
Payment Number,Customer ID,Customer Name,Payment Date,Amount,Payment Method
PMT-001,CUST-001,Acme Corp,2024-02-10,5000.00,Bank Transfer
PMT-002,CUST-003,Global Industries,2024-02-12,3000.00,Check
```

## Step 4: Place Files in Project Root

Move both CSV files to your project directory:

```
internal-reporting-system/
├── quickbooks_invoices.csv    ← Place here
├── quickbooks_payments.csv    ← Place here
├── etl/
├── tools/
└── ...
```

## Step 5: Run the Sync

```bash
python -m etl.scheduler sync
```

The system will:
1. ✅ Import invoices from `quickbooks_invoices.csv`
2. ✅ Import payments from `quickbooks_payments.csv`
3. ✅ Load data into Supabase
4. ✅ Generate reports

## Step 6: Update Regularly

To keep data fresh:

1. **Weekly/Monthly**: Re-export CSV files from QuickBooks
2. **Replace** the old CSV files with new ones
3. **Run sync** again: `python -m etl.scheduler sync`

## Alternative: Create a Template

If you export regularly, save your report customization in QuickBooks:

1. Customize the report once
2. Click "Save customization"
3. Name it (e.g., "ETL Export - Invoices")
4. Next time: Just open the saved report and export

## Troubleshooting

### "No invoices CSV file specified"
- Make sure `quickbooks_invoices.csv` is in the project root
- Check the filename matches exactly (case-sensitive)

### "Error importing invoices"
- Check CSV format matches the expected columns
- Make sure dates are in YYYY-MM-DD format
- Make sure amounts are numbers (no $ signs)

### Missing Columns
- Edit the CSV file to add missing columns
- Or modify `etl/extractors/quickbooks_csv_importer.py` to match your CSV format

## Comparison: CSV vs API

| Feature | CSV Export | OAuth API |
|---------|-----------|-----------|
| Setup Complexity | Easy | Complex |
| Real Data | ✅ Yes | ✅ Yes |
| Automated | ❌ Manual | ✅ Automatic |
| Real-time | ❌ No | ✅ Yes |
| Token Management | ✅ None | ❌ Refresh every 100 days |
| Best For | Small teams, infrequent updates | Large teams, daily syncs |

## Recommendation

**Start with CSV export** to get real data flowing, then decide if you need the API:
- If you only need weekly/monthly reports → CSV is fine
- If you need daily automated syncs → Set up OAuth API

---

Need help? Check the CSV files are formatted correctly or run with mock data first to test the pipeline.

