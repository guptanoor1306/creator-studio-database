# 🔄 Creator Studio Data Export Workflow

## Complete Process Overview

### Step 1: Fetch All Videos (Pagination Handled)

```
API Call: GET /api/user/videos
Parameters:
  - limit: 100
  - offset: 0 (then 100, 200, 300...)
  - start: 2026-01-12
  - end: 2026-01-19
  - sort_by: outlier_score
  - is_short: false
  - channel_ids: (optional)

Response: List of 100 videos (or fewer on last page)
```

**The script automatically:**
- Makes multiple API calls if there are more than 100 videos
- Combines all results into a single list
- Waits 0.5 seconds between pagination requests

**Example Output:**
```
Fetching videos from 2026-01-12 to 2026-01-19...
Fetched 100 videos so far...
Fetched 200 videos so far...
Fetched 250 videos so far...
✓ Total videos fetched: 250
```

---

### Step 2: Fetch Transcripts (Loop Through Each Video)

```
For each video in the list:
  API Call: GET /api/videos/{video_id}/transcript
  
  Response: {
    "text": "Full transcript text here...",
    "language": "en"
  }
  
  Add to video object:
    video['transcript_text'] = response['text']
    video['transcript_language'] = response['language']
  
  Wait 0.3 seconds (rate limiting)
```

**The script automatically:**
- Loops through ALL videos fetched in Step 1
- Makes a separate API call for each video's transcript
- Shows progress every 10 videos
- Handles missing transcripts gracefully
- Waits 0.3 seconds between requests

**Example Output:**
```
Fetching transcripts for 250 videos...
  Progress: 1/250 transcripts...
  Progress: 10/250 transcripts...
  Progress: 20/250 transcripts...
  ...
  Progress: 250/250 transcripts...
✓ Transcripts fetched successfully!
```

---

### Step 3: Export to Excel

```
Create Excel file with multiple sheets:

Sheet 1: Videos
  - All video data
  - Transcript text (full)
  - Transcript language
  - Views, likes, comments
  - Outlier score
  - etc.

Sheet 2: Summary
  - Total videos
  - Date range
  - Aggregate stats

Sheet 3: Raw Data (optional)
  - Original JSON for each video
```

**Example Output:**
```
Preparing data for export...
✓ Data exported successfully to: cs_videos_export_20260119_143022.xlsx
```

---

## 📊 Complete API Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER RUNS SCRIPT                                            │
│ exporter.quick_export_last_n_days(days=7)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: FETCH VIDEOS (with pagination)                     │
├─────────────────────────────────────────────────────────────┤
│ GET /api/user/videos?limit=100&offset=0&...                │
│   → Returns videos 1-100                                    │
│                                                             │
│ GET /api/user/videos?limit=100&offset=100&...              │
│   → Returns videos 101-200                                  │
│                                                             │
│ GET /api/user/videos?limit=100&offset=200&...              │
│   → Returns videos 201-250 (last page)                      │
│                                                             │
│ Result: List of 250 videos (WITHOUT transcripts yet)       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: FETCH TRANSCRIPTS (loop through each video)        │
├─────────────────────────────────────────────────────────────┤
│ For video #1 (id: olzqaofhvLQ):                            │
│   GET /api/videos/olzqaofhvLQ/transcript                   │
│   → Adds transcript_text and transcript_language            │
│   → Wait 0.3s                                               │
│                                                             │
│ For video #2 (id: abc123xyz):                              │
│   GET /api/videos/abc123xyz/transcript                     │
│   → Adds transcript_text and transcript_language            │
│   → Wait 0.3s                                               │
│                                                             │
│ ... (repeat for all 250 videos)                            │
│                                                             │
│ Result: All videos now have transcript data                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: EXPORT TO EXCEL                                     │
├─────────────────────────────────────────────────────────────┤
│ Create DataFrame from all video data                       │
│ Create Excel file with multiple sheets                     │
│ Add formatting and summaries                               │
│                                                             │
│ Result: cs_videos_export_20260119_143022.xlsx              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Performance & Timing

### Time Breakdown

For **N videos**:

1. **Video Fetching**: ~0.5s per 100 videos
   - Example: 250 videos = 3 requests = ~1.5 seconds

2. **Transcript Fetching**: ~0.3s per video
   - Example: 250 videos × 0.3s = ~75 seconds

3. **Excel Export**: ~2-5 seconds (depends on data size)

**Total Time**:
- 10 videos: ~5 seconds
- 50 videos: ~18 seconds
- 100 videos: ~35 seconds
- 250 videos: ~80 seconds
- 500 videos: ~2.5 minutes

### Rate Limiting

The script includes built-in delays to respect API limits:

- **0.5s** between video pagination requests
- **0.3s** between transcript requests
- Prevents API rate limit errors
- Can be adjusted in the code if needed

---

## 🎛️ Control Options

### Option 1: With Transcripts (Default)

```python
exporter.quick_export_last_n_days(days=7)
# or
videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19"
)
```

**Result**: Full data with transcripts for all videos

### Option 2: Without Transcripts (Faster)

```python
exporter.quick_export_last_n_days(days=7, include_transcripts=False)
# or
videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19",
    include_transcripts=False
)
```

**Result**: Fast export without transcript data

---

## 🔍 What Data Gets Fetched?

### From /api/user/videos

- Video ID, Title, Channel Name
- Views, Likes, Comments Count
- Published Date, Duration
- Description, Tags, Category
- Outlier Score, Engagement Rate
- Thumbnail URL
- Is Short (True/False)

### From /api/videos/{id}/transcript (per video)

- Full transcript text
- Language code (e.g., "en", "es", "fr")

### Combined in Excel

All video metadata + transcript data in a single row per video

---

## 💡 Best Practices

1. **Start Small**: Test with 1-2 days of data first
2. **Monitor Progress**: Watch the console output to track progress
3. **Check API Limits**: If you get errors, increase the delay times
4. **Save Regularly**: For large exports (500+ videos), run in chunks
5. **Use Filters**: Narrow down by channel_ids if you don't need all channels

---

## 🐛 Troubleshooting

### "Error fetching transcript for {video_id}"

- Some videos may not have transcripts available
- The script continues anyway and leaves transcript field empty
- This is normal and expected

### "Connection Error"

- Check your internet connection
- Verify your Bearer token hasn't expired
- Try reducing the number of videos

### "Rate Limit Exceeded"

- Increase the sleep time in the code:
  - Line 130: Change `time.sleep(0.5)` to `time.sleep(1.0)`
  - Line 168: Change `time.sleep(0.3)` to `time.sleep(0.5)`

---

## 📞 Support

For API-specific questions, refer to the Creator Studio API documentation or contact your CS admin.
