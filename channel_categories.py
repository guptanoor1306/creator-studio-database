"""
Channel Categories Configuration
NOTE: This file is now OPTIONAL!

The app now fetches categories directly from the Creator Studio API:
  GET /api/channel-categories

This file is kept as a fallback/reference, but the API categories 
will be used automatically if available.

If you want to use manual categories instead, you can modify app.py 
to use this file instead of the API endpoint.
"""

# Category definitions
CATEGORIES = {
    'indian_finance': {
        'name': 'Indian Finance',
        'icon': '🇮🇳',
        'color': '#FF9933',
        'channels': [
            # Add your Indian Finance channel IDs here
            # Example: 'UCqW8jxh4tH1Z1sWPbkGWL4g',
        ]
    },
    'global_finance': {
        'name': 'Global Finance',
        'icon': '🌍',
        'color': '#4CAF50',
        'channels': [
            # Add your Global Finance channel IDs here
        ]
    },
    'business_case_studies': {
        'name': 'Business Case Studies',
        'icon': '📊',
        'color': '#2196F3',
        'channels': [
            # Add your Business Case Studies channel IDs here
        ]
    },
    'podcasts': {
        'name': 'Podcasts',
        'icon': '🎙️',
        'color': '#9C27B0',
        'channels': [
            # Add your Podcasts channel IDs here
        ]
    },
    'others': {
        'name': 'Others',
        'icon': '📺',
        'color': '#607D8B',
        'channels': [
            # All other channels will automatically go here
        ]
    }
}


def get_channel_category(channel_id):
    """
    Get the category for a given channel ID
    Returns: category_key or 'others' if not found
    """
    for category_key, category_info in CATEGORIES.items():
        if category_key == 'others':
            continue
        if channel_id in category_info['channels']:
            return category_key
    return 'others'


def get_category_info(category_key):
    """Get full information for a category"""
    return CATEGORIES.get(category_key, CATEGORIES['others'])


def categorize_channels(channels):
    """
    Group channels by category
    Returns: dict with category keys and list of channels
    """
    categorized = {key: [] for key in CATEGORIES.keys()}
    
    for channel in channels:
        channel_id = channel.get('id', '')
        category = get_channel_category(channel_id)
        categorized[category].append(channel)
    
    # Remove empty categories except 'others'
    return {k: v for k, v in categorized.items() if v or k == 'others'}


def add_channel_to_category(channel_id, category_key):
    """
    Helper function to add a channel to a category
    Use this in an admin interface or script
    """
    if category_key in CATEGORIES and category_key != 'others':
        if channel_id not in CATEGORIES[category_key]['channels']:
            CATEGORIES[category_key]['channels'].append(channel_id)
            return True
    return False


# Quick mapping helper - paste your channel IDs here
# Format: {'channel_id': 'category_key'}
CHANNEL_MAPPING = {
    # Example:
    # 'UCqW8jxh4tH1Z1sWPbkGWL4g': 'indian_finance',
    # 'UCBqvATpjSubtNxpqUDj4_cA': 'global_finance',
    # 'UCsNxHPbaCWL1tkw2hxGQD6g': 'business_case_studies',
    # 'UCPgfM-dk3XAb4T3DhT6Nwsw': 'podcasts',
}

# Auto-populate from mapping
for channel_id, category_key in CHANNEL_MAPPING.items():
    if category_key in CATEGORIES and category_key != 'others':
        if channel_id not in CATEGORIES[category_key]['channels']:
            CATEGORIES[category_key]['channels'].append(channel_id)
