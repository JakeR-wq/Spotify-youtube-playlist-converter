from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from ytmusicapi import YTMusic
import os

# Declare environment variables for the Spotify API
os.environ['SPOTIPY_CLIENT_ID'] = 'yours'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'yourappsecret'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:9090'

# Initialize Spotify and YouTube Music clients
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
yt_music = YTMusic("oauth.json")

def convert_spotify_to_ytmusic(playlist_url):
    # Extract playlist ID from URL
    playlist_id = playlist_url.split('/')[-1].split('?')[0]
    
    # Get total number of tracks in the Spotify playlist
    spotify_playlist = sp.playlist(playlist_id)
    total_tracks = spotify_playlist['tracks']['total']
    print(total_tracks)
    
    # Check if playlist name exists
    playlist_title = "baller playlist"
    if 'name' in spotify_playlist:
        playlist_title = spotify_playlist['name']
    
    # Fetch tracks in batches of 100
    offset = 0
    ytmusic_tracks = []
    not_found_tracks = []
    i = 0
    while offset < total_tracks:
        if i >= total_tracks:
            break
        try:
            spotify_tracks = sp.playlist_tracks(playlist_id, offset=offset)['items']
        except Exception as e:
            print(f"Error fetching tracks: {e}")
            continue
        
        for track in spotify_tracks:
            try:
                track_name = track['track']['name']
                artists = [artist['name'] for artist in track['track']['artists']]
                artist_str = ', '.join(artists)
                query = f"{track_name} {artist_str}"
                print(query)
                ytmusic_search_results = yt_music.search(query)
                if ytmusic_search_results:
                    first_result = ytmusic_search_results[0]
                    ytmusic_tracks.append(first_result)
                else:
                    not_found_tracks.append(query)
            except KeyError as e:
                print(f"Error processing track: {e}")
                continue
            i += 1
        offset += 100
    
    # Create a playlist on YouTube Music
    description = "Converted from Spotify playlist"
    ytmusic_playlist_id = yt_music.create_playlist(playlist_title, description,privacy_status='public')
    
    # Create a list to store video IDs
    video_ids = []

    # Extract video IDs from each track and add them to the list
    for track in ytmusic_tracks:
        if 'videoId' in track:
            video_ids.append(track['videoId'])
            print(track['videoId'])

    # Add the list of video IDs to the playlist
    yt_music.add_playlist_items(ytmusic_playlist_id, video_ids, duplicates=True)

    print(f"Playlist '{playlist_title}' successfully converted and created on YouTube Music!")
    
    # Print out tracks not found on YouTube Music
    if not_found_tracks:
        print("\nTracks not found on YouTube Music:")
        for track in not_found_tracks:
            print(track)


url='yourplaylisturlehere'

convert_spotify_to_ytmusic(url)
