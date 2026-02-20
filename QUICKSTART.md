# ⚡ Quick Start Guide - 3 Steps to Your First Export

## Step 1: Install (30 seconds)

Open Terminal and run:

```bash
cd /Users/noorgupta/Downloads/Cursor/csdb
pip install -r requirements.txt
```

**What this does**: Installs the required Python libraries (requests, pandas, openpyxl)

---

## Step 2: Get Your Bearer Token (1 minute)

1. Open https://zero1creatorstudio.com in your browser
2. Press **F12** (or right-click → Inspect)
3. Go to **Network** tab
4. Refresh the page or click on "Videos"
5. Find a request to `api/user/videos`
6. Click on it → **Headers** tab
7. Find **Authorization** header
8. Copy everything after "Bearer " (the long string starting with `eyJ...`)

**Example**:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOi...
       ↑
       Copy this entire part (without "Bearer ")
```

---

## Step 3: Run the Script (10 seconds)

### Option A: Use the Interactive Script

1. Open `quick_export.py` in a text editor
2. Replace line 9 with your Bearer token:
   ```python
   BEARER_TOKEN = "eyJhbGciOiJI..."  # Paste your token here
   ```
3. Save and run:
   ```bash
   python quick_export.py
   ```
4. Choose option 1 for "Last 7 days"
5. Wait for it to complete
6. Find your Excel file in the same folder!

### Option B: Use Python Directly

Create a new file `my_export.py`:

```python
from cs_data_exporter import CSDataExporter

# Paste your Bearer token here
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Create exporter
exporter = CSDataExporter(TOKEN)

# Export last 7 days (includes transcripts automatically!)
exporter.quick_export_last_n_days(days=7)
```

Run it:
```bash
python my_export.py
```

---

## 🎉 That's It!

You should now have an Excel file with:
- ✅ All videos from the last 7 days
- ✅ Full transcripts for each video
- ✅ Views, likes, comments, outlier scores
- ✅ Summaries and statistics

---

## 📊 What You'll Get

Your Excel file will have these sheets:

### 1. Videos Sheet
All your video data in rows:
- Video ID, Title, Channel Name
- Views, Likes, Comments
- Outlier Score
- **Full Transcript Text**
- **Transcript Language**
- Description, Tags
- YouTube URL

### 2. Summary Sheet
Quick stats:
- Total videos
- Date range
- Total views/likes/comments
- Average views per video

---

## 🚀 Next Steps

### Export Last 30 Days
```python
exporter.quick_export_last_n_days(days=30)
```

### Export Specific Date Range
```python
videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19"
)
exporter.export_to_excel(videos, filename="my_export.xlsx")
```

### Export Specific Channels Only
```python
videos = exporter.fetch_videos(
    start_date="2026-01-01",
    end_date="2026-01-19",
    channel_ids=[
        "UCqW8jxh4tH1Z1sWPbkGWL4g",
        "UCBqvATpjSubtNxpqUDj4_cA"
    ]
)
exporter.export_to_excel(videos, filename="my_channels.xlsx")
```

### Fast Export (Without Transcripts)
```python
videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19",
    include_transcripts=False  # Much faster!
)
exporter.export_to_excel(videos)
```

---

## ⏱️ How Long Will It Take?

- **10 videos**: ~5 seconds
- **50 videos**: ~18 seconds
- **100 videos**: ~35 seconds
- **500 videos**: ~2.5 minutes

**Why?** The script fetches transcripts for each video individually (about 0.3s per video).

---

## 🔧 Troubleshooting

### "Authentication Error"
→ Your Bearer token expired. Get a new one from the browser.

### "No videos found"
→ Check your date range. Try a wider range or remove channel filters.

### "Connection timeout"
→ Check your internet. Try again in a few minutes.

### Script is slow
→ It's fetching transcripts! This is normal. To speed up, use `include_transcripts=False`.

---

## 📚 More Help

- See `README.md` for complete documentation
- See `WORKFLOW.md` to understand how it works
- See `example.py` for more code examples
- See `transcript_example.py` for transcript-specific examples

---

## 🎯 Common Use Cases

### Weekly Report for Your Boss
```python
# Every Monday, export last week's data
exporter.quick_export_last_n_days(days=7, filename="weekly_report.xlsx")
```

### Monthly Analysis
```python
# Export entire month
exporter.quick_export_last_n_days(days=30, filename="monthly_analysis.xlsx")
```

### Find Viral Videos
```python
# Export with outlier_score sorting (default)
videos = exporter.fetch_videos(
    start_date="2026-01-01",
    end_date="2026-01-19",
    sort_by="outlier_score"  # Highest outlier scores first
)
exporter.export_to_excel(videos, filename="viral_videos.xlsx")
```

### Analyze Shorts Performance
```python
# Only YouTube Shorts
videos = exporter.fetch_videos(
    start_date="2026-01-01",
    end_date="2026-01-19",
    is_short=True
)
exporter.export_to_excel(videos, filename="shorts_only.xlsx")
```

---

**Happy Exporting! 🚀**
