from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import threading
import time
import os
import sys
import asyncio

from main import MusicPlayer

app = FastAPI(title="Music Player API", description="Remote control API for Pygame Music Player")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

music_player = None

class YouTubeURL(BaseModel):
    url: str

class SearchQuery(BaseModel):
    query: str

class VolumeRequest(BaseModel):
    volume: int  

class QueueTrack(BaseModel):
    track_name: str

class BluetoothDevice(BaseModel):
    device_index: int

class ControlRequest(BaseModel):
    action: str

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

def init_music_player():
    global music_player
    try:
        music_player = MusicPlayer(headless=True)
        print("✅ Music player initialized in headless mode")
    except Exception as e:
        print(f"❌ Error initializing music player: {e}")
        music_player = None

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Music Player API...")
    init_music_player()

@app.get("/", response_model=Response)
async def root():
    return Response(
        success=True,
        message="Music Player API is running",
        data={"status": "active"}
    )

@app.get("/status", response_model=Response)
async def get_status():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    return Response(
        success=True,
        message="Player status retrieved",
        data={
            "is_playing": music_player.is_playing,
            "current_track": music_player.current_track,
            "volume": int(music_player.volume * 100),
            "queue_length": len(music_player.queue),
            "repeat_mode": music_player.repeat_mode,
            "connected_device": music_player.connected_device["name"] if music_player.connected_device else None
        }
    )

@app.post("/resume", response_model=Response)
async def resume_playback():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        if not music_player.is_playing:
            music_player.unpause_music()
            return Response(success=True, message="Playback resumed")
        else:
            return Response(success=False, message="Music is already playing")
    except Exception as e:
        return Response(success=False, message=f"Error resuming playback: {str(e)}")

@app.post("/pause", response_model=Response)
async def pause_playback():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        if music_player.is_playing:
            music_player.pause_music()
            return Response(success=True, message="Playback paused")
        else:
            return Response(success=False, message="Music is already paused")
    except Exception as e:
        return Response(success=False, message=f"Error pausing playback: {str(e)}")

@app.post("/skip", response_model=Response)
async def skip_track():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        music_player.skip_track()
        return Response(success=True, message="Skipped to next track")
    except Exception as e:
        return Response(success=False, message=f"Error skipping track: {str(e)}")

@app.post("/previous", response_model=Response)
async def previous_track():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        music_player.previous_track()
        return Response(success=True, message="Moved to previous track")
    except Exception as e:
        return Response(success=False, message=f"Error moving to previous track: {str(e)}")

@app.post("/stop", response_model=Response)
async def stop_playback():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        music_player.stop_music()
        music_player.clear_queue()
        return Response(success=True, message="Playback stopped and queue cleared")
    except Exception as e:
        return Response(success=False, message=f"Error stopping playback: {str(e)}")

@app.get("/current", response_model=Response)
async def get_current_song():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        current_pos = 0
        if music_player.is_playing and music_player.current_track:
            current_pos = 0 
        
        return Response(
            success=True,
            message="Current song info retrieved",
            data={
                "title": music_player.current_track,
                "progress": current_pos,  
                "duration": 0,  
                "state": "playing" if music_player.is_playing else "paused",
                "volume": int(music_player.volume * 100)
            }
        )
    except Exception as e:
        return Response(success=False, message=f"Error getting current song info: {str(e)}")

@app.post("/volume", response_model=Response)
async def set_volume(request: VolumeRequest):
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        volume_float = max(0, min(100, request.volume)) / 100.0
        music_player.set_volume(volume_float)
        return Response(
            success=True, 
            message=f"Volume set to {request.volume}%",
            data={"volume": request.volume}
        )
    except Exception as e:
        return Response(success=False, message=f"Error setting volume: {str(e)}")

@app.get("/search", response_model=Response)
async def search_tracks(query: str = Query(..., alias="q")):
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        music_player.search_music(query)
        top_results = music_player.search_results[:5]
        return Response(
            success=True,
            message=f"Found {len(top_results)} matching tracks",
            data={"results": top_results}
        )
    except Exception as e:
        return Response(success=False, message=f"Error searching tracks: {str(e)}")

@app.post("/queue/add", response_model=Response)
async def add_to_queue(request: QueueTrack):
    """Add track to queue - enhanced to handle URLs and search"""
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        track_name = request.track_name
        
        # Check if it's a URL (YouTube link)
        if "youtube.com" in track_name or "youtu.be" in track_name:
            # Download from URL
            success = music_player.download_from_youtube(track_name)
            if success:
                # Get the latest downloaded track
                latest_track = music_player.music_files[-1] if music_player.music_files else None
                if latest_track:
                    music_player.add_to_queue(latest_track)
                    return Response(
                        success=True,
                        message=f"Downloaded and added '{latest_track}' to queue",
                        data={"queue_length": len(music_player.queue)}
                    )
                else:
                    return Response(success=False, message="Download failed")
            else:
                return Response(success=False, message="Failed to download from URL")
        else:
            # Checks if search query
            if track_name not in music_player.music_files:
                # Search for track
                music_player.search_music(track_name)
                if music_player.search_results:
                    # Add top result
                    top_result = music_player.search_results[0]
                    music_player.add_to_queue(top_result)
                    return Response(
                        success=True,
                        message=f"Added top search result '{top_result}' to queue",
                        data={"queue_length": len(music_player.queue)}
                    )
                else:
                    return Response(success=False, message="No tracks found matching the query")
            else:
                music_player.add_to_queue(track_name)
                return Response(
                    success=True,
                    message=f"Added '{track_name}' to queue",
                    data={"queue_length": len(music_player.queue)}
                )
    except Exception as e:
        return Response(success=False, message=f"Error adding to queue: {str(e)}")

@app.get("/queue", response_model=Response)
async def get_queue():
    """Get current queue with index"""
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        queue_with_index = []
        for i, track in enumerate(music_player.queue):
            queue_with_index.append({
                "index": i,
                "track": track
            })
        
        return Response(
            success=True,
            message=f"Queue has {len(music_player.queue)} tracks",
            data={
                "queue": queue_with_index,
                "total_tracks": len(music_player.queue)
            }
        )
    except Exception as e:
        return Response(success=False, message=f"Error getting queue: {str(e)}")

@app.delete("/queue/{index}", response_model=Response)
async def remove_from_queue(index: int):
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        if 0 <= index < len(music_player.queue):
            removed_track = music_player.queue[index]
            music_player.remove_from_queue(index)
            return Response(
                success=True,
                message=f"Removed '{removed_track}' from queue",
                data={"queue_length": len(music_player.queue)}
            )
        else:
            return Response(success=False, message=f"Invalid index {index}. Queue has {len(music_player.queue)} tracks")
    except Exception as e:
        return Response(success=False, message=f"Error removing from queue: {str(e)}")

@app.delete("/library/{track_name}", response_model=Response)
async def delete_music_file(track_name: str):
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        success = music_player.delete_music_file(track_name)
        if success:
            return Response(
                success=True,
                message=f"Deleted '{track_name}' from music library",
                data={"tracks_count": len(music_player.music_files)}
            )
        else:
            return Response(success=False, message=f"Failed to delete '{track_name}' - file not found")
    except Exception as e:
        return Response(success=False, message=f"Error deleting file: {str(e)}")

@app.post("/control", response_model=Response)
async def control_player(request: ControlRequest):
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    action = request.action.lower()
    
    try:
        if action == "play":
            if music_player.queue:
                music_player.play_from_queue()
            elif music_player.music_files:
                file_path = os.path.join(music_player.music_folder, music_player.music_files[music_player.current_index])
                music_player.play_music(file_path)
            else:
                return Response(success=False, message="No music files available")
        
        elif action == "pause":
            music_player.pause_music()
        
        elif action == "stop":
            music_player.stop_music()
        
        elif action == "next":
            music_player.skip_track()
        
        elif action == "previous":
            music_player.previous_track()
        
        elif action == "repeat":
            music_player.toggle_repeat_mode()
        
        else:
            return Response(success=False, message=f"Unknown action: {action}")
        
        return Response(success=True, message=f"Action '{action}' executed successfully")
    
    except Exception as e:
        return Response(success=False, message=f"Error executing action: {str(e)}")

@app.get("/tracks", response_model=Response)
async def get_tracks():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    return Response(
        success=True,
        message=f"Found {len(music_player.music_files)} tracks",
        data={"tracks": music_player.music_files}
    )

@app.post("/download", response_model=Response)
async def download_from_youtube(request: YouTubeURL):
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        success = music_player.download_from_youtube(request.url)
        if success:
            return Response(
                success=True,
                message="Download completed successfully",
                data={"tracks_count": len(music_player.music_files)}
            )
        else:
            return Response(success=False, message="Download failed")
    except Exception as e:
        return Response(success=False, message=f"Error downloading: {str(e)}")

@app.delete("/queue/clear", response_model=Response)
async def clear_queue():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        music_player.clear_queue()
        return Response(success=True, message="Queue cleared")
    except Exception as e:
        return Response(success=False, message=f"Error clearing queue: {str(e)}")

@app.get("/bluetooth/devices", response_model=Response)
async def get_bluetooth_devices():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    return Response(
        success=True,
        message=f"Found {len(music_player.bluetooth_devices)} Bluetooth devices",
        data={"devices": music_player.bluetooth_devices}
    )

@app.post("/bluetooth/connect", response_model=Response)
async def connect_bluetooth(request: BluetoothDevice):
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        music_player.connect_bluetooth_device(request.device_index)
        device = music_player.connected_device
        return Response(
            success=True,
            message=f"Connected to {device['name']}",
            data={"connected_device": device}
        )
    except Exception as e:
        return Response(success=False, message=f"Error connecting to device: {str(e)}")

@app.post("/bluetooth/disconnect", response_model=Response)
async def disconnect_bluetooth():
    if not music_player:
        raise HTTPException(status_code=503, detail="Music player not initialized")
    
    try:
        music_player.disconnect_bluetooth()
        return Response(success=True, message="Disconnected from Bluetooth device")
    except Exception as e:
        return Response(success=False, message=f"Error disconnecting: {str(e)}")

if __name__ == "__main__":
    print("🎵 Starting Music Player API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 