"""
Creator Studio Data Exporter
Export YouTube video data from Zero1 Creator Studio to Excel
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Optional, List
import time
from openpyxl.utils import get_column_letter


class CSDataExporter:
    def __init__(self, bearer_token: str):
        """
        Initialize the CS Data Exporter
        
        Args:
            bearer_token: Your Bearer token for authentication
        """
        self.base_url = "https://confucius.zero1creatorstudio.com/api"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def fetch_transcript(self, video_id: str, video_title: str = "") -> Optional[dict]:
        """
        Fetch transcript for a single video
        
        Args:
            video_id: MongoDB video ID (not YouTube ID)
            video_title: Video title for logging
        
        Returns:
            Transcript data or None if not available
        """
        try:
            response = requests.get(
                f"{self.base_url}/videos/{video_id}/transcript",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 404:
                # Transcript not found or not ready
                return None
            else:
                print(f"  ⚠️  Transcript API returned status {response.status_code} for: {video_title[:50]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error fetching transcript: {e}")
            return None
    
    def fetch_videos(
        self,
        start_date: str,
        end_date: str,
        channel_ids: Optional[List[str]] = None,
        sort_by: str = "outlier_score",
        is_short: bool = False,
        limit: int = 100,
        include_transcripts: bool = True
    ) -> List[dict]:
        """
        Fetch videos from Creator Studio API
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            channel_ids: List of channel IDs to filter (optional)
            sort_by: Sort field (default: outlier_score)
            is_short: Filter for shorts (default: False)
            limit: Number of records per request (default: 100)
            include_transcripts: Fetch transcripts for each video (default: True)
        
        Returns:
            List of video dictionaries with transcripts
        """
        all_videos = []
        offset = 0
        
        # Build query parameters
        params = {
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
            "start": start_date,
            "end": end_date,
            "is_short": str(is_short).lower()
        }
        
        # Add channel IDs if provided
        if channel_ids:
            params["channel_ids"] = ",".join(channel_ids)
        
        print(f"Fetching videos from {start_date} to {end_date}...")
        
        while True:
            params["offset"] = offset
            
            try:
                response = requests.get(
                    f"{self.base_url}/user/videos",
                    headers=self.headers,
                    params=params
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, dict):
                    videos = data.get('data', data.get('videos', []))
                    total = data.get('total', 0)
                else:
                    videos = data
                    total = len(videos)
                
                if not videos:
                    break
                
                all_videos.extend(videos)
                print(f"Fetched {len(all_videos)} videos so far...")
                
                # Check if we've fetched all videos
                if len(videos) < limit:
                    break
                
                offset += limit
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break
        
        print(f"✓ Total videos fetched: {len(all_videos)}")
        
        # Fetch transcripts for each video if requested
        if include_transcripts and all_videos:
            print(f"\nFetching transcripts for {len(all_videos)} videos...")
            
            transcripts_fetched = 0
            transcripts_already_available = 0
            transcripts_not_available = 0
            
            for i, video in enumerate(all_videos, 1):
                # Use YouTube video ID for transcript API (not MongoDB ID!)
                youtube_video_id = video.get('video_id', '')
                video_title = video.get('title', 'Unknown')
                transcript_status = video.get('transcript_status', '')
                
                if not youtube_video_id:
                    continue
                
                # Show progress
                if i % 10 == 0 or i == 1:
                    print(f"  Progress: {i}/{len(all_videos)} videos processed...")
                
                # Check if transcript is already in the video object
                existing_transcript = video.get('transcript', '')
                
                if existing_transcript and isinstance(existing_transcript, str) and len(existing_transcript) > 50:
                    # Transcript already available in video object as string
                    video['transcript_text'] = existing_transcript
                    video['transcript_language'] = 'en'  # Default
                    video['transcript_status'] = transcript_status or 'available'
                    transcripts_already_available += 1
                else:
                    # Fetch transcript from API using YouTube video ID
                    try:
                        transcript_data = self.fetch_transcript(youtube_video_id, video_title)
                        
                        if transcript_data:
                            # Extract transcript from API response
                            if isinstance(transcript_data, dict):
                                # Check if transcript is a list of segments
                                transcript_raw = transcript_data.get('transcript', transcript_data.get('text', ''))
                                
                                if isinstance(transcript_raw, list):
                                    # Join all text segments into one string, filtering out None values
                                    transcript_text = ' '.join([
                                        str(seg.get('text', '') or '') 
                                        for seg in transcript_raw 
                                        if isinstance(seg, dict) and seg.get('text')
                                    ])
                                    video['transcript_text'] = transcript_text
                                    video['transcript_segments'] = transcript_raw  # Keep segments for reference
                                elif isinstance(transcript_raw, str):
                                    video['transcript_text'] = transcript_raw
                                else:
                                    video['transcript_text'] = str(transcript_raw) if transcript_raw else ''
                                
                                video['transcript_language'] = transcript_data.get('language', 'en')
                                video['transcript_status'] = 'fetched'
                                transcripts_fetched += 1
                            else:
                                video['transcript_text'] = ''
                                video['transcript_language'] = ''
                                video['transcript_status'] = 'unavailable'
                                transcripts_not_available += 1
                        else:
                            video['transcript_text'] = ''
                            video['transcript_language'] = ''
                            video['transcript_status'] = transcript_status or 'unavailable'
                            transcripts_not_available += 1
                    except Exception as e:
                        print(f"  ⚠️  Error processing transcript for {video_title[:50]}: {e}")
                        video['transcript_text'] = ''
                        video['transcript_language'] = ''
                        video['transcript_status'] = 'error'
                        transcripts_not_available += 1
                    
                    # Rate limiting - be nice to the API
                    time.sleep(0.3)
            
            print(f"\n✓ Transcript Summary:")
            print(f"  • Already available: {transcripts_already_available}")
            print(f"  • Newly fetched: {transcripts_fetched}")
            print(f"  • Not available: {transcripts_not_available}")
        
        return all_videos
    
    def flatten_video_data(self, videos: List[dict]) -> pd.DataFrame:
        """
        Flatten nested video data for Excel export
        
        Args:
            videos: List of video dictionaries
        
        Returns:
            Pandas DataFrame with flattened data
        """
        flattened_data = []
        
        for video in videos:
            flat_video = {
                # Basic info
                'video_id': str(video.get('id', '') or ''),
                'title': str(video.get('title', '') or 'Untitled'),
                'channel_id': str(video.get('channel_id', '') or ''),
                'channel_name': str(video.get('channel_name', video.get('channel', {}).get('name', '')) or ''),
                'published_at': str(video.get('published_at', video.get('publishedAt', '')) or ''),
                
                # Metrics - handle None values
                'views': int(video.get('views') or video.get('view_count') or 0),
                'likes': int(video.get('likes') or video.get('like_count') or 0),
                'comments_count': int(video.get('comments_count') or video.get('comment_count') or 0),
                'duration': str(video.get('duration', '') or ''),
                
                # Engagement
                'outlier_score': str(video.get('outlier_score', video.get('outlierScore', '')) or ''),
                'engagement_rate': str(video.get('engagement_rate', '') or ''),
                
                # Content
                'description': str(video.get('description', '') or ''),
                'tags': ', '.join([str(t) for t in video.get('tags', []) if t]) if isinstance(video.get('tags'), list) else str(video.get('tags', '') or ''),
                'category': str(video.get('category', '') or ''),
                
                # Status
                'is_short': video.get('is_short', video.get('isShort', False)),
                
                # URLs
                'url': f"https://youtube.com/watch?v={video.get('id', '')}" if video.get('id') else '',
                'thumbnail_url': str(video.get('thumbnail_url', video.get('thumbnail', '')) or ''),
            }
            
            # Add transcript if available - ensure all values are strings
            if 'transcript_text' in video:
                flat_video['transcript'] = str(video.get('transcript_text', '') or '')
                flat_video['transcript_language'] = str(video.get('transcript_language', '') or '')
                flat_video['transcript_status'] = str(video.get('transcript_status', '') or '')
            elif 'transcript' in video:
                transcript = video['transcript']
                if isinstance(transcript, dict):
                    flat_video['transcript'] = str(transcript.get('text', transcript.get('transcript', '')) or '')
                    flat_video['transcript_language'] = str(transcript.get('language', 'en') or 'en')
                    flat_video['transcript_status'] = str(video.get('transcript_status', 'available') or 'available')
                elif isinstance(transcript, str):
                    flat_video['transcript'] = transcript
                    flat_video['transcript_language'] = 'en'
                    flat_video['transcript_status'] = str(video.get('transcript_status', 'available') or 'available')
                else:
                    flat_video['transcript'] = ''
                    flat_video['transcript_language'] = ''
                    flat_video['transcript_status'] = 'unavailable'
            else:
                flat_video['transcript'] = ''
                flat_video['transcript_language'] = ''
                flat_video['transcript_status'] = 'not_fetched'
            
            # Add any other custom fields (sanitize column names)
            for key, value in video.items():
                if key not in flat_video and not isinstance(value, (dict, list)):
                    # Sanitize column names - remove invalid characters
                    clean_key = str(key).replace('[', '').replace(']', '').replace(':', '_').replace('/', '_')
                    flat_video[clean_key] = value
            
            flattened_data.append(flat_video)
        
        df = pd.DataFrame(flattened_data)
        
        # Additional sanitization of column names
        df.columns = [str(col).replace('[', '').replace(']', '').replace(':', '_').replace('/', '_') 
                      for col in df.columns]
        
        return df
    
    def export_to_excel(
        self,
        videos: List[dict],
        filename: Optional[str] = None,
        include_raw_data: bool = False
    ) -> str:
        """
        Export videos to Excel file
        
        Args:
            videos: List of video dictionaries
            filename: Output filename (optional, auto-generated if not provided)
            include_raw_data: Include raw JSON data sheet (default: False)
        
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cs_videos_export_{timestamp}.xlsx"
        
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        print(f"Preparing data for export...")
        df = self.flatten_video_data(videos)
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Videos', index=False)
            
            # Adjust column widths
            worksheet = writer.sheets['Videos']
            for idx, col in enumerate(df.columns, start=1):
                try:
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    column_letter = get_column_letter(idx)
                    worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
                except Exception as e:
                    # Skip column if there's an issue
                    print(f"  Warning: Could not adjust width for column '{col}': {e}")
            
            # Add raw data sheet if requested
            if include_raw_data:
                raw_df = pd.DataFrame({'raw_json': [json.dumps(v) for v in videos]})
                raw_df.to_excel(writer, sheet_name='Raw Data', index=False)
            
            # Add summary sheet
            summary_data = {
                'Metric': [
                    'Total Videos',
                    'Date Range',
                    'Total Views',
                    'Total Likes',
                    'Total Comments',
                    'Avg Views per Video',
                    'Export Date'
                ],
                'Value': [
                    len(videos),
                    f"{df['published_at'].min()} to {df['published_at'].max()}" if 'published_at' in df.columns else 'N/A',
                    df['views'].sum() if 'views' in df.columns else 0,
                    df['likes'].sum() if 'likes' in df.columns else 0,
                    df['comments_count'].sum() if 'comments_count' in df.columns else 0,
                    f"{df['views'].mean():.0f}" if 'views' in df.columns else 0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"✓ Data exported successfully to: {filename}")
        return filename
    
    def quick_export_last_n_days(
        self,
        days: int = 7,
        filename: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Quick export for last N days
        
        Args:
            days: Number of days to look back (default: 7)
            filename: Output filename (optional)
            **kwargs: Additional parameters for fetch_videos
        
        Returns:
            Path to the exported file
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        videos = self.fetch_videos(
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
        
        if not videos:
            print("No videos found for the specified date range.")
            return None
        
        return self.export_to_excel(videos, filename)


# Example usage
if __name__ == "__main__":
    # CONFIGURATION
    # Replace with your actual Bearer token
    BEARER_TOKEN = "your_bearer_token_here"
    
    # Initialize exporter
    exporter = CSDataExporter(BEARER_TOKEN)
    
    # Example 1: Export last 7 days
    print("=== Example 1: Last 7 days ===")
    exporter.quick_export_last_n_days(days=7, filename="last_7_days.xlsx")
    
    # Example 2: Custom date range with specific channels
    print("\n=== Example 2: Custom date range ===")
    videos = exporter.fetch_videos(
        start_date="2026-01-12",
        end_date="2026-01-19",
        sort_by="outlier_score",
        is_short=False
    )
    exporter.export_to_excel(videos, filename="custom_export.xlsx")
    
    # Example 3: With specific channel IDs
    print("\n=== Example 3: Specific channels ===")
    channel_ids = [
        "UCqW8jxh4tH1Z1sWPbkGWL4g",
        "UCBqvATpjSubtNxpqUDj4_cA"
        # Add more channel IDs as needed
    ]
    videos = exporter.fetch_videos(
        start_date="2026-01-12",
        end_date="2026-01-19",
        channel_ids=channel_ids,
        sort_by="outlier_score"
    )
    exporter.export_to_excel(videos, filename="specific_channels.xlsx")
