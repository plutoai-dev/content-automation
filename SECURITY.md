# Security Best Practices

This document outlines security measures and best practices for the Video Content Automation system.

## 🔐 Credential Management

### GitHub Secrets (Backend)
**Location**: GitHub Repository → Settings → Secrets and variables → Actions

**Required Secrets**:
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Full service account JSON as plain text
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GOOGLE_SHEET_ID`: Google Sheet ID
- `GOOGLE_DRIVE_FOLDER_ID_UPLOAD`: Upload folder ID
- `GOOGLE_DRIVE_FOLDER_ID_FINAL`: Final folder ID

### Vercel Environment Variables (Frontend)
**Location**: Vercel Dashboard → Project Settings → Environment Variables

**Required Variables**:
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Same service account JSON
- `GOOGLE_SHEET_ID`: Same Sheet ID

## 🛡️ Service Account Security

### Google Cloud Setup
1. **Create dedicated service account** for this project only
2. **Enable minimal required APIs**:
   - Google Drive API
   - Google Sheets API
3. **Grant minimal permissions**:
   - Drive: Read/write access to specific folders only
   - Sheets: Read/write access to specific sheet only

### Access Control
- **Never share service account JSON** outside secure systems
- **Rotate keys regularly** (Google recommends every 90 days)
- **Monitor service account usage** in Google Cloud Console

## 📁 File System Security

### .gitignore Rules
```
# Environment and Credentials
.env
.env*.local
service_account.json

# Temporary Files
temp_*
Final_*
*.mp4
*.mp3
*.png
```

**Critical**: Never commit credential files to version control.

### Local Development
- Use `.env` files for local development
- Never commit `.env` files
- Use different credentials for development/production

## 🔄 Runtime Security

### GitHub Actions
- **Credentials created at runtime** from encrypted secrets
- **Automatic cleanup** after workflow completion
- **No credential persistence** between runs
- **Isolated execution environment**

### Vercel Deployment
- **Environment variables** encrypted at rest
- **Runtime-only access** to credentials
- **No credential exposure** in client-side code

## 🚨 Security Monitoring

### GitHub Security
- **Dependabot**: Automatic dependency updates
- **Code scanning**: Automated security analysis
- **Secret scanning**: Detects leaked credentials

### Google Cloud Monitoring
- **Audit logs**: Monitor service account activity
- **Access patterns**: Review unusual access
- **Permission changes**: Alert on permission modifications

## 🛠️ Incident Response

### Credential Compromise
1. **Immediately revoke** compromised credentials
2. **Generate new keys** for service accounts
3. **Update all systems** with new credentials
4. **Audit access logs** for unauthorized activity

### Data Breach
1. **Assess impact** of exposed data
2. **Notify affected parties** if necessary
3. **Rotate all credentials**
4. **Review access controls**

## 📊 API Security

### OpenAI/Anthropic
- **API key rotation**: Regular key cycling
- **Usage monitoring**: Track API consumption
- **Rate limiting**: Respect API limits
- **Cost monitoring**: Alert on unusual spending

### Google APIs
- **Scoped access**: Minimal required permissions
- **Request monitoring**: Log all API calls
- **Quota management**: Stay within limits
- **Error handling**: Secure failure responses

## 🔧 Development Security

### Code Practices
- **Input validation**: Sanitize all inputs
- **Error handling**: Don't expose sensitive information in errors
- **Logging**: Never log credentials or sensitive data
- **Dependency management**: Keep dependencies updated

### Testing
- **Separate test environments** with test credentials
- **Mock external services** in unit tests
- **Never use production credentials** in tests

## 📋 Security Checklist

### Initial Setup
- [ ] Service account created with minimal permissions
- [ ] APIs enabled in Google Cloud
- [ ] Resources shared with service account
- [ ] GitHub secrets configured
- [ ] Vercel environment variables set
- [ ] .gitignore properly configured

### Ongoing Maintenance
- [ ] Credentials rotated every 90 days
- [ ] Dependencies updated regularly
- [ ] Security scans run weekly
- [ ] Access logs reviewed monthly
- [ ] API usage monitored continuously

### Incident Prevention
- [ ] No credentials in code or logs
- [ ] Secure credential transmission
- [ ] Minimal permission principle followed
- [ ] Regular security audits performed

## 📞 Security Contacts

- **Google Cloud Security**: [Google Cloud Security Center](https://cloud.google.com/security)
- **GitHub Security**: [GitHub Security Lab](https://securitylab.github.com/)
- **Vercel Security**: [Vercel Security](https://vercel.com/security)

## 🚨 Emergency Procedures

**If you suspect a security breach:**
1. **Stop all systems** immediately
2. **Revoke all credentials** and generate new ones
3. **Change all API keys**
4. **Audit all access logs**
5. **Contact security team** if applicable

**Remember**: Security is everyone's responsibility. Always err on the side of caution with credentials and access controls.