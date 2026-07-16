# 📨 Slack Integration Guide

## Overview

The Creator Studio Data Exporter now includes **automatic Slack notifications** for outlier videos! This feature helps you stay on top of viral content by automatically detecting and sending high-performing videos to your Slack workspace.

---

## 🎯 What It Does

**Automatically detects and sends to Slack:**
- **Long-form videos** with:
  - Outlier score ≥ 2.0x OR
  - Views ≥ 500,000
  
- **Short-form videos** with:
  - Outlier score ≥ 2.0x OR
  - Views ≥ 100,000

**Filters:**
- Indian niche categories (optional)
- Recent videos from last 3-30 days
- Sorted by outlier score (top 20 sent)

---

## 🚀 Setup Instructions

### Step 1: Create Slack Webhook

1. **Go to Slack Workspace Settings**
   - Click on your workspace name → Settings & administration → Manage apps

2. **Find Incoming Webhooks**
   - Search for "Incoming Webhooks"
   - Click "Add to Slack"

3. **Configure Webhook**
   - Choose a channel (e.g., `#outlier-videos`, `#content-alerts`)
   - Click "Add Incoming Webhooks integration"

4. **Copy Webhook URL**
   - You'll get a URL like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`
   - **Keep this private!** It's like a password to your Slack

### Step 2: Use in the Tool

1. **Open the tool**: http://localhost:8080
2. **Enter credentials**:
   - Bearer Token (from Creator Studio)
   - Slack Webhook URL (from step 1)
3. **Configure settings**:
   - Days back: 3, 7, 14, or 30 days
   - Filter: Indian Niche Only or All Categories
4. **Click**: "📨 Find & Send Outliers to Slack"

---

## 📊 What Gets Sent to Slack

### Message Format

Each Slack message includes:

**Header:**
- 🔥 Title: "Outlier Videos Alert - Last X Days"
- Total count of outliers found
- Breakdown: Long-form vs Shorts

**For each video (top 10):**
- 📺 Video title (truncated to 100 chars)
- 📺 Channel name
- 👁️ View count (formatted: 1.2M, 500K, etc.)
- 🔥 Outlier score (e.g., 3.5x)
- 🎬 Type: Long-form or Short
- 📅 Published date
- 🔗 Direct YouTube link
- 🖼️ Thumbnail image

### Example Slack Message

```
🔥 Outlier Videos Alert - Last 7 Days
Found 15 outlier videos in Indian niche
Long-form: 10 | Shorts: 5
---

1. How I Made $10M in 30 Days | Full Business Breakdown
📺 Think School | 👁️ 2,400,000 views | 🔥 4.2x outlier
🎬 Long-form | 📅 2026-07-14
[Watch on YouTube]

2. India's Secret to Success Revealed
📺 Varun Mayya | 👁️ 850,000 views | 🔥 3.8x outlier
🎬 Long-form | 📅 2026-07-13
[Watch on YouTube]

... (up to 10 videos shown)
```

---

## 🔧 Configuration Options

### Days Back
- **3 days**: Most recent, highly viral content
- **7 days** (recommended): Good balance of recency and coverage
- **14 days**: Broader coverage
- **30 days**: Comprehensive monthly overview

### Filter Options
- **Indian Niche Only**: Filters for Indian finance channels
  - Checks if "indian" or "india" appears in category or channel name
  - Best for focused regional insights

- **All Categories**: Global coverage
  - Includes all channels regardless of niche
  - Good for broader market trends

---

## 💡 Use Cases

### Daily Morning Briefing
**Setup:**
- Days back: 1-3 days
- Filter: Indian Niche Only
- Run every morning at 9 AM

**Result:** Get fresh outliers from yesterday

### Weekly Team Review
**Setup:**
- Days back: 7 days
- Filter: Indian Niche Only
- Run every Monday

**Result:** Comprehensive weekly performance review

### Monthly Trend Analysis
**Setup:**
- Days back: 30 days
- Filter: All Categories
- Run first of every month

**Result:** Identify long-term patterns and trends

---

## 🎨 Customization

Want to customize the criteria? Edit these values in `app.py`:

```python
# Long-form thresholds (line ~560)
if outlier_score >= 2.0 or views >= 500000:

# Short-form thresholds (line ~580)
if outlier_score >= 2.0 or views >= 100000:

# Number of videos to send (line ~595)
all_outliers = sorted(...)[:20]  # Change 20 to your desired number
```

---

## 🔒 Security Best Practices

### Protect Your Webhook URL
- ✅ Never commit webhook URL to git
- ✅ Don't share it in public channels
- ✅ Treat it like a password
- ✅ If leaked, regenerate it in Slack settings

### Where to Store Webhook
- **For personal use**: Enter manually each time
- **For team use**: Use environment variables
- **For automation**: Store in secure key vault

---

## 🤖 Automation Options

### Option 1: Manual (Current)
- Run from UI whenever you want
- Full control over timing
- Good for ad-hoc checks

### Option 2: Scheduled Task (Coming Soon)
Want automatic daily/weekly notifications? Add to `app.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=send_daily_outliers,
    trigger="cron",
    hour=9,  # 9 AM daily
    minute=0
)
scheduler.start()
```

### Option 3: Railway Cron (For Deployed Apps)
If deployed on Railway, use Railway's cron jobs:
- Create `/api/cron/daily-slack` endpoint
- Add authentication
- Schedule via Railway dashboard

---

## 🐛 Troubleshooting

### "Slack webhook returned status 404"
**Cause:** Invalid webhook URL
**Fix:** Check that URL starts with `https://hooks.slack.com/services/`

### "No outliers found matching criteria"
**Cause:** No videos meet the threshold
**Fix:** 
- Increase days back (try 14 or 30)
- Lower outlier criteria in code
- Try "All Categories" instead of "Indian Niche Only"

### "Bearer token is required"
**Cause:** Token not entered
**Fix:** Enter your Creator Studio bearer token first

### Slack message not formatted correctly
**Cause:** Missing video data
**Fix:** Check that API is returning complete video objects

---

## 📈 Next Steps

### Enhancement Ideas
1. **Custom thresholds per niche**
   - Different criteria for finance vs entertainment
   
2. **Trend detection**
   - Alert on sudden spikes in performance
   
3. **Competitive analysis**
   - Compare your channels vs competitors
   
4. **Multi-channel Slack**
   - Send to different channels based on category

5. **Rich formatting**
   - Add engagement rate charts
   - Include historical comparison

---

## 🎉 Quick Start

1. Get Slack webhook from workspace settings
2. Enter Bearer token + Slack webhook in UI
3. Select "Last 7 days" + "Indian Niche Only"
4. Click "📨 Find & Send Outliers to Slack"
5. Check your Slack channel!

**That's it! You'll now get outlier video alerts in Slack! 🚀**
