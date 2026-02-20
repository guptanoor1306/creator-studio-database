"""
Helper Script to Categorize Channels
Run this to easily assign your channels to categories
"""

import requests
import json

# Your Bearer token
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODZkMGM0MjMyMWNkNDZiZWFhMDU5MTUiLCJleHAiOjE3ODcxMTc1ODZ9.sHS-ZkuRjQ4gp-_hrnFeVQtVbe31Lmbln-oXXicgbUc"

# Categories
CATEGORIES = {
    '1': {'key': 'indian_finance', 'name': 'Indian Finance', 'icon': '🇮🇳'},
    '2': {'key': 'global_finance', 'name': 'Global Finance', 'icon': '🌍'},
    '3': {'key': 'business_case_studies', 'name': 'Business Case Studies', 'icon': '📊'},
    '4': {'key': 'podcasts', 'name': 'Podcasts', 'icon': '🎙️'},
    '5': {'key': 'others', 'name': 'Others', 'icon': '📺'},
}


def fetch_channels():
    """Fetch all channels from Creator Studio"""
    try:
        response = requests.get(
            "https://confucius.zero1creatorstudio.com/api/user/channels",
            headers={
                "Authorization": f"Bearer {BEARER_TOKEN}",
                "Accept": "application/json"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
            else:
                return data.get('data', data.get('channels', []))
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def generate_mapping():
    """Interactive script to categorize channels"""
    print("\n" + "=" * 70)
    print("Channel Categorization Helper")
    print("=" * 70)
    print("\nFetching your channels from Creator Studio...\n")
    
    channels = fetch_channels()
    
    if not channels:
        print("❌ No channels found or error fetching channels.")
        return
    
    print(f"✅ Found {len(channels)} channels!\n")
    print("=" * 70)
    print("\nAvailable Categories:")
    for num, cat in CATEGORIES.items():
        print(f"  {num}. {cat['icon']} {cat['name']}")
    print("\n" + "=" * 70)
    
    mapping = {}
    
    print("\n📝 For each channel, enter the category number (1-5)")
    print("   Or press Enter to assign to 'Others' automatically\n")
    
    for i, channel in enumerate(channels, 1):
        channel_id = channel.get('id', channel.get('channel_id', ''))
        channel_name = channel.get('name', channel.get('title', 'Unknown'))
        subs = channel.get('subscriber_count', channel.get('subscribers', 0))
        
        print(f"\n[{i}/{len(channels)}] 📺 {channel_name}")
        print(f"         Subscribers: {format_number(subs)}")
        print(f"         ID: {channel_id}")
        
        while True:
            choice = input("         Category (1-5, or Enter for Others): ").strip()
            
            if choice == '':
                choice = '5'  # Default to Others
            
            if choice in CATEGORIES:
                category_key = CATEGORIES[choice]['key']
                mapping[channel_id] = category_key
                print(f"         ✓ Assigned to: {CATEGORIES[choice]['icon']} {CATEGORIES[choice]['name']}")
                break
            else:
                print("         ❌ Invalid choice. Please enter 1-5.")
    
    # Generate output
    print("\n" + "=" * 70)
    print("✅ Categorization Complete!")
    print("=" * 70)
    
    print("\n📋 Copy this mapping to channel_categories.py:\n")
    print("CHANNEL_MAPPING = {")
    for channel_id, category_key in mapping.items():
        channel = next((ch for ch in channels if ch.get('id', ch.get('channel_id')) == channel_id), None)
        if channel:
            channel_name = channel.get('name', channel.get('title', 'Unknown'))
            print(f"    '{channel_id}': '{category_key}',  # {channel_name}")
    print("}")
    
    # Save to file
    output_file = 'channel_mapping.txt'
    with open(output_file, 'w') as f:
        f.write("# Channel Categorization Mapping\n")
        f.write("# Copy this to channel_categories.py\n\n")
        f.write("CHANNEL_MAPPING = {\n")
        for channel_id, category_key in mapping.items():
            channel = next((ch for ch in channels if ch.get('id', ch.get('channel_id')) == channel_id), None)
            if channel:
                channel_name = channel.get('name', channel.get('title', 'Unknown'))
                f.write(f"    '{channel_id}': '{category_key}',  # {channel_name}\n")
        f.write("}\n")
    
    print(f"\n💾 Mapping also saved to: {output_file}")
    print("\n🔧 Next steps:")
    print("   1. Open channel_categories.py")
    print("   2. Replace the CHANNEL_MAPPING dict with the one above")
    print("   3. Restart the Flask server")
    print("   4. Refresh your browser - channels will be categorized!\n")


def format_number(num):
    """Format number with K/M suffix"""
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    return str(num)


def quick_list():
    """Just list all channels with their IDs"""
    print("\n" + "=" * 70)
    print("Channel List")
    print("=" * 70)
    
    channels = fetch_channels()
    
    if not channels:
        print("❌ No channels found or error fetching channels.")
        return
    
    print(f"\n✅ Found {len(channels)} channels:\n")
    
    for i, channel in enumerate(channels, 1):
        channel_id = channel.get('id', channel.get('channel_id', ''))
        channel_name = channel.get('name', channel.get('title', 'Unknown'))
        subs = channel.get('subscriber_count', channel.get('subscribers', 0))
        
        print(f"{i:2d}. {channel_name}")
        print(f"    ID: {channel_id}")
        print(f"    Subscribers: {format_number(subs)}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        quick_list()
    else:
        generate_mapping()
