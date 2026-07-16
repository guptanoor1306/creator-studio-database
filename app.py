"""
Flask Web Application for Creator Studio Data Exporter
Provides a beautiful HTML UI for exporting data with filters
"""

from flask import Flask, render_template, request, jsonify, send_file
from cs_data_exporter import CSDataExporter
from channel_categories import categorize_channels, get_channel_category, get_category_info, CATEGORIES
from datetime import datetime, timedelta
import os
import traceback
import requests as http_requests

app = Flask(__name__)


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
        
        # Fetch categories from CS API
        categories_response = requests.get(
            "https://confucius.zero1creatorstudio.com/api/channel-categories",
            headers={
                "Authorization": f"Bearer {bearer_token}",
                "Accept": "application/json"
            }
        )
        
        # Fetch channels from CS API
        channels_response = requests.get(
            "https://confucius.zero1creatorstudio.com/api/user/channels",
            headers={
                "Authorization": f"Bearer {bearer_token}",
                "Accept": "application/json"
            }
        )
        
        if channels_response.status_code != 200:
            return jsonify({'success': False, 'error': f'Channels API returned status {channels_response.status_code}'})
        
        # Parse channels
        channels_data = channels_response.json()
        if isinstance(channels_data, list):
            channels_list = channels_data
        else:
            channels_list = channels_data.get('data', channels_data.get('channels', []))
        
        # Parse categories from CS API
        cs_categories = {}
        channel_to_category = {}
        
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
        indian_niche_only = data.get('indianNicheOnly', True)
        
        if not bearer_token:
            return jsonify({'success': False, 'error': 'Bearer token is required'}), 400
        
        if not slack_webhook_url:
            return jsonify({'success': False, 'error': 'Slack webhook URL is required'}), 400
        
        print(f"✅ Configuration:")
        print(f"   Days back: {days_back}")
        print(f"   Indian niche only: {indian_niche_only}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        print(f"📅 Date range: {start_date_str} to {end_date_str}")
        
        # Create exporter and fetch videos
        exporter = CSDataExporter(bearer_token)
        
        # Fetch all videos (both shorts and long-form)
        print("📡 Fetching videos...")
        videos = exporter.fetch_videos(
            start_date=start_date_str,
            end_date=end_date_str,
            channel_ids=None,
            sort_by='outlier_score',
            is_short=False,
            include_transcripts=False
        )
        
        shorts = exporter.fetch_videos(
            start_date=start_date_str,
            end_date=end_date_str,
            channel_ids=None,
            sort_by='outlier_score',
            is_short=True,
            include_transcripts=False
        )
        
        print(f"✅ Fetched {len(videos)} long-form videos and {len(shorts)} shorts")
        
        # Filter outliers
        outlier_videos = []
        outlier_shorts = []
        
        # Long-form: outliers OR views > 500K
        for video in videos:
            outlier_score = float(video.get('outlier_score', video.get('outlierScore', 0)) or 0)
            views = int(video.get('views', video.get('view_count', 0)) or 0)
            category = video.get('category', '').lower()
            
            # Check if it's Indian niche
            is_indian_niche = 'indian' in category or 'india' in video.get('channel_name', '').lower()
            
            if indian_niche_only and not is_indian_niche:
                continue
            
            # Check if it's an outlier (>2x) OR high views
            if outlier_score >= 2.0 or views >= 500000:
                outlier_videos.append({
                    'title': video.get('title', 'Untitled'),
                    'channel': video.get('channel_name', 'Unknown'),
                    'views': views,
                    'outlier_score': outlier_score,
                    'url': f"https://youtube.com/watch?v={video.get('video_id', '')}",
                    'published': video.get('published_at', ''),
                    'thumbnail': video.get('thumbnail_url', ''),
                    'type': 'Long-form'
                })
        
        # Shorts: outliers OR views > 100K
        for video in shorts:
            outlier_score = float(video.get('outlier_score', video.get('outlierScore', 0)) or 0)
            views = int(video.get('views', video.get('view_count', 0)) or 0)
            category = video.get('category', '').lower()
            
            is_indian_niche = 'indian' in category or 'india' in video.get('channel_name', '').lower()
            
            if indian_niche_only and not is_indian_niche:
                continue
            
            if outlier_score >= 2.0 or views >= 100000:
                outlier_shorts.append({
                    'title': video.get('title', 'Untitled'),
                    'channel': video.get('channel_name', 'Unknown'),
                    'views': views,
                    'outlier_score': outlier_score,
                    'url': f"https://youtube.com/watch?v={video.get('video_id', '')}",
                    'published': video.get('published_at', ''),
                    'thumbnail': video.get('thumbnail_url', ''),
                    'type': 'Short'
                })
        
        print(f"🎯 Found {len(outlier_videos)} outlier long-form videos")
        print(f"🎯 Found {len(outlier_shorts)} outlier shorts")
        
        if not outlier_videos and not outlier_shorts:
            return jsonify({
                'success': True,
                'message': 'No outliers found matching criteria',
                'videos_found': 0
            })
        
        # Sort by outlier score
        all_outliers = sorted(
            outlier_videos + outlier_shorts,
            key=lambda x: x['outlier_score'],
            reverse=True
        )[:20]  # Top 20
        
        # Format Slack message
        slack_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔥 Outlier Videos Alert - Last {days_back} Days"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Found *{len(all_outliers)}* outlier videos{' in Indian niche' if indian_niche_only else ''}\n_Long-form: {len(outlier_videos)} | Shorts: {len(outlier_shorts)}_"
                }
            },
            {"type": "divider"}
        ]
        
        # Add top videos
        for i, video in enumerate(all_outliers[:10], 1):
            views_formatted = f"{video['views']:,}"
            slack_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{i}. {video['title'][:100]}*\n📺 {video['channel']} | 👁️ {views_formatted} views | 🔥 {video['outlier_score']:.1f}x outlier\n🎬 {video['type']} | 📅 {video['published'][:10]}\n<{video['url']}|Watch on YouTube>"
                }
            })
            if video['thumbnail']:
                slack_blocks[-1]["accessory"] = {
                    "type": "image",
                    "image_url": video['thumbnail'],
                    "alt_text": "thumbnail"
                }
        
        # Send to Slack
        print(f"📤 Sending to Slack...")
        slack_payload = {
            "blocks": slack_blocks,
            "text": f"Found {len(all_outliers)} outlier videos"
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
                'message': f'Sent {len(all_outliers)} outlier videos to Slack',
                'videos_found': len(all_outliers),
                'long_form': len(outlier_videos),
                'shorts': len(outlier_shorts)
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
    print("\n" + "=" * 70 + "\n")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
