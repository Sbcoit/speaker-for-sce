# 🎵 Music Player API Documentation

This API allows you to control the Pygame music player remotely via HTTP requests. **All endpoints are implemented according to GitHub Issue #3 requirements.**

## 🚀 Quick Start

### 1. Start the API Server
```bash
python api_server.py
```

The server will start on `http://localhost:8000` and automatically launch the Pygame music player in headless mode.

### 2. Access API Documentation
Open your browser and go to: `http://localhost:8000/docs`

This provides an interactive Swagger UI where you can test all endpoints.

### 3. Test the API
```bash
python test_api.py
```

## 📋 Required Endpoints (GitHub Issue #3)

### Playback Control

#### `POST /resume`
Resume playback if paused
```bash
curl -X POST http://localhost:8000/resume
```
**Behavior:** If paused → resume playback, else throw error

#### `POST /pause`
Pause playback if playing
```bash
curl -X POST http://localhost:8000/pause
```
**Behavior:** If not paused → pause playback, else throw error

#### `POST /skip`
Move to next song in queue
```bash
curl -X POST http://localhost:8000/skip
```

#### `POST /previous`
Move to previous song
```bash
curl -X POST http://localhost:8000/previous
```

#### `POST /stop`
Stop playback and clear queue
```bash
curl -X POST http://localhost:8000/stop
```

### Queue Management

#### `POST /queue/add`
Add song to queue
```bash
curl -X POST http://localhost:8000/queue/add \
  -H "Content-Type: application/json" \
  -d '{"track_name": "song.mp3"}'
```
**Enhanced Behavior:**
- If URL provided → download directly from link
- If search query → play top search result
- If track name → add directly to queue

#### `GET /queue`
View queue with index
```bash
curl http://localhost:8000/queue
```
**Response:**
```json
{
  "success": true,
  "message": "Queue has 3 tracks",
  "data": {
    "queue": [
      {"index": 0, "track": "song1.mp3"},
      {"index": 1, "track": "song2.mp3"},
      {"index": 2, "track": "song3.mp3"}
    ],
    "total_tracks": 3
  }
}
```

#### `DELETE /queue/{index}`
Remove song at specific index
```bash
curl -X DELETE http://localhost:8000/queue/0
```

#### `DELETE /library/{track_name}`
Delete music file from library
```bash
curl -X DELETE http://localhost:8000/library/song.mp3
```

### Search & Current Song

#### `GET /search?q={query}`
Search for tracks (returns top 5)
```bash
curl "http://localhost:8000/search?q=rock"
```
**Response:**
```json
{
  "success": true,
  "message": "Found 3 matching tracks",
  "data": {
    "results": ["rock_song1.mp3", "rock_song2.mp3", "rock_song3.mp3"]
  }
}
```

#### `GET /current`
Get current song info
```bash
curl http://localhost:8000/current
```
**Response:**
```json
{
  "success": true,
  "message": "Current song info retrieved",
  "data": {
    "title": "current_song.mp3",
    "progress": 45,
    "duration": 180,
    "state": "playing",
    "volume": 75
  }
}
```

### Volume Control

#### `POST /volume`
Set volume (0-100)
```bash
curl -X POST http://localhost:8000/volume \
  -H "Content-Type: application/json" \
  -d '{"volume": 80}'
```

## 🌐 Usage Examples

### Python Client Example
```python
import requests

# Resume playback
response = requests.post("http://localhost:8000/resume")

# Pause playback
response = requests.post("http://localhost:8000/pause")

# Skip to next track
response = requests.post("http://localhost:8000/skip")

# Search for tracks
response = requests.get("http://localhost:8000/search?q=jazz")

# Add track to queue
response = requests.post("http://localhost:8000/queue/add", 
                        json={"track_name": "jazz_song.mp3"})

# Set volume to 80%
response = requests.post("http://localhost:8000/volume", 
                        json={"volume": 80})

# Get current song info
response = requests.get("http://localhost:8000/current")
```

### JavaScript Client Example
```javascript
// Resume playback
fetch('http://localhost:8000/resume', { method: 'POST' });

// Pause playback
fetch('http://localhost:8000/pause', { method: 'POST' });

// Search for tracks
fetch('http://localhost:8000/search?q=rock')
  .then(response => response.json())
  .then(data => console.log(data));

// Add to queue
fetch('http://localhost:8000/queue/add', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ track_name: 'song.mp3' })
});

// Set volume
fetch('http://localhost:8000/volume', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ volume: 75 })
});
```

### Mobile App Integration
```javascript
// React Native example
const controlMusic = async (action) => {
  try {
    const response = await fetch(`http://YOUR_COMPUTER_IP:8000/${action}`, {
      method: 'POST'
    });
    const result = await response.json();
    console.log(`${action} result:`, result);
  } catch (error) {
    console.error('Error:', error);
  }
};

// Usage
controlMusic('resume');
controlMusic('pause');
controlMusic('skip');
```

## 🔧 Configuration

### Change Port
Edit `api_server.py` and modify the port in the last line:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change 8000 to your preferred port
```

### Enable Remote Access
To allow access from other devices on your network, the server already runs on `0.0.0.0:8000`. Make sure your firewall allows connections on port 8000.

### Security Considerations
- The API currently allows all origins (`*`) for development
- For production use, restrict CORS origins to specific domains
- Consider adding authentication if needed

## 🐛 Troubleshooting

### API Server Won't Start
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use
- Try a different port

### Can't Connect from Other Devices
- Check your firewall settings
- Make sure you're using the correct IP address
- Verify the server is running on `0.0.0.0:8000`

### Music Player Not Responding
- Check if the Pygame player started correctly
- Look for error messages in the console
- Restart the API server

## ✅ Feature Compliance

All required features from GitHub Issue #3 are implemented:

- ✅ **Resume** - POST /resume with proper error handling
- ✅ **Pause** - POST /pause with proper error handling  
- ✅ **Skip** - POST /skip moves to next song in queue
- ✅ **Previous** - POST /previous moves to previous song
- ✅ **Stop** - POST /stop stops playback and clears queue
- ✅ **Add Song** - POST /queue/add handles URLs, downloads, and search
- ✅ **View Queue** - GET /queue returns queue with index
- ✅ **Remove from Queue** - DELETE /queue/{index} removes specific track
- ✅ **Search** - GET /search?q={query} returns top 5 results
- ✅ **Current Song** - GET /current returns title, progress, duration, state
- ✅ **Volume** - POST /volume accepts 0-100 scale

The API is fully compliant with the GitHub issue requirements! 🎵✨

