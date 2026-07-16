"""
Flask Web Application for Creator Studio Data Exporter
Provides a beautiful HTML UI for exporting data with filters
"""

from flask import Flask, render_template, request, jsonify, send_file
from cs_data_exporter import CSDataExporter
from channel_categories import categorize_channels, get_channel_category, get_category_info, CATEGORIES
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os
import traceback
import requests as http_requests
import atexit
import json

app = Flask(__name__)

# Scheduler configuration storage
SCHEDULER_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'scheduler_config.json')
scheduler = BackgroundScheduler()
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


# Global error handler to always return JSON for API endpoints
@app.errorhandler(Exception)
def handle_error(error):
    """Handle all errors and return JSON instead of HTML"""
    # Check if this is an API request
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': str(error)
        }), 500
    # For non-API requests, let Flask handle it normally
    raise error


# Scheduler configuration management
def load_scheduler_config():
    """Load scheduler configuration from file"""
    if os.path.exists(SCHEDULER_CONFIG_FILE):
        try:
            with open(SCHEDULER_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading scheduler config: {e}")
    return None

def save_scheduler_config(config):
    """Save scheduler configuration to file"""
    try:
        with open(SCHEDULER_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving scheduler config: {e}")
        return False

def scheduled_slack_notification():
    """Scheduled task to send Slack notifications"""
    try:
        config = load_scheduler_config()
        if not config or not config.get('enabled'):
            print("Scheduler disabled or no config found")
            return
        
        print(f"\n⏰ Running scheduled Slack notification at {datetime.now()}")
        
        # Get credentials from environment variables or config file
        bearer_token = os.environ.get('CS_BEARER_TOKEN') or config.get('bearer_token')
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL') or config.get('webhook_url')
        days_back = config.get('days_back', 7)
        category_filter = config.get('category_filter', 'all')
        long_form_threshold = config.get('long_form_threshold', 500000)
        shorts_threshold = config.get('shorts_threshold', 100000)
        
        if not bearer_token or not webhook_url:
            print("Missing bearer token or webhook URL. Set CS_BEARER_TOKEN and SLACK_WEBHOOK_URL environment variables or configure in UI.")
            return
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        print(f"📅 Date range: {start_date_str} to {end_date_str}")
        
        # Create exporter and fetch videos
        exporter = CSDataExporter(bearer_token)
        
        # First, fetch channels with categories to build mapping
        print("📡 Fetching channels and categories...")
        channel_to_category = {}
        categories_available = False
        try:
            channels_response = http_requests.get(
                "https://confucius.zero1creatorstudio.com/api/user/channels",
                headers={
                    "Authorization": f"Bearer {bearer_token}",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if channels_response.status_code == 200:
                channels_data = channels_response.json()
                channels_list = channels_data if isinstance(channels_data, list) else channels_data.get('data', channels_data.get('channels', []))
                
                for channel in channels_list:
                    channel_id = channel.get('channel_id', channel.get('id', ''))
                    category = channel.get('category', channel.get('categoryName', ''))
                    if channel_id and category:
                        channel_to_category[channel_id] = category
                
                if channel_to_category:
                    categories_available = True
                    print(f"✅ Mapped {len(channel_to_category)} channels to categories")
                else:
                    print(f"⚠️ No categories found in response")
        except Exception as e:
            print(f"⚠️ Could not fetch channel categories: {e}")
            print(f"   Continuing without category information...")
            categories_available = False
        
        # Fetch videos
        print("📡 Fetching videos...")
        videos = exporter.fetch_videos(
            start_date=start_date_str,
            end_date=end_date_str,
            channel_ids=None,
            sort_by='views',
            is_short=False,
            include_transcripts=False
        )
        
        shorts = exporter.fetch_videos(
            start_date=start_date_str,
            end_date=end_date_str,
            channel_ids=None,
            sort_by='views',
            is_short=True,
            include_transcripts=False
        )
        
        print(f"✅ Fetched {len(videos)} long-form videos and {len(shorts)} shorts")
        
        # Filter high-performing content
        high_performing_videos = []
        high_performing_shorts = []
        
        for video in videos:
            views = int(video.get('views', video.get('view_count', 0)) or 0)
            channel_id = video.get('channel_id', '')
            channel_name = video.get('channel_title', 'Unknown')
            video_category = channel_to_category.get(channel_id, '') if categories_available else ''
            
            if categories_available and category_filter != 'all' and video_category:
                if video_category.lower().replace(' ', '_') != category_filter:
                    continue
            
            if views >= long_form_threshold:
                video_data = {
                    'title': video.get('title', 'Untitled'),
                    'channel': channel_name,
                    'views': views,
                    'url': f"https://youtube.com/watch?v={video.get('video_id', '')}",
                    'published': video.get('published_at', ''),
                    'thumbnail': video.get('thumbnail_url', video.get('thumbnails', {}).get('high', {}).get('url', '')),
                    'type': 'Long-form'
                }
                if categories_available and video_category:
                    video_data['category'] = video_category
                high_performing_videos.append(video_data)
        
        for video in shorts:
            views = int(video.get('views', video.get('view_count', 0)) or 0)
            channel_id = video.get('channel_id', '')
            channel_name = video.get('channel_title', 'Unknown')
            video_category = channel_to_category.get(channel_id, '') if categories_available else ''
            
            if categories_available and category_filter != 'all' and video_category:
                if video_category.lower().replace(' ', '_') != category_filter:
                    continue
            
            if views >= shorts_threshold:
                video_data = {
                    'title': video.get('title', 'Untitled'),
                    'channel': channel_name,
                    'views': views,
                    'url': f"https://youtube.com/shorts/{video.get('video_id', '')}",
                    'published': video.get('published_at', ''),
                    'thumbnail': video.get('thumbnail_url', video.get('thumbnails', {}).get('high', {}).get('url', '')),
                    'type': 'Short'
                }
                if categories_available and video_category:
                    video_data['category'] = video_category
                high_performing_shorts.append(video_data)
        
        # Sort by views
        high_performing_videos_sorted = sorted(high_performing_videos, key=lambda x: x['views'], reverse=True)
        high_performing_shorts_sorted = sorted(high_performing_shorts, key=lambda x: x['views'], reverse=True)
        
        total_videos = len(high_performing_videos_sorted) + len(high_performing_shorts_sorted)
        
        if total_videos == 0:
            print("No high-performing videos found")
            return
        
        # Format and send Slack message
        category_names = {
            'indian_finance': 'Indian Finance',
            'global_finance': 'Global Finance',
            'business_case_studies': 'Business Case Studies',
            'podcasts': 'Podcasts',
            'others': 'Others',
            'all': 'All Categories'
        }
        category_display = category_names.get(category_filter, category_filter)
        
        slack_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"High-Performing Content Report"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Category:* {category_display}\n*Date Range:* {start_date_str} to {end_date_str}\n*Total Videos:* {total_videos} ({len(high_performing_videos_sorted)} Long-form, {len(high_performing_shorts_sorted)} Shorts)"
                }
            },
            {"type": "divider"}
        ]
        
        # Add long-form section
        if high_performing_videos_sorted:
            slack_blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Long-Form Videos (>{long_form_threshold:,} views)"
                }
            })
            
            for video in high_performing_videos_sorted:
                video_text = f"• *{video['title']}*\n"
                video_text += f"  Channel: {video['channel']}\n"
                # Only add category if available
                if 'category' in video:
                    video_text += f"  Category: {video['category']}\n"
                video_text += f"  Views: {video['views']:,}\n"
                video_text += f"  Published: {video['published'][:10] if video['published'] else 'Unknown'}\n"
                video_text += f"  Link: {video['url']}"
                
                slack_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": video_text
                    }
                })
        
        # Add shorts section
        if high_performing_shorts_sorted:
            slack_blocks.append({"type": "divider"})
            slack_blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Shorts (>{shorts_threshold:,} views)"
                }
            })
            
            for video in high_performing_shorts_sorted:
                video_text = f"• *{video['title']}*\n"
                video_text += f"  Channel: {video['channel']}\n"
                # Only add category if available
                if 'category' in video:
                    video_text += f"  Category: {video['category']}\n"
                video_text += f"  Views: {video['views']:,}\n"
                video_text += f"  Published: {video['published'][:10] if video['published'] else 'Unknown'}\n"
                video_text += f"  Link: {video['url']}"
                
                slack_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": video_text
                    }
                })
        
        # Send to Slack
        slack_message = {"blocks": slack_blocks}
        response = http_requests.post(webhook_url, json=slack_message)
        
        if response.status_code == 200:
            print(f"✅ Successfully sent scheduled notification to Slack")
        else:
            print(f"❌ Failed to send to Slack: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error in scheduled task: {e}")
        traceback.print_exc()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/channels', methods=['POST'])
def get_channels():
    """Fetch available channels with categories from CS API"""
    try:
        import requests
        
        # Get bearer token from request
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request format. Expected JSON data.'}), 400
        
        bearer_token = data.get('bearerToken', '')
        
        if not bearer_token:
            return jsonify({'success': False, 'error': 'Bearer token is required'}), 400
        
        # Fetch channels from CS API
        try:
            channels_response = requests.get(
                "https://confucius.zero1creatorstudio.com/api/user/channels",
                headers={
                    "Authorization": f"Bearer {bearer_token}",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if channels_response.status_code != 200:
                return jsonify({'success': False, 'error': f'Channels API returned status {channels_response.status_code}'})
            
            # Parse channels
            channels_data = channels_response.json()
            print(f"📊 Channels API response type: {type(channels_data)}")
            
            if isinstance(channels_data, list):
                channels_list = channels_data
            elif isinstance(channels_data, dict):
                # Try different possible keys
                channels_list = channels_data.get('data', channels_data.get('channels', []))
                
                # Handle case where data might be nested
                if isinstance(channels_list, dict) and 'channels' in channels_list:
                    channels_list = channels_list['channels']
                elif isinstance(channels_list, dict) and 'data' in channels_list:
                    channels_list = channels_list['data']
            else:
                channels_list = []
            
            print(f"📊 Parsed channels_list type: {type(channels_list)}, length: {len(channels_list) if isinstance(channels_list, list) else 'N/A'}")
            
            # Ensure it's a list
            if not isinstance(channels_list, list):
                print(f"⚠️ channels_list is not a list, it's: {type(channels_list)}")
                channels_list = []
                
        except Exception as e:
            print(f"❌ Error fetching channels: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Failed to fetch channels: {str(e)}'})
        
        # Try to fetch categories from CS API (optional)
        cs_categories = {}
        channel_to_category = {}
        
        try:
            categories_response = requests.get(
                "https://confucius.zero1creatorstudio.com/api/channel-categories",
                headers={
                    "Authorization": f"Bearer {bearer_token}",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if categories_response.status_code == 200:
                categories_data = categories_response.json()
                
                # Handle different response formats
                if isinstance(categories_data, dict) and 'categories' in categories_data:
                    cs_categories_list = categories_data['categories']
                elif isinstance(categories_data, list):
                    cs_categories_list = categories_data
                else:
                    cs_categories_list = []
                
                # Build category mapping
                for cat in cs_categories_list:
                    category_id = cat.get('id', cat.get('category_id', ''))
                    category_name = cat.get('name', cat.get('title', ''))
                    category_channels = cat.get('channels', cat.get('channel_ids', []))
                    
                    # Map category name to our keys
                    category_key = category_name.lower().replace(' ', '_')
                    
                    # Store category info
                    cs_categories[category_key] = {
                        'id': category_id,
                        'name': category_name,
                        'channels': []
                    }
                    
                    # Map each channel to this category
                    for channel_id in category_channels:
                        channel_to_category[channel_id] = category_key
        except Exception as e:
            print(f"⚠️ Could not fetch channel categories: {e}")
            print(f"   Continuing without category information...")
        
        # Format channels with category information
        formatted_channels = []
        categorized = {}
        
        # Define icon and color mapping
        category_icons = {
            'indian_finance': '🇮🇳',
            'global_finance': '🌍',
            'business_case_studies': '📊',
            'podcasts': '🎙️',
            'others': '📺'
        }
        
        category_colors = {
            'indian_finance': '#FF9933',
            'global_finance': '#4CAF50',
            'business_case_studies': '#2196F3',
            'podcasts': '#9C27B0',
            'others': '#607D8B'
        }
        
        for ch in channels_list:
            # Safety check: ensure ch is a dictionary
            if not isinstance(ch, dict):
                print(f"⚠️ Skipping non-dict channel item: {type(ch)}")
                continue
                
            mongodb_id = ch.get('id', '')
            youtube_channel_id = ch.get('channel_id', '')
            
            # Get category from channel object or mapping
            category_from_api = ch.get('category', '')
            if category_from_api:
                # Convert API category to our key format
                category_key = category_from_api.lower().replace(' ', '_')
            else:
                category_key = channel_to_category.get(mongodb_id, 'others')
            
            formatted_channel = {
                'id': youtube_channel_id,  # Use YouTube ID for filtering videos
                'mongodb_id': mongodb_id,   # Keep MongoDB ID for reference
                'name': ch.get('title', ch.get('name', 'Unknown Channel')),
                'thumbnail': ch.get('thumbnail_url', ch.get('thumbnail', '')),
                'subscribers': ch.get('subscriber_count', ch.get('subscribers', 0)),
                'category': category_key
            }
            
            formatted_channels.append(formatted_channel)
            
            # Group by category
            if category_key not in categorized:
                category_name = cs_categories.get(category_key, {}).get('name', category_key.replace('_', ' ').title())
                categorized[category_key] = {
                    'key': category_key,
                    'name': category_name,
                    'icon': category_icons.get(category_key, '📺'),
                    'color': category_colors.get(category_key, '#607D8B'),
                    'channels': [],
                    'count': 0
                }
            
            categorized[category_key]['channels'].append(formatted_channel)
            categorized[category_key]['count'] += 1
        
        # Convert to list and sort by priority
        priority_order = ['indian_finance', 'global_finance', 'business_case_studies', 'podcasts', 'others']
        categories_list = []
        
        for key in priority_order:
            if key in categorized:
                categories_list.append(categorized[key])
        
        # Add any other categories not in priority list
        for key, cat in categorized.items():
            if key not in priority_order:
                categories_list.append(cat)
        
        return jsonify({
            'success': True,
            'channels': formatted_channels,
            'categories': categories_list
        })
        
    except Exception as e:
        print(f"Error fetching channels: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/export', methods=['POST'])
def export_data():
    """Export data with filters"""
    try:
        print("\n" + "="*70)
        print("📤 EXPORT REQUEST RECEIVED")
        print("="*70)
        
        data = request.get_json(silent=True)
        if not data:
            print("❌ Error: No JSON data received")
            return jsonify({'success': False, 'error': 'Invalid request format. Expected JSON data.'}), 400
        
        # Get bearer token from request
        bearer_token = data.get('bearerToken', '')
        
        if not bearer_token:
            print("❌ Error: No bearer token provided")
            return jsonify({'success': False, 'error': 'Bearer token is required'}), 400
        
        print(f"✅ Bearer token received: {bearer_token[:20]}...")
        
        # Parse filters with error handling
        try:
            time_frame = data.get('timeFrame', 'last_7_days')
            channel_ids = data.get('channelIds', [])
            content_type = data.get('contentType', 'all')
            sort_by = data.get('sortBy', 'outlier_score')
            outlier_min = float(data.get('outlierMin', 0))
            outlier_max = float(data.get('outlierMax', 100))
            views_min = int(data.get('viewsMin', 0))
            views_max_raw = data.get('viewsMax', None)
            views_max = int(views_max_raw) if views_max_raw and str(views_max_raw).strip() else None
            include_transcripts = data.get('includeTranscripts', True)
            
            print(f"📋 Filters parsed successfully:")
            print(f"   Time frame: {time_frame}")
            print(f"   Channels: {len(channel_ids)}")
            print(f"   Content type: {content_type}")
            print(f"   Sort by: {sort_by}")
            print(f"   Include transcripts: {include_transcripts}")
        except Exception as parse_error:
            print(f"❌ Error parsing filters: {parse_error}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Invalid filter values: {str(parse_error)}'}), 400
        
        # Calculate date range
        end_date = datetime.now()
        
        if time_frame == 'last_7_days':
            start_date = end_date - timedelta(days=7)
        elif time_frame == 'last_30_days':
            start_date = end_date - timedelta(days=30)
        elif time_frame == 'last_90_days':
            start_date = end_date - timedelta(days=90)
        elif time_frame == 'last_6_months':
            start_date = end_date - timedelta(days=180)
        elif time_frame == 'last_year':
            start_date = end_date - timedelta(days=365)
        elif time_frame == 'lifetime':
            # Fetch all videos - use a very old date (YouTube launched in 2005)
            start_date = datetime(2005, 1, 1)
        elif time_frame == 'this_month':
            start_date = end_date.replace(day=1)
        elif time_frame == 'custom':
            start_date = datetime.strptime(data.get('startDate'), '%Y-%m-%d')
            end_date = datetime.strptime(data.get('endDate'), '%Y-%m-%d')
        else:
            start_date = end_date - timedelta(days=7)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        print(f"\n=== Export Request ===")
        print(f"Time Frame: {time_frame}")
        print(f"Date Range: {start_date_str} to {end_date_str}")
        print(f"Selected Channels: {len(channel_ids)} channels")
        print(f"Channel IDs: {channel_ids[:3]}..." if channel_ids else "No channels selected")
        print(f"Content Type: {content_type}")
        print(f"Sort By: {sort_by}")
        
        # Determine is_short based on content type
        is_short = None
        if content_type == 'shorts':
            is_short = True
        elif content_type == 'videos':
            is_short = False
        
        # Fetch videos
        print(f"\n=== Fetching Videos ===")
        print(f"API Call Parameters:")
        print(f"  start_date: {start_date_str}")
        print(f"  end_date: {end_date_str}")
        print(f"  channel_ids: {channel_ids if channel_ids else 'All channels'}")
        print(f"  sort_by: {sort_by}")
        print(f"  is_short: {is_short}")
        print(f"  include_transcripts: {include_transcripts}")
        
        # Create exporter with user's token
        try:
            print("🔧 Creating CSDataExporter instance...")
            exporter = CSDataExporter(bearer_token)
            print("✅ CSDataExporter created successfully")
        except Exception as exporter_error:
            print(f"❌ Error creating CSDataExporter: {exporter_error}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Failed to initialize exporter: {str(exporter_error)}'}), 500
        
        try:
            print("📡 Fetching videos from API...")
            videos = exporter.fetch_videos(
                start_date=start_date_str,
                end_date=end_date_str,
                channel_ids=channel_ids if channel_ids else None,
                sort_by=sort_by,
                is_short=is_short if is_short is not None else False,
                include_transcripts=include_transcripts
            )
            print(f"✅ Fetch completed: {len(videos) if videos else 0} videos retrieved")
        except Exception as fetch_error:
            print(f"❌ Error fetching videos: {fetch_error}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Failed to fetch videos: {str(fetch_error)}'}), 500
        
        print(f"\n=== Videos Fetched ===")
        print(f"Total videos before filters: {len(videos)}")
        
        if not videos:
            print("❌ No videos found from API")
            return jsonify({'success': False, 'error': 'No videos found matching your filters. Try expanding your date range or removing channel filters.'})
        
        # Apply additional filters
        print(f"\n=== Applying Additional Filters ===")
        print(f"Outlier range: {outlier_min} to {outlier_max}")
        print(f"Views range: {views_min} to {views_max if views_max else 'unlimited'}")
        
        filtered_videos = []
        for video in videos:
            # Filter by outlier score
            outlier = video.get('outlier_score', video.get('outlierScore', 0))
            try:
                outlier = float(outlier) if outlier else 0
            except:
                outlier = 0
            
            if outlier < outlier_min or outlier > outlier_max:
                continue
            
            # Filter by views
            views = video.get('views', video.get('view_count', 0))
            if views < views_min:
                continue
            if views_max and views > views_max:
                continue
            
            filtered_videos.append(video)
        
        print(f"Videos after filters: {len(filtered_videos)}")
        
        if not filtered_videos:
            print("❌ No videos match filter criteria")
            return jsonify({'success': False, 'error': f'No videos match your filter criteria. Found {len(videos)} videos in date range, but none match outlier score ({outlier_min}-{outlier_max}) or view count filters.'})
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cs_export_{timestamp}.xlsx"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # Export to Excel with error handling
        try:
            print(f"\n📊 Creating Excel file: {filename}")
            exporter.export_to_excel(filtered_videos, filename=filepath)
            print(f"✅ Excel file created successfully")
            
            return jsonify({
                'success': True,
                'filename': filename,
                'video_count': len(filtered_videos),
                'message': f'Successfully exported {len(filtered_videos)} videos'
            })
        except Exception as export_error:
            print(f"❌ Error during Excel export: {export_error}")
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Error creating Excel file: {str(export_error)}. The data was fetched successfully but there was an issue formatting it for Excel.'
            }), 500
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR in export_data:")
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download exported file"""
    try:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/preview', methods=['POST'])
def preview_data():
    """Preview video count before exporting"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request format. Expected JSON data.'}), 400
        
        # Get bearer token from request
        bearer_token = data.get('bearerToken', '')
        
        if not bearer_token:
            return jsonify({'success': False, 'error': 'Bearer token is required'}), 400
        
        # Parse filters (same as export)
        time_frame = data.get('timeFrame', 'last_7_days')
        channel_ids = data.get('channelIds', [])
        content_type = data.get('contentType', 'all')
        
        # Calculate date range
        end_date = datetime.now()
        
        if time_frame == 'last_7_days':
            start_date = end_date - timedelta(days=7)
        elif time_frame == 'last_30_days':
            start_date = end_date - timedelta(days=30)
        elif time_frame == 'last_90_days':
            start_date = end_date - timedelta(days=90)
        elif time_frame == 'last_6_months':
            start_date = end_date - timedelta(days=180)
        elif time_frame == 'last_year':
            start_date = end_date - timedelta(days=365)
        elif time_frame == 'lifetime':
            # Fetch all videos - use a very old date (YouTube launched in 2005)
            start_date = datetime(2005, 1, 1)
        elif time_frame == 'this_month':
            start_date = end_date.replace(day=1)
        else:
            start_date = end_date - timedelta(days=7)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Quick fetch without transcripts for preview
        is_short = None
        if content_type == 'shorts':
            is_short = True
        elif content_type == 'videos':
            is_short = False
        
        print(f"\n=== Preview Request ===")
        print(f"Date Range: {start_date_str} to {end_date_str}")
        print(f"Channels: {len(channel_ids)} selected")
        print(f"Content Type: {content_type}")
        
        # Create exporter with user's token
        exporter = CSDataExporter(bearer_token)
        
        videos = exporter.fetch_videos(
            start_date=start_date_str,
            end_date=end_date_str,
            channel_ids=channel_ids if channel_ids else None,
            is_short=is_short if is_short is not None else False,
            include_transcripts=False  # Skip transcripts for preview
        )
        
        print(f"Preview result: {len(videos)} videos found")
        
        return jsonify({
            'success': True,
            'video_count': len(videos),
            'date_range': f"{start_date_str} to {end_date_str}"
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/send-to-slack', methods=['POST'])
def send_to_slack():
    """Find outlier videos and send to Slack"""
    try:
        print("\n" + "="*70)
        print("📨 SLACK NOTIFICATION REQUEST")
        print("="*70)
        
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request format'}), 400
        
        # Get configuration
        bearer_token = data.get('bearerToken', '')
        slack_webhook_url = data.get('slackWebhookUrl', '')
        days_back = int(data.get('daysBack', 7))
        category_filter = data.get('categoryFilter', 'all')
        long_form_threshold = int(data.get('longFormThreshold', 500000))
        shorts_threshold = int(data.get('shortsThreshold', 100000))
        
        if not bearer_token:
            return jsonify({'success': False, 'error': 'Bearer token is required'}), 400
        
        if not slack_webhook_url:
            return jsonify({'success': False, 'error': 'Slack webhook URL is required'}), 400
        
        print(f"✅ Configuration:")
        print(f"   Days back: {days_back}")
        print(f"   Category filter: {category_filter}")
        print(f"   Long-form threshold: {long_form_threshold:,}")
        print(f"   Shorts threshold: {shorts_threshold:,}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        print(f"📅 Date range: {start_date_str} to {end_date_str}")
        
        # Create exporter and fetch videos
        exporter = CSDataExporter(bearer_token)
        
        # First, fetch channels with categories to build mapping
        print("📡 Fetching channels and categories...")
        channel_to_category = {}
        categories_available = False
        try:
            channels_response = http_requests.get(
                "https://confucius.zero1creatorstudio.com/api/user/channels",
                headers={
                    "Authorization": f"Bearer {bearer_token}",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            # Build channel_id to category mapping
            if channels_response.status_code == 200:
                channels_data = channels_response.json()
                channels_list = channels_data if isinstance(channels_data, list) else channels_data.get('data', channels_data.get('channels', []))
                
                for channel in channels_list:
                    channel_id = channel.get('channel_id', channel.get('id', ''))
                    category = channel.get('category', channel.get('categoryName', ''))
                    if channel_id and category:
                        channel_to_category[channel_id] = category
                
                if channel_to_category:
                    categories_available = True
                    print(f"✅ Mapped {len(channel_to_category)} channels to categories")
                else:
                    print(f"⚠️ No categories found in response")
        except Exception as e:
            print(f"⚠️ Could not fetch channel categories: {e}")
            print(f"   Continuing without category information...")
            categories_available = False
        
        # Fetch all videos (both shorts and long-form)
        print("📡 Fetching videos...")
        videos = exporter.fetch_videos(
            start_date=start_date_str,
            end_date=end_date_str,
            channel_ids=None,
            sort_by='views',
            is_short=False,
            include_transcripts=False
        )
        
        shorts = exporter.fetch_videos(
            start_date=start_date_str,
            end_date=end_date_str,
            channel_ids=None,
            sort_by='views',
            is_short=True,
            include_transcripts=False
        )
        
        print(f"✅ Fetched {len(videos)} long-form videos and {len(shorts)} shorts")
        
        # Filter by category and view thresholds
        high_performing_videos = []
        high_performing_shorts = []
        
        # Long-form: views > custom threshold
        for video in videos:
            views = int(video.get('views', video.get('view_count', 0)) or 0)
            
            # Get channel info
            channel_id = video.get('channel_id', '')
            channel_name = video.get('channel_title', 'Unknown')
            
            # Get category from mapping (if available)
            video_category = channel_to_category.get(channel_id, '') if categories_available else ''
            
            # Filter by category if not "all" and categories are available
            if categories_available and category_filter != 'all' and video_category:
                if video_category.lower().replace(' ', '_') != category_filter:
                    continue
            
            # Check if views meet threshold
            if views >= long_form_threshold:
                video_data = {
                    'title': video.get('title', 'Untitled'),
                    'channel': channel_name,
                    'views': views,
                    'url': f"https://youtube.com/watch?v={video.get('video_id', '')}",
                    'published': video.get('published_at', ''),
                    'thumbnail': video.get('thumbnail_url', video.get('thumbnails', {}).get('high', {}).get('url', '')),
                    'type': 'Long-form'
                }
                # Only include category if available
                if categories_available and video_category:
                    video_data['category'] = video_category
                high_performing_videos.append(video_data)
        
        # Shorts: views > custom threshold
        for video in shorts:
            views = int(video.get('views', video.get('view_count', 0)) or 0)
            
            # Get channel info
            channel_id = video.get('channel_id', '')
            channel_name = video.get('channel_title', 'Unknown')
            
            # Get category from mapping (if available)
            video_category = channel_to_category.get(channel_id, '') if categories_available else ''
            
            # Filter by category if not "all" and categories are available
            if categories_available and category_filter != 'all' and video_category:
                if video_category.lower().replace(' ', '_') != category_filter:
                    continue
            
            # Check if views meet threshold
            if views >= shorts_threshold:
                video_data = {
                    'title': video.get('title', 'Untitled'),
                    'channel': channel_name,
                    'views': views,
                    'url': f"https://youtube.com/shorts/{video.get('video_id', '')}",
                    'published': video.get('published_at', ''),
                    'thumbnail': video.get('thumbnail_url', video.get('thumbnails', {}).get('high', {}).get('url', '')),
                    'type': 'Short'
                }
                # Only include category if available
                if categories_available and video_category:
                    video_data['category'] = video_category
                high_performing_shorts.append(video_data)
        
        print(f"🎯 Found {len(high_performing_videos)} high-performing long-form videos")
        print(f"🎯 Found {len(high_performing_shorts)} high-performing shorts")
        
        if not high_performing_videos and not high_performing_shorts:
            return jsonify({
                'success': True,
                'message': 'No high-performing videos found matching criteria',
                'videos_found': 0
            })
        
        # Sort each type by views
        high_performing_videos_sorted = sorted(
            high_performing_videos,
            key=lambda x: x['views'],
            reverse=True
        )
        
        high_performing_shorts_sorted = sorted(
            high_performing_shorts,
            key=lambda x: x['views'],
            reverse=True
        )
        
        # Get category name for display
        category_names = {
            'indian_finance': 'Indian Finance',
            'global_finance': 'Global Finance',
            'business_case_studies': 'Business Case Studies',
            'podcasts': 'Podcasts',
            'others': 'Others',
            'all': 'All Categories'
        }
        category_display = category_names.get(category_filter, category_filter)
        
        total_videos = len(high_performing_videos_sorted) + len(high_performing_shorts_sorted)
        
        # Format Slack message
        slack_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"High-Performing Videos - Last {days_back} Days"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Found {total_videos} videos in {category_display}*\nLong-form: {len(high_performing_videos_sorted)} | Shorts: {len(high_performing_shorts_sorted)}"
                }
            },
            {"type": "divider"}
        ]
        
        # Add Long-form Videos Section
        if high_performing_videos_sorted:
            slack_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*LONG-FORM VIDEOS ({len(high_performing_videos_sorted)})*"
                }
            })
            
            # Build bullet list for long-form
            lf_bullets = []
            for i, video in enumerate(high_performing_videos_sorted, 1):
                views_formatted = f"{video['views']:,}"
                published_date = video['published'][:10] if video['published'] else 'Unknown'
                bullet = f"• *{video['title']}*\n  Channel: {video['channel']}\n  Views: {views_formatted}"
                # Only add category if available
                if 'category' in video:
                    bullet += f"\n  Category: {video['category']}"
                bullet += f"\n  Published: {published_date}\n  <{video['url']}|Watch>"
                lf_bullets.append(bullet)
            
            # Slack has a limit of ~3000 chars per text block, so split if needed
            slack_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n\n".join(lf_bullets)
                }
            })
            
            slack_blocks.append({"type": "divider"})
        
        # Add Shorts Section
        if high_performing_shorts_sorted:
            slack_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*SHORT-FORM VIDEOS ({len(high_performing_shorts_sorted)})*"
                }
            })
            
            # Build bullet list for shorts
            sf_bullets = []
            for i, video in enumerate(high_performing_shorts_sorted, 1):
                views_formatted = f"{video['views']:,}"
                published_date = video['published'][:10] if video['published'] else 'Unknown'
                bullet = f"• *{video['title']}*\n  Channel: {video['channel']}\n  Views: {views_formatted}"
                # Only add category if available
                if 'category' in video:
                    bullet += f"\n  Category: {video['category']}"
                bullet += f"\n  Published: {published_date}\n  <{video['url']}|Watch>"
                sf_bullets.append(bullet)
            
            slack_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n\n".join(sf_bullets)
                }
            })
        
        # Send to Slack
        print(f"📤 Sending to Slack...")
        slack_payload = {
            "blocks": slack_blocks,
            "text": f"Found {total_videos} high-performing videos"
        }
        
        response = http_requests.post(
            slack_webhook_url,
            json=slack_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Slack notification sent successfully")
            return jsonify({
                'success': True,
                'message': f'Sent {total_videos} high-performing videos to Slack',
                'videos_found': total_videos,
                'long_form': len(high_performing_videos_sorted),
                'shorts': len(high_performing_shorts_sorted)
            })
        else:
            print(f"❌ Slack API error: {response.status_code}")
            return jsonify({
                'success': False,
                'error': f'Slack webhook returned status {response.status_code}'
            }), 500
        
    except Exception as e:
        print(f"❌ Error sending to Slack: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scheduler/config', methods=['GET', 'POST'])
def scheduler_config():
    """Get or set scheduler configuration"""
    try:
        if request.method == 'GET':
            config = load_scheduler_config()
            if config:
                # Don't send bearer token to frontend for security
                safe_config = config.copy()
                safe_config['bearer_token'] = '***' if config.get('bearer_token') else ''
                return jsonify({'success': True, 'config': safe_config})
            else:
                return jsonify({'success': True, 'config': None})
        
        elif request.method == 'POST':
            data = request.get_json(silent=True)
            if not data:
                return jsonify({'success': False, 'error': 'Invalid request format'}), 400
            
            # Validate required fields if enabling
            if data.get('enabled'):
                required_fields = ['bearer_token', 'webhook_url']
                missing = [f for f in required_fields if not data.get(f)]
                if missing:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required fields: {", ".join(missing)}'
                    }), 400
            
            # Save configuration
            config = {
                'enabled': data.get('enabled', False),
                'bearer_token': data.get('bearer_token', ''),
                'webhook_url': data.get('webhook_url', ''),
                'days_back': int(data.get('days_back', 7)),
                'category_filter': data.get('category_filter', 'all'),
                'long_form_threshold': int(data.get('long_form_threshold', 500000)),
                'shorts_threshold': int(data.get('shorts_threshold', 100000)),
                'interval_days': int(data.get('interval_days', 3))
            }
            
            if save_scheduler_config(config):
                # Update scheduler
                if config['enabled']:
                    # Remove existing job if any
                    if scheduler.get_job('slack_notification'):
                        scheduler.remove_job('slack_notification')
                    
                    # Add new job
                    scheduler.add_job(
                        func=scheduled_slack_notification,
                        trigger=IntervalTrigger(days=config['interval_days']),
                        id='slack_notification',
                        name='Slack Notification',
                        replace_existing=True
                    )
                    print(f"✅ Scheduler enabled - will run every {config['interval_days']} days")
                else:
                    # Disable scheduler
                    if scheduler.get_job('slack_notification'):
                        scheduler.remove_job('slack_notification')
                    print("⏸️ Scheduler disabled")
                
                return jsonify({'success': True, 'message': 'Configuration saved'})
            else:
                return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
    
    except Exception as e:
        print(f"Error in scheduler config: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scheduler/trigger', methods=['POST'])
def trigger_scheduler():
    """Manually trigger the scheduled task"""
    try:
        scheduled_slack_notification()
        return jsonify({'success': True, 'message': 'Scheduled task triggered'})
    except Exception as e:
        print(f"Error triggering scheduler: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# Load scheduler configuration on startup
startup_config = load_scheduler_config()
if startup_config and startup_config.get('enabled'):
    try:
        scheduler.add_job(
            func=scheduled_slack_notification,
            trigger=IntervalTrigger(days=startup_config.get('interval_days', 3)),
            id='slack_notification',
            name='Slack Notification',
            replace_existing=True
        )
        print(f"✅ Scheduler loaded from config - will run every {startup_config.get('interval_days', 3)} days")
    except Exception as e:
        print(f"⚠️ Failed to start scheduler: {e}")


if __name__ == '__main__':
    # Get port from environment variable (for Railway) or default to 8080
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    print("\n" + "=" * 70)
    print("Creator Studio Data Exporter - Web UI")
    print("=" * 70)
    print(f"\n🌐 Starting server on port: {port}")
    print(f"\n📝 Open your browser and go to: http://localhost:{port}")
    print("\n✨ Features:")
    print("  • Select channels to export")
    print("  • Filter by time frame, content type, views, outlier score")
    print("  • Sort by different metrics")
    print("  • Automatic transcript fetching")
    print("  • Download Excel files directly")
    print("  • Automated Slack notifications")
    print("\n" + "=" * 70 + "\n")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
