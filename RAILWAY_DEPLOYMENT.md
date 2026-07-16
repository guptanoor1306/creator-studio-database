# Railway Deployment Guide

## 🚀 Quick Deploy to Railway

This guide will help you deploy the Creator Studio Data Exporter to Railway in minutes!

### Prerequisites

1. A Railway account (sign up at https://railway.app - free tier available)
2. GitHub account (recommended for automatic deployments)

---

## 📦 What's Already Configured

Your repository includes all necessary Railway configuration files:

- ✅ `Procfile` - Tells Railway how to run your app
- ✅ `railway.toml` - Railway configuration with auto-restart
- ✅ `runtime.txt` - Specifies Python 3.11
- ✅ `.railwayignore` - Excludes unnecessary files
- ✅ `requirements.txt` - All Python dependencies
- ✅ Token input in UI - No hardcoded credentials!

---

## 🎯 Deployment Options

### Option A: Deploy from GitHub (Recommended)

This enables automatic deployments when you push changes.

#### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Deploy Creator Studio Data Exporter"

# Create main branch
git branch -M main

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

#### Step 2: Deploy on Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Choose your repository
6. Railway will automatically:
   - Detect it's a Python app
   - Install dependencies from `requirements.txt`
   - Run the app using the `Procfile` command
   - Assign a public URL

#### Step 3: Get Your Public URL

1. Once deployed, click on your project
2. Go to **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Your app will be available at: `https://your-app-name.up.railway.app`

---

### Option B: Deploy from Railway CLI

Quick deployment directly from your terminal.

#### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

Or with Homebrew (macOS):
```bash
brew install railway
```

#### Step 2: Login and Deploy

```bash
# Login to Railway
railway login

# Link to a new project
railway init

# Deploy your app
railway up

# Open your deployed app
railway open
```

---

## 🔧 Environment Variables

Railway automatically sets the `PORT` variable. You can add optional variables for optimization and automation.

### For Automated Slack Notifications (Recommended)

For production automated notifications, set these variables to avoid storing credentials in config files:

**Variable Name**: `CS_BEARER_TOKEN`  
**Value**: Your Creator Studio bearer token  
**Purpose**: Authentication for automated data fetching

**Variable Name**: `SLACK_WEBHOOK_URL`  
**Value**: Your Slack webhook URL  
**Purpose**: Automated Slack notifications

**Variable Name**: `FLASK_ENV`  
**Value**: `production`  
**Purpose**: Optimization (optional)

**How to add:**
1. Go to your Railway project dashboard
2. Click on your service
3. Select **"Variables"** tab
4. Click **"New Variable"**
5. Add each variable with its value
6. Railway will automatically restart the service

**Important Notes:**
- Environment variables take priority over UI-configured values
- Credentials are encrypted and secure in Railway
- Update `CS_BEARER_TOKEN` when it expires (see ENV_SETUP.md)
- Manual operations through the UI still work without these variables

---

## 🔒 Security Features

### ✅ No Hardcoded Tokens!

The app has been updated to:
- **Remove hardcoded bearer tokens** from the codebase
- **Require users to enter their own token** via the UI
- **Store tokens only in browser session** (not persisted)

This makes it safe to:
- Deploy publicly on Railway
- Share the URL with team members
- Commit code to GitHub without exposing credentials

### How Users Get Their Token:

1. Visit Creator Studio: https://zero1creatorstudio.com
2. Open Developer Tools (F12 or Cmd+Option+I on Mac)
3. Go to **Network** tab
4. Refresh or navigate to any page
5. Find a request to `/api/user/videos` or similar
6. Look for **Authorization** header
7. Copy the token after `Bearer ` (starts with `eyJ...`)

---

## 📝 Using Your Deployed App

1. **Visit your Railway URL**: `https://your-app.up.railway.app`
2. **Paste Bearer Token**: Enter token in the authentication field
3. **Click "Load Channels"**: Fetches your channels from API
4. **Select Channels**: Choose which channels to export
5. **Configure Filters**: Set time frame, content type, outlier scores, etc.
6. **Export**: Download your Excel file with full data + transcripts!

---

## 🛠️ Troubleshooting

### Build Fails on Railway

**Check Railway logs:**
1. Go to your project dashboard
2. Click **"Deployments"**
3. Click on the failed deployment
4. View build logs

**Common fixes:**
- Ensure `requirements.txt` lists all dependencies
- Check Python version in `runtime.txt` (currently 3.11)
- Verify no syntax errors in code

### App Crashes After Deploy

**View runtime logs:**
```bash
railway logs
```

**Common issues:**
- Port binding: Railway sets `PORT` env var automatically
- Missing dependencies: Update `requirements.txt`
- Memory limits: Check Railway plan limits

### "Bearer token is required" Error

This is expected behavior! Users must:
1. Enter their Bearer token in the UI
2. Click "Load Channels" before exporting

### Slow Performance

For large exports (500+ videos with transcripts):
- Consider upgrading Railway plan for more resources
- Or advise users to filter by specific channels/shorter time frames

---

## 💰 Railway Pricing

- **Trial**: $5 credit (no credit card required)
- **Hobby Plan**: $5/month + usage-based pricing
  - 500 execution hours included
  - Perfect for this tool with moderate usage

**Estimated costs for this app:**
- Small usage (few exports/day): Free tier sufficient
- Medium usage (50+ exports/day): ~$5-10/month
- High usage: Scale as needed

---

## 🔄 Automatic Deployments

Once connected to GitHub, Railway will:
- ✅ Auto-deploy on every push to main branch
- ✅ Show deployment status
- ✅ Keep deployment history
- ✅ Allow instant rollbacks

---

## 🎉 Next Steps

1. Deploy to Railway using Option A or B above
2. Share your Railway URL with your team
3. Each user enters their own Bearer token
4. Start exporting data!

**Your app will be live at**: `https://[your-project-name].up.railway.app`

Need help? Check Railway docs: https://docs.railway.app
