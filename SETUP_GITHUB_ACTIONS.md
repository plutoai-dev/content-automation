# 🚀 Setting Up GitHub Actions for Video Processing

This guide will help you configure automated video processing using GitHub Actions.

## 📋 Prerequisites

- ✅ Google Cloud Project with Drive and Sheets APIs enabled
- ✅ Service Account with appropriate permissions
- ✅ Vercel dashboard deployed
- ✅ GitHub repository with this codebase

## 🔐 Step 1: Add GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

### Required Secrets:

#### 1. `GOOGLE_SERVICE_ACCOUNT_JSON`
- **Value**: Your complete service account JSON (as one line)
- **How to get it**:
  1. Go to Google Cloud Console
  2. IAM & Admin → Service Accounts
  3. Select your service account
  4. Keys → Add Key → JSON
  5. Copy the entire JSON content
  6. Paste as a single line in GitHub Secret

#### 2. `GOOGLE_SHEET_ID`
- **Value**: Your Google Sheet ID
- **How to find it**: In the Google Sheets URL: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`

#### 3. `GOOGLE_DRIVE_FOLDER_ID_UPLOAD`
- **Value**: Google Drive folder ID for input videos
- **How to find it**: In Drive URL: `https://drive.google.com/drive/folders/[FOLDER_ID]`

#### 4. `GOOGLE_DRIVE_FOLDER_ID_FINAL`
- **Value**: Google Drive folder ID for processed videos
- **How to find it**: Same as above

#### 5. `OPENAI_API_KEY`
- **Value**: Your OpenAI API key
- **How to get it**: OpenAI Platform → API Keys

#### 6. `ANTHROPIC_API_KEY`
- **Value**: Your Anthropic API key
- **How to get it**: Anthropic Console → API Keys

## ⚙️ Step 2: Enable GitHub Actions

1. Go to your repository → **Actions** tab
2. You should see the "Video Content Processor" workflow
3. Click **"I understand my workflows, go ahead and enable them"**

## 🧪 Step 3: Test the Workflow

### Manual Test Run:
1. Go to **Actions** → **Video Content Processor**
2. Click **"Run workflow"** (dropdown on the right)
3. Optionally change **max_videos** (default: 5)
4. Click **"Run workflow"**

### Monitor the Run:
1. Click on the running workflow
2. Watch the **build logs** in real-time
3. Check for any errors

## 📊 Step 4: Verify Everything Works

### Check Google Sheets:
- New videos should be logged in "Content Engine" tab
- Status updates should appear in "Backend Monitoring" tab

### Check Google Drive:
- Processed videos should appear in your final folder
- Videos should have subtitles and effects applied

### Check Vercel Dashboard:
- Dashboard should show updated statistics
- New videos should appear in the activity feed

## 🔍 Monitoring & Troubleshooting

### View Workflow Runs:
- Repository → **Actions** → **Video Content Processor**
- Click on any run to see detailed logs

### Common Issues:

#### ❌ "service_account.json not found"
- Check that `GOOGLE_SERVICE_ACCOUNT_JSON` secret is set correctly
- Ensure the JSON is valid (no extra characters)

#### ❌ "API key not found"
- Verify all API key secrets are set
- Check for typos in secret names

#### ❌ "Permission denied"
- Ensure service account has access to:
  - Google Drive folders
  - Google Sheets document

#### ❌ "Timeout"
- Videos might be too long - check `MAX_VIDEOS_PER_RUN`
- Processing might take too long - check video sizes

### Debug Tips:
1. **Manual runs**: Use workflow dispatch to test with different settings
2. **Logs**: Check the detailed logs for each step
3. **Environment**: Test locally first with the same environment variables

## ⏰ Schedule

The workflow runs automatically every 15 minutes, but you can:
- **Change the schedule**: Edit `.github/workflows/video-processor.yml`
- **Manual runs**: Use the workflow dispatch feature
- **Disable**: Turn off scheduled runs if needed

## 💰 Cost Monitoring

- **GitHub Actions**: 2000 minutes free/month
- **Each run**: ~5-15 minutes depending on video count
- **Monitor usage**: Repository → Settings → Billing

## 🆘 Need Help?

1. Check the **Actions** tab for error logs
2. Verify all **secrets** are set correctly
3. Test with **manual workflow runs**
4. Check **Google Cloud Console** for API access
5. Review **Vercel dashboard** for frontend issues

## ✅ Success Checklist

- [ ] All GitHub Secrets configured
- [ ] Workflow enabled
- [ ] Manual test run successful
- [ ] Videos processed and uploaded
- [ ] Google Sheets updated
- [ ] Vercel dashboard shows data
- [ ] Automatic runs working

**Congratulations!** Your automated video processing system is now live! 🎉