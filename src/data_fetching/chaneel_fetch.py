from datetime import datetime, timezone
import re
from datetime import datetime, timezone
from bson import ObjectId
import isodate
from src.utils.commons import youtube, connect_to_mongodb, mongo_conn  # Import the required modules


class Yotube_Data_Fetching:

    def __init__(self):
        pass

    def get_channel_id_from_video_url(self, youtube_connection, video_url):  
        try:
            # Extract the video ID from the URL using regular expression
            video_id_match = re.search(r'(?:youtu.be\/|youtube.com\/(?:v|e(?:mbed)?)\/|youtube.com\/watch\?v=)([a-zA-Z0-9_-]{11})', video_url)
            
            if video_id_match:
                video_id = video_id_match.group(1)

                # Request to get video details
                request = youtube_connection.videos().list(
                    part="snippet",
                    id=video_id
                )

                # Execute the request
                response = request.execute()

                # Extract channel ID from the response
                if 'items' in response and len(response['items']) > 0:
                    channel_id = response['items'][0]['snippet']['channelId']
                    return channel_id
                else:
                    return None
            else:
                return "Invalid YouTube video URL"
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def parse_duration_to_seconds(self, duration):
        try:
            duration = isodate.parse_duration(duration)
            return int(duration.total_seconds())
        except Exception as e:
            print(f'Error parsing duration {duration}: {e}')
            return 0

    def get_video_statistics(self, video_id):
        try:
            video_response = youtube.videos().list(part='statistics,contentDetails', id=video_id).execute()
            video_info = video_response.get('items', [])[0] if 'items' in video_response else {}
            stats = video_info.get('statistics', {})
            details = video_info.get('contentDetails', {})
            
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            duration = details.get('duration', 'PT0S')
            duration_seconds = self.parse_duration_to_seconds(duration)
            
            return likes, comments, duration_seconds
        except Exception as e:
            print(f'Error fetching video data for ID {video_id}: {e}')
            return 0, 0, 0

    

    def get_channel_statistics(self, channel_id, start_date):
        try:
            # Ensure start_date is timezone-aware (assume it's in UTC)
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            
            db = connect_to_mongodb(mongo_conn)

            # Check if the channel_id already exists in MongoDB
            existing_channel = db['youtube_channel_data'].find_one({'channel_id': channel_id})
            if existing_channel:
                print(existing_channel['channel_details'], "((((((((((()))))))))))")
                print(f"Channel ID {channel_id} already exists. Skipping data fetch.")
                return  existing_channel['channel_details']
            channel_response = youtube.channels().list(part='snippet,contentDetails,statistics', id=channel_id).execute()
            channel_info = channel_response.get('items', [])[0] if 'items' in channel_response else {}

            if channel_info:
                snippet = channel_info.get('snippet', {})
                statistics = channel_info.get('statistics', {})
                content_details = channel_info.get('contentDetails', {})
                
                # Fetch channel start date
                channel_start_date = snippet.get('publishedAt', 'NA')
                channel_start_date = datetime.fromisoformat(channel_start_date.replace('Z', '+00:00'))
                
                # Ensure the channel start date is timezone-aware
                if channel_start_date.tzinfo is None:
                    channel_start_date = channel_start_date.replace(tzinfo=timezone.utc)
                    
                # Use the user start date for filtering
                uploads_playlist_id = content_details.get('relatedPlaylists', {}).get('uploads', 'NA')
                
                if uploads_playlist_id == 'NA':
                    print(f'No uploads playlist found for channel ID {channel_id}.')
                    return
                
                total_likes = 0
                total_comments = 0
                short_videos_count = 0
                long_videos_count = 0
                
                next_page_token = None
                while True:
                    playlist_items_response = youtube.playlistItems().list(
                        part='contentDetails,snippet',
                        playlistId=uploads_playlist_id,
                        maxResults=50,
                        pageToken=next_page_token
                    ).execute()
                    
                    items = playlist_items_response.get('items', [])
                    for item in items:
                        video_id = item['contentDetails']['videoId']
                        video_upload_date = item['snippet'].get('publishedAt', 'NA')
                        video_upload_date = datetime.fromisoformat(video_upload_date.replace('Z', '+00:00'))
                        
                        # Ensure video upload date is timezone-aware
                        if video_upload_date.tzinfo is None:
                            video_upload_date = video_upload_date.replace(tzinfo=timezone.utc)

                        if video_upload_date >= start_date:
                            likes, comments, duration_seconds = self.get_video_statistics(video_id)
                            total_likes += likes
                            total_comments += comments
                            if duration_seconds < 60:
                                short_videos_count += 1
                            else:
                                long_videos_count += 1
                    
                    next_page_token = playlist_items_response.get('nextPageToken')
                    if not next_page_token:
                        break
                
                # Define the nested structure
                channel_data = {
                    'channel_id': channel_id,
                    'channel_details': {
                        'channel_name': snippet.get('title', 'NA'),
                        'channel_start_date': channel_start_date.isoformat(),
                        'inception_date': start_date.isoformat(),
                        'total_no_of_videos': statistics.get('videoCount', 'NA'),
                        'total_no_short_videos': short_videos_count,
                        'total_no_long_videos': long_videos_count,
                        'total_views': statistics.get('viewCount', 'NA'),
                        'total_likes': total_likes,
                        'total_comments': total_comments,
                        'total_subscribers': statistics.get('subscriberCount', 'NA'),
                    }
                }

                # Insert or update the data in MongoDB
                collection = db['youtube_channel_data']  # Replace with your collection name
                collection.update_one(
                    {'channel_id': channel_id},  # Use channel_id as unique identifier
                    {'$set': channel_data},
                    upsert=True
                )
                print(f'Data for channel ID {channel_id} inserted/updated in MongoDB.')
                return channel_data
            else:
                print(f'Channel with ID {channel_id} not found or no data available.')

        except Exception as e:
            print(f'Error fetching channel data for ID {channel_id}: {e}')



