#!/usr/bin/env python3
"""
Test script for the Music Player API
This script demonstrates how to control the Pygame music player remotely via HTTP requests
Tests all required endpoints from GitHub issue #3
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_api():
    """Test all API endpoints"""
    print("🎵 Testing Music Player API - GitHub Issue #3 Requirements")
    print("=" * 60)
    
    # Test 1: Check if API is running
    print("\n1. Testing API status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is running!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API error: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running with: python api_server.py")
        return
    
    # Test 2: Get player status
    print("\n2. Getting player status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Player status retrieved!")
            print(f"Current track: {status['data']['current_track']}")
            print(f"Playing: {status['data']['is_playing']}")
            print(f"Volume: {status['data']['volume']}%")
            print(f"Queue length: {status['data']['queue_length']}")
        else:
            print(f"❌ Status error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting status: {e}")
    
    # Test 3: Get current song info
    print("\n3. Getting current song info...")
    try:
        response = requests.get(f"{BASE_URL}/current")
        if response.status_code == 200:
            current = response.json()
            print("✅ Current song info retrieved!")
            print(f"Title: {current['data']['title']}")
            print(f"State: {current['data']['state']}")
            print(f"Progress: {current['data']['progress']}s")
            print(f"Volume: {current['data']['volume']}%")
        else:
            print(f"❌ Current song error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting current song: {e}")
    
    # Test 4: Volume control (0-100 scale)
    print("\n4. Testing volume control...")
    try:
        volume_data = {"volume": 75}
        response = requests.post(f"{BASE_URL}/volume", json=volume_data)
        if response.status_code == 200:
            volume_result = response.json()
            print(f"✅ Volume set to {volume_result['data']['volume']}%")
        else:
            print(f"❌ Volume error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error setting volume: {e}")
    
    # Test 5: Search functionality (GET with query parameter)
    print("\n5. Testing search functionality...")
    try:
        response = requests.get(f"{BASE_URL}/search?q=music")
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search completed! Found {len(search_results['data']['results'])} results")
            if search_results['data']['results']:
                print("Top results:")
                for i, result in enumerate(search_results['data']['results'][:3], 1):
                    print(f"  {i}. {result}")
        else:
            print(f"❌ Search error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error searching: {e}")
    
    # Test 6: Queue management
    print("\n6. Testing queue management...")
    try:
        # Get current queue
        response = requests.get(f"{BASE_URL}/queue")
        if response.status_code == 200:
            queue = response.json()
            print(f"✅ Current queue has {queue['data']['total_tracks']} tracks")
            if queue['data']['queue']:
                print("Queue contents:")
                for item in queue['data']['queue']:
                    print(f"  [{item['index']}] {item['track']}")
        
        # Clear queue
        response = requests.delete(f"{BASE_URL}/queue/clear")
        if response.status_code == 200:
            print("✅ Queue cleared!")
        else:
            print(f"❌ Clear queue error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error managing queue: {e}")
    
    # Test 7: Add to queue (enhanced functionality)
    print("\n7. Testing add to queue...")
    try:
        # Test adding a track name
        track_data = {"track_name": "test_song.mp3"}
        response = requests.post(f"{BASE_URL}/queue/add", json=track_data)
        if response.status_code == 200:
            add_result = response.json()
            print(f"✅ Added track to queue: {add_result['message']}")
        else:
            print(f"❌ Add to queue error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error adding to queue: {e}")
    
    # Test 8: Playback controls
    print("\n8. Testing playback controls...")
    try:
        # Test pause
        response = requests.post(f"{BASE_URL}/pause")
        if response.status_code == 200:
            pause_result = response.json()
            print(f"✅ Pause: {pause_result['message']}")
        else:
            print(f"❌ Pause error: {response.status_code}")
        
        time.sleep(1)
        
        # Test resume
        response = requests.post(f"{BASE_URL}/resume")
        if response.status_code == 200:
            resume_result = response.json()
            print(f"✅ Resume: {resume_result['message']}")
        else:
            print(f"❌ Resume error: {response.status_code}")
        
        time.sleep(1)
        
        # Test skip
        response = requests.post(f"{BASE_URL}/skip")
        if response.status_code == 200:
            skip_result = response.json()
            print(f"✅ Skip: {skip_result['message']}")
        else:
            print(f"❌ Skip error: {response.status_code}")
        
        time.sleep(1)
        
        # Test previous
        response = requests.post(f"{BASE_URL}/previous")
        if response.status_code == 200:
            prev_result = response.json()
            print(f"✅ Previous: {prev_result['message']}")
        else:
            print(f"❌ Previous error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error with playback controls: {e}")
    
    # Test 9: Stop functionality
    print("\n9. Testing stop functionality...")
    try:
        response = requests.post(f"{BASE_URL}/stop")
        if response.status_code == 200:
            stop_result = response.json()
            print(f"✅ Stop: {stop_result['message']}")
        else:
            print(f"❌ Stop error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error stopping: {e}")
    
    # Test 10: Remove from queue
    print("\n10. Testing remove from queue...")
    try:
        # First add a track to queue
        track_data = {"track_name": "test_song.mp3"}
        requests.post(f"{BASE_URL}/queue/add", json=track_data)
        
        # Then remove it
        response = requests.delete(f"{BASE_URL}/queue/0")
        if response.status_code == 200:
            remove_result = response.json()
            print(f"✅ Remove from queue: {remove_result['message']}")
        else:
            print(f"❌ Remove from queue error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error removing from queue: {e}")
    
    # Test 11: Delete music file
    print("\n11. Testing delete music file...")
    try:
        response = requests.delete(f"{BASE_URL}/library/test_song.mp3")
        if response.status_code == 200:
            delete_result = response.json()
            print(f"✅ Delete music file: {delete_result['message']}")
        else:
            print(f"❌ Delete music file error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error deleting music file: {e}")
    
    # Test 12: YouTube download (optional)
    print("\n12. Testing YouTube download...")
    print("⚠️  This test is commented out to avoid downloading files")
    print("   Uncomment the code below to test YouTube downloads")
    
    """
    try:
        # Example YouTube URL (uncomment to test)
        youtube_data = {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
        response = requests.post(f"{BASE_URL}/download", json=youtube_data)
        if response.status_code == 200:
            download_result = response.json()
            print(f"✅ Download completed! {download_result['message']}")
        else:
            print(f"❌ Download error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error downloading: {e}")
    """
    
    print("\n" + "=" * 60)
    print("🎉 API testing completed!")
    print("\n📋 Required endpoints from GitHub Issue #3:")
    print("  ✅ POST /resume              - Resume playback if paused")
    print("  ✅ POST /pause               - Pause playback if playing")
    print("  ✅ POST /skip                - Move to next song in queue")
    print("  ✅ POST /previous            - Move to previous song")
    print("  ✅ POST /stop                - Stop playback and clear queue")
    print("  ✅ POST /queue/add           - Add song (URL/download or search)")
    print("  ✅ GET  /queue               - View queue with index")
    print("  ✅ DELETE /queue/{index}     - Remove from queue")
    print("  ✅ GET  /search?q={query}    - Search (returns top 5)")
    print("  ✅ GET  /current             - Current song info")
    print("  ✅ POST /volume              - Set volume (0-100)")
    
    print("\n🌐 API Documentation available at: http://localhost:8000/docs")
    print("📖 Interactive testing available at: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api() 