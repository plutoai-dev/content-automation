# GitHub Actions Backend Setup

This guide walks you through setting up the automated video processing backend using GitHub Actions.

## 📋 Prerequisites

- GitHub repository with this code
- Google Cloud service account with Drive and Sheets API access
- OpenAI API key
- Anthropic API key
- Google Sheet and Drive folder IDs

## 🔐 Step 1: Create GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

### Required Secrets:

#### 1. GOOGLE_SERVICE_ACCOUNT_JSON
- **Name**: `GOOGLE_SERVICE_ACCOUNT_JSON`
- **Value**: Copy the entire JSON content from your Google service account key file
- **Important**: Paste as plain text, do not format as JSON

#### 2. OPENAI_API_KEY
- **Name**: `OPENAI_API_KEY`
- **Value**: Your OpenAI API key (starts with `sk-`)

#### 3. ANTHROPIC_API_KEY
- **Name**: `ANTHROPIC_API_KEY`
- **Value**: Your Anthropic API key

#### 4. GOOGLE_SHEET_ID
- **Name**: `GOOGLE_SHEET_ID`
- **Value**: Your Google Sheet ID (from the URL: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`)

#### 5. GOOGLE_DRIVE_FOLDER_ID_UPLOAD
- **Name**: `GOOGLE_DRIVE_FOLDER_ID_UPLOAD`
- **Value**: The Google Drive folder ID where videos are uploaded

#### 6. GOOGLE_DRIVE_FOLDER_ID_FINAL
- **Name**: `GOOGLE_DRIVE_FOLDER_ID_FINAL`
- **Value**: The Google Drive folder ID where processed videos are stored

## 🔍 Step 2: Find Your Google IDs

### Google Sheet ID
1. Open your Google Sheet
2. Copy the ID from the URL: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`
3. The Sheet ID is the long string between `/d/` and `/edit`

### Google Drive Folder IDs
1. Open your Google Drive folder
2. Copy the ID from the URL: `https://drive.google.com/drive/folders/[FOLDER_ID]`
3. The Folder ID is the long string after `/folders/`

## ⚙️ Step 3: Enable GitHub Actions

1. Go to your GitHub repository → **Actions** tab
2. You should see the "Video Content Processor" workflow
3. Click **"Enable workflows"** if prompted

## 🧪 Step 4: Test the Workflow

### Manual Trigger
1. Go to **Actions** → **Video Content Processor**
2. Click **"Run workflow"** → **"Run workflow"** button
3. This will trigger the workflow immediately for testing

### Check Results
1. Click on the running workflow
2. View the logs to see processing details
3. Check your Google Sheet for new entries
4. Check your Google Drive final folder for processed videos

## 📊 Step 5: Monitor Automated Runs

### View Scheduled Runs
- GitHub Actions runs automatically every 15 minutes
- Go to **Actions** tab to see all runs
- Green checkmark = success, red X = failure

### Read Logs
1. Click on any workflow run
2. Click **"process-videos"** job
3. View detailed logs for each step

### Common Log Messages
```
Starting Video Content Engine (GitHub Actions Edition)...
Tracking X already processed videos
Found X total files in upload folder
[X] Processing new file: video.mp4
✅ Success! Processed video.mp4
EXECUTION SUMMARY
Total files scanned: X
Successfully processed: X
```

## 🚨 Step 6: Handle Failures

### If Workflow Fails
1. Check the error logs in GitHub Actions
2. Common issues:
   - **Invalid credentials**: Check your secrets
   - **Missing permissions**: Verify service account access
   - **API limits**: Wait and retry
   - **Large files**: Videos over 100MB may fail

### Retry Failed Runs
1. Go to the failed run
2. Click **"Re-run jobs"** → **"Re-run failed jobs"**

## 🔧 Step 7: Customize Schedule (Optional)

To change the 15-minute schedule, edit `.github/workflows/video-processor.yml`:

```yaml
on:
  schedule:
    # Run every 15 minutes (change cron expression as needed)
    - cron: '*/15 * * * *'
```

Common cron expressions:
- `*/15 * * * *` = Every 15 minutes
- `*/30 * * * *` = Every 30 minutes
- `0 * * * *` = Every hour
- `0 */6 * * *` = Every 6 hours

## 📈 Step 8: Monitor Usage

### GitHub Actions Limits
- **Free tier**: 2,000 minutes/month
- **Paid tier**: $0.008/minute
- Each video processing run takes ~5-15 minutes

### Check Usage
1. Go to GitHub → **Settings** → **Billing & plans**
2. View **Actions** usage

## 🛠️ Troubleshooting

### Workflow Not Triggering
- Check that secrets are set correctly
- Verify repository has Actions enabled
- Check branch protection rules

### Authentication Errors
- Verify `GOOGLE_SERVICE_ACCOUNT_JSON` is valid JSON
- Check service account has correct permissions
- Ensure Google Sheet and Drive folders are shared

### Processing Errors
- Check video file formats (MP4 recommended)
- Verify FFmpeg installation in logs
- Check API key validity and credits

### Dashboard Not Updating
- Ensure Vercel has correct environment variables
- Check Google Sheet permissions for dashboard service account
- Verify sheet structure matches expected format

## 📞 Support

If you encounter issues:
1. Check the troubleshooting guide: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review GitHub Actions logs for error details
3. Verify all secrets and permissions are correct
4. Test with manual workflow trigger

## ✅ Success Checklist

- [ ] All 6 GitHub secrets created
- [ ] Workflow appears in Actions tab
- [ ] Manual trigger works
- [ ] Automated runs start every 15 minutes
- [ ] Videos are processed successfully
- [ ] Results appear in Google Sheet
- [ ] Processed videos upload to Drive
- [ ] Dashboard shows real-time data