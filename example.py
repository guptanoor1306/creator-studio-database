"""
Example usage of CS Data Exporter
"""

from cs_data_exporter import CSDataExporter

# Replace with your actual Bearer token
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_TOKEN_HERE"

# Initialize the exporter
exporter = CSDataExporter(BEARER_TOKEN)

# ===== EXAMPLE 1: Last 7 Days (Simplest) =====
# Automatically fetches transcripts for all videos!
print("Exporting last 7 days with transcripts...")
exporter.quick_export_last_n_days(days=7, filename="last_week.xlsx")

# ===== EXAMPLE 2: Last 30 Days =====
print("\nExporting last 30 days...")
exporter.quick_export_last_n_days(days=30, filename="last_month.xlsx")

# ===== EXAMPLE 3: Specific Date Range =====
print("\nExporting specific date range...")
videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19",
    sort_by="outlier_score"
)
exporter.export_to_excel(videos, filename="jan_12_to_19.xlsx")

# ===== EXAMPLE 4: Specific Channels Only =====
print("\nExporting specific channels...")
my_channels = [
    "UCqW8jxh4tH1Z1sWPbkGWL4g",
    "UCBqvATpjSubtNxpqUDj4_cA",
    "UCsNxHPbaCWL1tkw2hxGQD6g"
]
videos = exporter.fetch_videos(
    start_date="2026-01-01",
    end_date="2026-01-19",
    channel_ids=my_channels,
    sort_by="views"  # Sort by views instead of outlier score
)
exporter.export_to_excel(videos, filename="my_channels.xlsx")

# ===== EXAMPLE 5: Only YouTube Shorts =====
print("\nExporting only shorts...")
videos = exporter.fetch_videos(
    start_date="2026-01-01",
    end_date="2026-01-19",
    is_short=True  # Only shorts
)
exporter.export_to_excel(videos, filename="shorts_only.xlsx")

# ===== EXAMPLE 6: Without Transcripts (Faster) =====
# If you don't need transcripts, you can skip them for faster export
print("\nExporting without transcripts (faster)...")
videos = exporter.fetch_videos(
    start_date="2026-01-12",
    end_date="2026-01-19",
    include_transcripts=False  # Skip transcripts
)
exporter.export_to_excel(videos, filename="no_transcripts.xlsx")

print("\n✅ All exports completed!")
