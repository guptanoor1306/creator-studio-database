"""
Configuration file for CS Data Exporter
Copy this file to config.py and add your actual token
"""

# Your Bearer token from Creator Studio
# You can find this in the Authorization header of your browser's Network tab
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Your channel IDs (optional - leave empty to fetch all channels)
CHANNEL_IDS = [
    "UCqW8jxh4tH1Z1sWPbkGWL4g",
    "UCBqvATpjSubtNxpqUDj4_cA",
    # Add more channel IDs here
]

# Default settings
DEFAULT_DAYS = 7  # Number of days to look back
SORT_BY = "outlier_score"  # Sort field: outlier_score, views, published_at, etc.
INCLUDE_SHORTS = False  # Set to True to include YouTube Shorts
