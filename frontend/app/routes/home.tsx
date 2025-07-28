import type { Route } from "./+types/home";
import { useState, useRef, useEffect } from "react";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Music Player" },
    { name: "description", content: "A simple music player interface" },
  ];
}

export default function Home() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [searchQuery, setSearchQuery] = useState("");
  const audioRef = useRef<HTMLAudioElement>(null);

  // Sample music data - you can replace with your own tracks
  const sampleTracks = [
    {
      id: 1,
      title: "Track 1",
      artist: "Artist 1",
      url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
    },
    {
      id: 2,
      title: "Track 2", 
      artist: "Artist 2",
      url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
    },
    {
      id: 3,
      title: "Track 3",
      artist: "Artist 3", 
      url: "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
    }
  ];

  const [currentTrack, setCurrentTrack] = useState(sampleTracks[0]);

  const filteredTracks = sampleTracks.filter(track =>
    track.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    track.artist.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnded = () => setIsPlaying(false);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const changeTrack = (track: typeof sampleTracks[0]) => {
    setCurrentTrack(track);
    setIsPlaying(false);
    setCurrentTime(0);
    if (audioRef.current) {
      audioRef.current.src = track.url;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-8">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-8 w-full max-w-4xl shadow-lg">
        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative">
            <input
              type="text"
              placeholder="Search tracks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-gray-500"
            />
            <div className="absolute right-3 top-3 text-gray-400">
              🔍
            </div>
          </div>
        </div>

        {/* Track Info */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-semibold text-white mb-2">{currentTrack.title}</h2>
          <p className="text-xl text-gray-300">{currentTrack.artist}</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-lg text-gray-400 mb-3">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
          <input
            type="range"
            min="0"
            max={duration || 0}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-3 bg-gray-600 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Controls */}
        <div className="flex justify-center items-center gap-8 mb-8">
          <button className="text-gray-300 hover:text-white text-2xl">
            ⏮
          </button>
          
          <button 
            onClick={togglePlay}
            className="bg-white text-gray-900 rounded-full p-4 hover:bg-gray-100 text-2xl"
          >
            {isPlaying ? "⏸" : "▶"}
          </button>

          <button className="text-gray-300 hover:text-white text-2xl">
            ⏭
          </button>
        </div>

        {/* Volume Control */}
        <div className="flex items-center gap-4 mb-8">
          <span className="text-gray-300 text-xl">🔊</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
            className="flex-1 h-3 bg-gray-600 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Track List */}
        <div>
          <h3 className="text-white font-medium mb-4 text-xl">Tracks</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTracks.map((track) => (
              <div
                key={track.id}
                onClick={() => changeTrack(track)}
                className={`p-4 rounded border cursor-pointer transition-colors ${
                  currentTrack.id === track.id 
                    ? 'bg-gray-700 border-gray-500' 
                    : 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                }`}
              >
                <div className="font-medium text-white text-lg">{track.title}</div>
                <div className="text-gray-300">{track.artist}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Hidden Audio Element */}
        <audio
          ref={audioRef}
          src={currentTrack.url}
          preload="metadata"
        />
      </div>
    </div>
  );
}
