# Video Content Automation System

An automated video processing pipeline that transcribes, enhances, and distributes video content across social media platforms.

## 🏗️ Architecture

This system uses a **separation of concerns** architecture:

### Backend (GitHub Actions)
- **Location**: `execution/` directory
- **Runtime**: GitHub Actions (scheduled every 15 minutes)
- **Purpose**: Process videos, generate content, upload to platforms
- **Language**: Python with FFmpeg

### Frontend (Vercel)
- **Location**: `dashboard/` directory
- **Runtime**: Vercel serverless functions
- **Purpose**: Monitor processing status, display analytics
- **Language**: Next.js (React/TypeScript)

### Data Flow
```
Google Drive → GitHub Actions → Processing → Google Drive + Sheets → Vercel Dashboard
```

## 🚀 Quick Start

### 1. Backend Setup (GitHub Actions)
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `GOOGLE_SERVICE_ACCOUNT_JSON`: Your service account JSON (as plain text)
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `GOOGLE_SHEET_ID`: Your Google Sheet ID
   - `GOOGLE_DRIVE_FOLDER_ID_UPLOAD`: Upload folder ID
   - `GOOGLE_DRIVE_FOLDER_ID_FINAL`: Final folder ID

### 2. Frontend Setup (Vercel)
1. Connect your GitHub repo to Vercel
2. Set environment variables (same as above)
3. Deploy - Vercel will automatically detect Next.js

### 3. Enable Automation
- GitHub Actions will run automatically every 15 minutes
- Or trigger manually from GitHub Actions tab

## 📁 Project Structure

```
├── .github/workflows/          # GitHub Actions workflows
├── dashboard/                  # Next.js frontend (Vercel)
│   ├── app/                    # Next.js app router
│   └── public/                 # Static assets
├── execution/                  # Python backend (GitHub Actions)
│   └── services/               # Processing modules
├── directives/                 # Processing instructions
├── .env                        # Local environment (NOT committed)
├── service_account.json        # Google credentials (NOT committed)
├── vercel.json                 # Vercel configuration
├── .vercelignore              # Vercel deployment exclusions
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

### Environment Variables

| Variable | Backend | Frontend | Description |
|----------|---------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | ❌ | OpenAI API access |
| `ANTHROPIC_API_KEY` | ✅ | ❌ | Anthropic API access |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ✅ | ✅ | Google service account |
| `GOOGLE_SHEET_ID` | ✅ | ✅ | Google Sheets ID |
| `GOOGLE_DRIVE_FOLDER_ID_UPLOAD` | ✅ | ❌ | Upload folder ID |
| `GOOGLE_DRIVE_FOLDER_ID_FINAL` | ✅ | ❌ | Final folder ID |

### Google Setup

1. **Create Service Account**: Google Cloud Console → IAM → Service Accounts
2. **Generate JSON Key**: Download the JSON file
3. **Share Google Sheet**: Give service account edit access
4. **Share Drive Folders**: Give service account access to upload/final folders

## 📊 Features

### Backend Processing
- ✅ Automatic video discovery from Google Drive
- ✅ AI-powered transcription (OpenAI Whisper)
- ✅ Content strategy generation
- ✅ Subtitle burning with FFmpeg
- ✅ Intro video creation for shorts
- ✅ Multi-platform optimization
- ✅ Google Sheets logging

### Frontend Dashboard
- ✅ Real-time processing status
- ✅ Video analytics and metrics
- ✅ Content strategy display
- ✅ Direct links to processed videos
- ✅ Platform distribution tracking

## 🔒 Security

- **No credentials in code**: All secrets stored in GitHub/Vercel
- **Service account isolation**: Limited Google API permissions
- **Automatic cleanup**: Credentials deleted after processing
- **Environment separation**: Backend/Frontend isolation

## 🚦 Monitoring

### GitHub Actions
- View runs in GitHub → Actions tab
- Check logs for processing details
- Manual trigger available for testing

### Vercel Dashboard
- Real-time status updates
- Processing metrics
- Error notifications

## 🛠️ Development

### Local Backend Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Add credentials to .env
# Add service_account.json

# Run processor
python execution/main.py
```

### Local Frontend Testing
```bash
cd dashboard
npm install
npm run dev
```

## 📚 Documentation

- [GitHub Actions Setup](SETUP_GITHUB_ACTIONS.md)
- [Vercel Deployment](DEPLOY_VERCEL.md)
- [Security Guide](SECURITY.md)
- [Troubleshooting](TROUBLESHOOTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.