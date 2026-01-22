# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Video Content Automation system.

## 🔍 Quick Diagnosis

### Check System Status
1. **GitHub Actions**: Go to Actions tab → Check latest workflow run
2. **Vercel Dashboard**: Check deployment status and function logs
3. **Google Sheet**: Verify data is being written
4. **Google Drive**: Check if processed videos are uploaded

## 🚨 Common Issues & Solutions

## Backend (GitHub Actions) Issues

### ❌ Workflow Not Running
**Symptoms**: No automated processing, manual trigger doesn't work

**Solutions**:
1. Check GitHub Actions secrets are set correctly
2. Verify workflow file exists: `.github/workflows/video-processor.yml`
3. Check repository has Actions enabled
4. Review workflow syntax for errors

### ❌ Authentication Failures
**Symptoms**: "Service account authentication failed" in logs

**Solutions**:
1. Verify `GOOGLE_SERVICE_ACCOUNT_JSON` secret is valid JSON
2. Check service account has Drive and Sheets API enabled
3. Ensure service account has access to specified folders/sheet
4. Try regenerating service account key

### ❌ No Videos Found
**Symptoms**: "Found 0 total files" in logs

**Solutions**:
1. Check `GOOGLE_DRIVE_FOLDER_ID_UPLOAD` points to correct folder
2. Verify service account has read access to upload folder
3. Ensure videos are in the root of the folder (not subfolders)
4. Check video file formats (MP4 recommended)

### ❌ Processing Errors
**Symptoms**: Videos start processing but fail

**Common Causes**:
- **FFmpeg issues**: Check FFmpeg installation in logs
- **API limits**: OpenAI/Anthropic rate limits reached
- **Large files**: Videos over 100MB may timeout
- **Corrupt files**: Try with different video file

### ❌ Upload Failures
**Symptoms**: Processing succeeds but upload fails

**Solutions**:
1. Check `GOOGLE_DRIVE_FOLDER_ID_FINAL` is correct
2. Verify service account has write access to final folder
3. Check available storage space
4. Review file size limits

## Frontend (Vercel) Issues

### ❌ 404 Page Not Found
**Symptoms**: Vercel shows 404 error

**Solutions**:
1. **Check Root Directory**: In Vercel dashboard → Project Settings → Set "Root Directory" to `dashboard`
2. **Framework Preset**: Must be `Next.js`
3. **Build Success**: Check Vercel deployment logs
4. **vercel.json**: Should NOT contain `rootDirectory` property (set in dashboard instead)

### ❌ No Data Loading
**Symptoms**: Dashboard loads but shows no data

**Solutions**:
1. Check Vercel environment variables are set
2. Verify `GOOGLE_SERVICE_ACCOUNT_JSON` is valid
3. Ensure service account has read access to Google Sheet
4. Check `GOOGLE_SHEET_ID` matches backend

### ❌ Authentication Errors
**Symptoms**: "Requested entity was not found" in Vercel logs

**Solutions**:
1. Verify Sheet ID is correct
2. Check service account permissions
3. Ensure Sheet is shared with service account email
4. Try regenerating service account credentials

## 🔧 Testing & Validation

### Test GitHub Actions Locally
```bash
# Create test .env file
cp .env.example .env
# Fill with test credentials

# Run locally
python execution/main.py
```

### Test Vercel Functions
1. Go to Vercel → Functions tab
2. Check API route logs
3. Test with browser: `https://your-domain.vercel.app/api/data`

### Validate Google Services
```bash
# Test service account access
python -c "
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_info(
    json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'))
)
print('Service account authenticated successfully')
"
```

## 📊 Monitoring & Logs

### GitHub Actions Logs
- Go to GitHub → Actions → Workflow run
- Click job name to see detailed logs
- Look for error messages and stack traces

### Vercel Logs
- Go to Vercel → Functions tab
- Click on function to see invocation logs
- Check for API errors and authentication issues

### Google Cloud Logs
- Go to Google Cloud Console → APIs & Services → Logs
- Filter by service account email
- Check for permission errors

## 🔄 Recovery Procedures

### Reset Processed Videos
If videos are stuck in "processed" state:
1. Go to Google Sheets → "Content Engine" tab
2. Find the video entry
3. Delete the row or clear the processed status
4. GitHub Actions will retry on next run

### Clear Temporary Files
If disk space issues:
```bash
# In GitHub Actions runner
rm -rf temp_* Final_* *.mp4 *.png
```

### Restart Services
- **GitHub Actions**: Manual trigger or wait for schedule
- **Vercel**: Redeploy from dashboard
- **Google Services**: Usually self-healing

## 🚨 Emergency Stop

### Stop GitHub Actions
1. Go to GitHub → Actions → Workflows
2. Click "Video Content Processor"
3. Click "..." → "Disable workflow"

### Stop Vercel
1. Go to Vercel → Project Settings
2. Temporarily change environment variables to invalid values
3. Or pause the project

## 📞 Getting Help

### Check Documentation
- [README.md](README.md) - Architecture overview
- [SETUP_GITHUB_ACTIONS.md](SETUP_GITHUB_ACTIONS.md) - Backend setup
- [DEPLOY_VERCEL.md](DEPLOY_VERCEL.md) - Frontend deployment
- [SECURITY.md](SECURITY.md) - Security best practices

### Debug Checklist
- [ ] GitHub secrets configured correctly
- [ ] Vercel environment variables set
- [ ] Service account has proper permissions
- [ ] Google Sheet and Drive folders exist
- [ ] IDs match between systems
- [ ] No typos in configuration
- [ ] Dependencies installed correctly

### Common Error Messages

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| `Service account authentication failed` | Invalid JSON or permissions | Check service account setup |
| `Requested entity was not found` | Wrong Sheet/Folder ID | Verify IDs in Google URLs |
| `API rate limit exceeded` | Too many requests | Wait and retry, check usage |
| `FFmpeg not found` | Installation failed | Check GitHub Actions setup |
| `Build failed` | Dependency issues | Check Node.js/Python versions |

### Performance Issues
- **Slow processing**: Check video file sizes
- **Timeouts**: Reduce batch size or increase timeout
- **High costs**: Monitor API usage and optimize calls

## 🔧 Advanced Troubleshooting

### Debug API Calls
Add logging to see what's happening:
```python
# In execution/main.py
print(f"DEBUG: Found {len(files)} files")
print(f"DEBUG: Processed IDs: {processed_ids}")
```

### Test Individual Components
```bash
# Test Google Drive access
python -c "
from execution.services.drive import DriveService
drive = DriveService()
files = drive.list_files(os.getenv('GOOGLE_DRIVE_FOLDER_ID_UPLOAD'))
print(f'Found {len(files)} files')
"
```

### Check Environment Variables
```bash
# In GitHub Actions or locally
echo $GOOGLE_SHEET_ID
echo $OPENAI_API_KEY  # Should be masked
```

## 📈 Preventive Maintenance

### Regular Checks
- [ ] Monitor GitHub Actions usage (free tier: 2000 min/month)
- [ ] Check Vercel function logs weekly
- [ ] Review Google API usage monthly
- [ ] Update dependencies quarterly
- [ ] Rotate service account keys every 90 days

### Performance Monitoring
- Track average processing time per video
- Monitor API costs and usage
- Check for failed workflows
- Review error patterns

## 🎯 Success Metrics

**System is working correctly when:**
- ✅ GitHub Actions runs every 15 minutes
- ✅ New videos are detected and processed
- ✅ Results appear in Google Sheet within 30 minutes
- ✅ Dashboard shows real-time data
- ✅ No errors in logs
- ✅ Costs stay within budget

**If any of these fail, refer to the appropriate troubleshooting section above.**