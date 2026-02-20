# 🌐 Creator Studio Data Exporter - Web UI Guide

## 🚀 Quick Start

### 1. Start the Server

```bash
cd /Users/noorgupta/Downloads/Cursor/csdb
source venv/bin/activate
python app.py
```

### 2. Open in Browser

Navigate to: **http://localhost:8080**

The beautiful web interface will load automatically!

---

## ✨ Features

### 📺 Channel Selection
- **Visual channel picker** with thumbnails
- See subscriber counts for each channel
- **Select/Deselect All** button for quick selection
- Multi-select channels to export

### 📅 Time Frame Options
- Last 7 days
- Last 30 days
- Last 90 days
- This month

### 🎬 Content Type Filters
- All (Videos + Shorts)
- Videos only
- Shorts only

### 🎯 Advanced Filters

**Sort Options:**
- Highest outlier score
- Most views
- Most recent
- Most likes

**Outlier Score Range:**
- Dual slider to set minimum and maximum outlier scores
- Range from 0x to 100x

**View Count Filter:**
- Set minimum views
- Set maximum views (optional)

### ⚙️ Export Options

**Include Transcripts:**
- ✅ Checked (default): Fetches full transcripts for each video
- ⬜ Unchecked: Skips transcripts for faster export

---

## 📊 Using the Interface

### Step 1: Select Channels
1. Scroll through the channel grid
2. Click on channels to select/deselect
3. Or use "Select / Deselect All" button
4. Selected channels have a purple highlight

### Step 2: Configure Filters
1. **Time Frame**: Choose your date range
2. **Content Type**: Select videos, shorts, or both
3. **Sort By**: Choose how to sort the results
4. **Outlier Score**: Adjust the range sliders
5. **View Counts**: Set min/max view thresholds

### Step 3: Preview (Optional)
- Click **🔍 Preview Count** to see how many videos match your filters
- This gives you a quick count without downloading

### Step 4: Export
- Click **📥 Export to Excel**
- Wait while the system:
  1. Fetches all matching videos
  2. Loops through each video and fetches transcripts (if enabled)
  3. Creates the Excel file
- File downloads automatically when ready!

---

## 🎨 UI Features

### Beautiful Design
- ✨ Modern gradient design
- 🌈 Smooth animations and transitions
- 📱 Responsive (works on mobile too!)
- 🎯 Clean, intuitive interface

### Real-time Feedback
- **Loading indicators** show progress
- **Status messages** for success/errors
- **Preview stats** show video counts and date ranges
- **Progress updates** during transcript fetching

### Smart UX
- **Hover effects** on all interactive elements
- **Visual feedback** for selected channels
- **Range sliders** for easy filtering
- **Checkbox toggle** for transcript option

---

## 📁 Excel Output

The exported file contains:

### Sheet 1: Videos
- Video ID, Title, Channel Name
- Views, Likes, Comments
- Outlier Score, Engagement Rate
- Published Date, Duration
- **Full Transcript** (if enabled)
- **Transcript Language**
- Description, Tags, Category
- YouTube URL, Thumbnail

### Sheet 2: Summary
- Total videos count
- Date range
- Total views/likes/comments
- Average views per video
- Export timestamp

---

## ⏱️ Performance

**With Transcripts Enabled:**
- 10 videos: ~5 seconds
- 50 videos: ~18 seconds
- 100 videos: ~35 seconds
- 500 videos: ~2.5 minutes

**Without Transcripts:**
- 100 videos: ~3-5 seconds
- 500 videos: ~10-15 seconds

---

## 🔧 Technical Details

### Architecture
```
┌─────────────────────────────────────────┐
│  Frontend (HTML/CSS/JavaScript)         │
│  - Beautiful UI                         │
│  - Channel selection                    │
│  - Filter configuration                 │
│  - Real-time updates                    │
└────────────┬────────────────────────────┘
             │ AJAX Requests
┌────────────▼────────────────────────────┐
│  Flask Backend (Python)                 │
│  - API endpoints                        │
│  - Data fetching                        │
│  - Transcript loop                      │
│  - Excel generation                     │
└────────────┬────────────────────────────┘
             │ HTTP Requests
┌────────────▼────────────────────────────┐
│  Creator Studio API                     │
│  - GET /api/user/channels               │
│  - GET /api/user/videos                 │
│  - GET /api/videos/{id}/transcript      │
└─────────────────────────────────────────┘
```

### API Endpoints

**GET /api/channels**
- Fetches all available channels
- Returns: Channel list with names, thumbnails, subscribers

**POST /api/preview**
- Quick video count without transcripts
- Returns: Number of videos matching filters

**POST /api/export**
- Main export function
- Fetches videos + transcripts
- Generates Excel file
- Returns: Download link

**GET /api/download/{filename}**
- Downloads generated Excel file

---

## 🛠️ Customization

### Change Port

Edit `app.py` line ~262:

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 8080 to your port
```

### Update Bearer Token

Edit `app.py` line ~14:

```python
BEARER_TOKEN = "your_new_token_here"
```

### Modify Filters

Edit `templates/index.html` to add/remove filter options in the dropdowns.

---

## 🎯 Use Cases

### Weekly Team Report
1. Select all channels
2. Choose "Last 7 days"
3. Enable transcripts
4. Export → Share with team

### High-Performing Content Analysis
1. Select specific channels
2. Set outlier score to 10x-100x
3. Sort by "Highest outlier"
4. Export → Analyze top content

### View Threshold Analysis
1. Set minimum views (e.g., 10,000)
2. Last 30 days
3. Export → Find consistent performers

### Shorts vs Videos Comparison
1. Export 1: Content type = "Shorts only"
2. Export 2: Content type = "Videos only"
3. Compare metrics in Excel

---

## 💡 Tips

1. **Use Preview First**: Check video counts before full export
2. **Disable Transcripts for Speed**: If you don't need them, uncheck for faster exports
3. **Filter Strategically**: Use outlier score and view filters to narrow results
4. **Select Relevant Channels**: Don't export all channels if you only need specific ones
5. **Regular Exports**: Schedule weekly exports for consistent tracking

---

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Kill existing process on port 8080
lsof -ti:8080 | xargs kill -9

# Restart
python app.py
```

### "No channels found"
- Check your Bearer token is valid
- Token may have expired - get a new one from browser

### Export Takes Too Long
- Disable transcripts
- Reduce date range
- Filter by specific channels only

### Can't Download File
- Check browser's download folder
- Look for popup blocker
- Try different browser

---

## 🎉 You're Ready!

Open **http://localhost:8080** in your browser and start exporting! 🚀

The interface is intuitive and self-explanatory. Enjoy your beautiful new data export tool!
