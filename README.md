# Creator Studio Data Exporter

Export YouTube video data from Zero1 Creator Studio to Excel with ease!

## ✨ Key Features

- ✅ **Automatic Transcript Fetching**: Fetches transcripts for all videos in a loop
- 🔄 **Smart Pagination**: Handles large datasets automatically
- 📊 **Rich Excel Output**: Multiple sheets with summaries and full data
- 🎯 **Flexible Filters**: Date ranges, channels, sort options, shorts/regular videos
- ⚡ **Rate Limiting**: Built-in delays to respect API limits

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Bearer Token

1. Open your Creator Studio in a browser (https://zero1creatorstudio.com)
2. Open Developer Tools (F12 or Right-click → Inspect)
3. Go to the **Network** tab
4. Refresh the page or navigate to videos
5. Find a request to `api/user/videos`
6. Click on it and look for the **Authorization** header
7. Copy the token after "Bearer " (the long string starting with `eyJ...`)

### 3. Run the Quick Export Script

```bash
python quick_export.py
```

Paste your Bearer token in the script and choose what to export!

## 📊 Usage Examples

### Example 1: Quick Export (Last 7 Days)

```python
from cs_data_exporter import CSDataExporter

exporter = CSDataExporter("your_bearer_token_here")
exporter.quick_export_last_n_days(days=7)
```

### Example 2: Custom Date Range

```python
from cs_data_exporter import CSDataExporter

exporter = CSDataExporter("your_bearer_token_here")

videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19",
    sort_by="outlier_score",
    is_short=False
)

exporter.export_to_excel(videos, filename="my_export.xlsx")
```

### Example 3: Specific Channels Only

```python
from cs_data_exporter import CSDataExporter

exporter = CSDataExporter("your_bearer_token_here")

channel_ids = [
    "UCqW8jxh4tH1Z1sWPbkGWL4g",
    "UCBqvATpjSubtNxpqUDj4_cA"
]

videos = exporter.fetch_videos(
    start_date="2026-01-01",
    end_date="2026-01-19",
    channel_ids=channel_ids
)

exporter.export_to_excel(videos, filename="selected_channels.xlsx")
```

## 📋 Available Filters

When calling `fetch_videos()`, you can use these parameters:

- **start_date**: Start date (YYYY-MM-DD format)
- **end_date**: End date (YYYY-MM-DD format)
- **channel_ids**: List of channel IDs to filter (optional)
- **sort_by**: Sort field - options: `outlier_score`, `views`, `published_at`, etc.
- **is_short**: `True` for YouTube Shorts only, `False` for regular videos
- **limit**: Number of records per API request (default: 100)
- **include_transcripts**: `True` to fetch transcripts for each video (default: True)

## 📝 Transcript Fetching

**By default, the script automatically fetches transcripts for ALL videos!**

The script will:
1. First fetch all videos matching your filters
2. Then loop through each video and fetch its transcript
3. Add transcript text and language to your Excel export

This happens automatically, but if you want to skip transcripts for faster exports:

```python
videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19",
    include_transcripts=False  # Skip transcripts
)
```

**Note**: Fetching transcripts adds time to the export (about 0.3 seconds per video), but ensures you have complete data!

### How It Works

```
Step 1: Fetch Videos
  ↓
  GET /api/user/videos?start=2026-01-12&end=2026-01-19
  → Returns 100 videos (handles pagination automatically)

Step 2: Fetch Transcripts (for each video)
  ↓
  Loop through videos:
    Video 1: GET /api/videos/{video_id_1}/transcript
    Video 2: GET /api/videos/{video_id_2}/transcript
    Video 3: GET /api/videos/{video_id_3}/transcript
    ... (with 0.3s delay between requests)

Step 3: Export to Excel
  ↓
  Combine all data → Create Excel file with multiple sheets
```

**Time Estimates:**
- 10 videos: ~5 seconds (3s for transcripts + 2s for videos)
- 100 videos: ~35 seconds (30s for transcripts + 5s for videos)
- 500 videos: ~2.5 minutes (150s for transcripts + 30s for videos)

## 📁 Excel Output

The exported Excel file contains:

### Sheet 1: Videos
- Video ID, Title, Channel Name
- Views, Likes, Comments
- Outlier Score, Engagement Rate
- Published Date, Duration
- Description, Tags, Category
- **Transcript** (full text, automatically fetched)
- **Transcript Language** (language code)
- YouTube URL, Thumbnail URL

### Sheet 2: Summary
- Total videos count
- Date range
- Total views, likes, comments
- Average views per video
- Export timestamp

### Sheet 3: Raw Data (optional)
- Complete JSON response for advanced analysis

## 🔧 Advanced Usage

### Using a Config File

1. Copy `config.example.py` to `config.py`
2. Add your Bearer token and settings
3. Import and use:

```python
from config import BEARER_TOKEN, CHANNEL_IDS
from cs_data_exporter import CSDataExporter

exporter = CSDataExporter(BEARER_TOKEN)
videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19",
    channel_ids=CHANNEL_IDS
)
exporter.export_to_excel(videos)
```

### Pagination

The script automatically handles pagination, fetching all available videos in batches of 100.

### Rate Limiting

Built-in 0.5-second delay between requests to avoid overwhelming the API.

## 🛠️ Troubleshooting

### "Authentication Error"
- Your Bearer token may have expired
- Get a fresh token from the browser's Network tab

### "No videos found"
- Check your date range
- Verify channel IDs are correct
- Try without channel filters first

### "Connection Error"
- Check your internet connection
- Verify the API endpoint is accessible

## 📝 Notes

- Bearer tokens typically expire after some time (hours/days)
- You'll need to refresh the token periodically
- The script respects API rate limits
- Large date ranges may take a few minutes to export

## 🎯 Common Use Cases

1. **Weekly Reports**: Export last 7 days every Monday
2. **Channel Analysis**: Filter specific channels for deep dive
3. **Outlier Detection**: Sort by outlier_score to find viral videos
4. **Content Planning**: Analyze descriptions and tags of top performers

## 🤝 Support

For issues or questions, check the Creator Studio documentation or API support.
