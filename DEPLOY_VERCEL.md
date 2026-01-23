# 🚀 Social Content Automation - Deployment Guide

## 📋 Project Overview

This project consists of two main components:
- **Frontend Dashboard**: Next.js app deployed on Vercel
- **Backend Processor**: Python script for video processing (needs cloud deployment)

## 🎯 Current Status

### ✅ Frontend (Dashboard)
- **Status**: Deployed and working on Vercel
- **URL**: https://content-automation-[hash].vercel.app
- **Features**:
  - Real-time monitoring of video processing
  - Displays processed videos with extracted titles
  - Shows processing status and statistics
  - Auto-refreshes every 60 seconds

### 🔄 Backend (Video Processor)
- **Status**: Working locally, needs cloud deployment
- **Location**: `execution/main.py`
- **Features**:
  - Monitors Google Drive folder for new videos
  - Processes videos with AI (transcription, subtitles, thumbnails)
  - Updates Google Sheets with results
  - Continuous polling every 60 seconds

## 🛠️ Backend Deployment Options

### Option 1: Railway (Recommended) ⭐

**Why Railway?**
- Python support out of the box
- Persistent file storage
- 24/7 uptime
- Easy GitHub integration
- Affordable ($5/month)

**Steps:**
1. Create account at [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables:
   ```
   OPENAI_API_KEY=your_key
   ANTHROPIC_API_KEY=your_key
   GOOGLE_DRIVE_FOLDER_ID_UPLOAD=your_folder_id
   GOOGLE_DRIVE_FOLDER_ID_FINAL=your_folder_id
   GOOGLE_SHEET_ID=your_sheet_id
   ```
4. Upload `service_account.json` to Railway
5. Set start command: `python execution/main.py`
6. Deploy

### Option 2: Render

**Steps:**
1. Create account at [Render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python execution/main.py`
6. Add environment variables
7. Upload service account JSON

### Option 3: DigitalOcean App Platform

**Steps:**
1. Create account at [DigitalOcean](https://digitalocean.com)
2. Create new App
3. Connect GitHub repo
4. Configure as Python app
5. Set environment variables
6. Deploy

## 📁 File Structure

```
Social content automation/
├── execution/                 # Python backend
│   ├── main.py               # Main processing script
│   └── services/             # Processing modules
├── frontend/                 # Next.js frontend
│   └── app/                  # Next.js app router
├── .env                      # Local environment variables
├── service_account.json      # Google service account
└── requirements.txt          # Python dependencies
```

## 🔐 Environment Variables

### Backend (.env)
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
GOOGLE_DRIVE_FOLDER_ID_UPLOAD=...
GOOGLE_DRIVE_FOLDER_ID_FINAL=...
GOOGLE_SHEET_ID=...
POLL_INTERVAL_SECONDS=60
```

### Frontend (Vercel)
```env
GOOGLE_SERVICE_ACCOUNT_JSON={...}
GOOGLE_SHEET_ID=...
```

## 🚀 Deployment Checklist

### Backend Deployment
- [ ] Choose cloud platform (Railway recommended)
- [ ] Set all environment variables
- [ ] Upload service_account.json
- [ ] Test video processing
- [ ] Verify Google Sheets updates

### Frontend Deployment
- [ ] Vercel project connected to GitHub
- [ ] Environment variables set
- [ ] Framework set to "Next.js"
- [ ] Root directory set to "frontend"
- [ ] Dashboard loads and shows data

## 🔍 Troubleshooting

### Backend Issues
- **"API key not found"**: Check .env file
- **"service_account.json not found"**: Upload to cloud platform
- **Google API errors**: Check service account permissions

### Frontend Issues
- **404 error**: Check Vercel framework settings
- **No data**: Ensure backend is running and updating sheets
- **Auth errors**: Check GOOGLE_SERVICE_ACCOUNT_JSON format

## 📊 Monitoring

- **Dashboard**: View processing status in real-time
- **Google Sheets**: Check "Content Engine" and "Backend Monitoring" tabs
- **Logs**: Check cloud platform logs for errors

## 💡 Next Steps

1. Deploy backend to Railway/Render
2. Test end-to-end video processing
3. Monitor dashboard for real-time updates
4. Optimize processing based on usage

---

**Need help?** Check the Vercel function logs and cloud platform logs for detailed error messages.