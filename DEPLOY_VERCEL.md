# Vercel Dashboard Deployment

This guide walks you through deploying the dashboard frontend to Vercel.

## 📋 Prerequisites

- GitHub repository connected to Vercel
- Google service account with Sheets read access
- Google Sheet ID

## 🚀 Step 1: Connect Repository to Vercel

### Option A: Automatic (Recommended)
1. Push your code to GitHub
2. Vercel will detect the deployment automatically if connected

### Option B: Manual Setup
1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect Next.js settings

## ⚙️ Step 2: Configure Build Settings

Vercel should automatically detect these settings, but verify:

### Build Settings
Vercel will auto-detect Next.js in the root directory:
- **Framework Preset**: `Next.js` (auto-detected)
- **Root Directory**: `/` (root directory)
- **Build Command**: `npm run build` (automatic)
- **Install Command**: `npm install` (automatic)

### Environment Variables
Add these in Vercel → Project Settings → Environment Variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Your service account JSON | Production |
| `GOOGLE_SHEET_ID` | Your Google Sheet ID | Production |

**Important**: Set environment to "Production" for live deployment.

## 🔐 Step 3: Google Sheets Access

### Service Account Setup
1. **Same service account** as GitHub Actions
2. **Sheets API access** enabled in Google Cloud
3. **Read-only access** to your Google Sheet

### Share Google Sheet
1. Open your Google Sheet
2. Click **Share**
3. Add the service account email: `your-service-account@your-project.iam.gserviceaccount.com`
4. Give **"Viewer"** permissions

## 🚀 Step 4: Deploy

### Automatic Deployment
- Vercel deploys automatically when you push to main branch
- Check deployment status in Vercel dashboard

### Manual Deployment
1. Go to Vercel project dashboard
2. Click **"Deployments"** tab
3. Click **"Redeploy"** for latest commit

## 📊 Step 5: Verify Deployment

### Check Live Site
1. Visit your Vercel domain (e.g., `your-project.vercel.app`)
2. You should see the dashboard loading
3. Data should appear from your Google Sheet

### Common Issues
- **404 Error**: Check Root Directory is set to `dashboard`
- **No Data**: Check environment variables and Sheet permissions
- **Auth Errors**: Verify service account JSON format

## 🔧 Step 6: Custom Domain (Optional)

### Add Custom Domain
1. Go to Vercel → Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### SSL Certificate
- Vercel provides automatic SSL certificates
- HTTPS enabled by default

## 📊 Step 7: Monitor Dashboard

### Vercel Analytics
- View in Vercel → Project → Analytics
- Monitor traffic, performance, errors

### Function Logs
- Go to **Functions** tab in Vercel
- View API call logs
- Debug authentication issues

## 🛠️ Step 8: Update Environment Variables

### Change Variables
1. Go to Vercel → Project Settings → Environment Variables
2. Update values as needed
3. **Redeploy** to apply changes

### Test Changes
1. Use **Preview Deployments** for testing
2. Create pull requests to test changes safely

## 🚨 Step 9: Troubleshooting

### Dashboard Not Loading
```
Error: 404 NOT_FOUND
```
- Check Root Directory setting
- Verify Next.js build succeeded
- Check Vercel function logs

### No Data Appearing
```
Console: Failed to fetch data
```
- Check environment variables
- Verify service account permissions
- Check Google Sheet ID

### Authentication Errors
```
Error: Requested entity was not found
```
- Verify service account JSON format
- Check Google Sheet sharing permissions
- Confirm Sheet ID is correct

### Build Failures
- Check Vercel build logs
- Verify Node.js version compatibility
- Check for missing dependencies

## 📈 Step 10: Performance Optimization

### Vercel Features
- **Edge Functions**: Automatic for better performance
- **Image Optimization**: Built-in Next.js feature
- **Caching**: Automatic static asset caching

### Monitor Usage
- **Free Tier**: 100GB bandwidth, 100GB hours
- **Paid Tier**: Additional resources available
- Check usage in Vercel → Project → Usage

## 🔄 Step 11: Update Deployment

### Automatic Updates
- Vercel redeploys on every push to main branch
- Preview deployments for pull requests

### Manual Updates
1. Push code changes to GitHub
2. Vercel detects changes automatically
3. Monitor deployment progress

## 📞 Support

### Vercel Support
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)

### Common Issues
- Check [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- Review Vercel function logs
- Verify Google service account setup

## ✅ Success Checklist

- [ ] Repository connected to Vercel
- [ ] Root Directory set to `dashboard`
- [ ] Environment variables configured
- [ ] Google Sheet shared with service account
- [ ] Deployment successful (green checkmark)
- [ ] Dashboard loads with data
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Monitoring and logs working