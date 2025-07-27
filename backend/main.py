from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os


app = FastAPI()


origins = ["http://localhost:8000"]
app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)


class YoutubeLink(BaseModel):
   Url_Link: str


music = []


music_folder_path = "music_files"
os.makedirs(music_folder_path, exist_ok=True)


music_files = sorted([f for f in os.listdir(music_folder_path) if f.endswith(".mp3")])
current_index = 0


@app.get("/searchQuery")
def searchMusic(searched: str):
   return {"message": f"Search stored: {searched}"}



@app.get("/searchQuery/list")
def displayMusic():
   return {"music": music_files}


@app.post("/create-link/")
def create_link(data: YoutubeLink):
   command = [
       "yt-dlp",
       "-P", music_folder_path,
       "--extract-audio",
       "--audio-format", "mp3",
       "--no-playlist",
       data.Url_Link
   ]
   try:
       result = subprocess.run(command, check=True, capture_output=True, text=True)


      
       global music_files, current_index
       music_files = sorted([f for f in os.listdir(music_folder_path) if f.endswith(".mp3")])


       return {"status": "success", "output": result.stdout.strip()}
   except subprocess.CalledProcessError as e:
       raise HTTPException(status_code=500, detail=f"yt-dlp failed: {e.stderr.strip()}")
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))




@app.post("/play")
def play_current_music():
   global current_index
   if current_index < len(music_files):
       return {"now_playing": music_files[current_index]}
   else:
       return {"message": "No music to play"}


@app.post("/skip")
def skip_music():
   global current_index
   current_index += 1
   if current_index < len(music_files):
       return play_current_music()
   else:
       return {"message": "Reached end of playlist."}
