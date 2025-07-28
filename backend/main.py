import pygame, pygame.scrap
import pyperclip
import os
import subprocess
import sys
import threading
import time
from typing import List, Optional

class MusicPlayer:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        pygame.scrap.init()
        
        # Display settings
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Music Player")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.BLUE = (0, 100, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        
        # Font
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Music settings
        self.music_folder = "music_files"
        os.makedirs(self.music_folder, exist_ok=True)
        self.music_files = []
        self.current_index = 0
        self.is_playing = False
        self.volume = 0.7
        self.current_track = ""
        
        # UI elements
        self.buttons = {}
        self.input_box = ""
        self.input_active = False
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Load music files
        self.refresh_music_files()
        
        # Set initial volume
        pygame.mixer.music.set_volume(self.volume)
    
    def refresh_music_files(self):
        """Refresh the list of music files"""
        self.music_files = sorted([f for f in os.listdir(self.music_folder) if f.endswith(".mp3")])
        self.max_scroll = max(0, len(self.music_files) - 10)  # Show 10 tracks at a time
    
    def play_music(self, file_path: str) -> bool:
        """Play music using pygame"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.is_playing = True
            self.current_track = os.path.basename(file_path)
            return True
        except Exception as e:
            print(f"Error playing music: {e}")
            return False
    
    def stop_music(self):
        """Stop music playback"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
        except Exception as e:
            print(f"Error stopping music: {e}")
    
    def pause_music(self):
        """Pause music playback"""
        try:
            pygame.mixer.music.pause()
            self.is_playing = False
        except Exception as e:
            print(f"Error pausing music: {e}")
    
    def unpause_music(self):
        """Unpause music playback"""
        try:
            pygame.mixer.music.unpause()
            self.is_playing = True
        except Exception as e:
            print(f"Error unpausing music: {e}")
    
    def skip_track(self):
        """Skip to next track"""
        if self.music_files:
            self.stop_music()
            self.current_index = (self.current_index + 1) % len(self.music_files)
            file_path = os.path.join(self.music_folder, self.music_files[self.current_index])
            self.play_music(file_path)
    
    def previous_track(self):
        """Go to previous track"""
        if self.music_files:
            self.stop_music()
            self.current_index = (self.current_index - 1) % len(self.music_files)
            file_path = os.path.join(self.music_folder, self.music_files[self.current_index])
            self.play_music(file_path)
    
    def set_volume(self, volume: float):
        """Set music volume"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def download_from_youtube(self, url: str):
        """Download music from YouTube URL"""
        if not url.strip():
            return False
        
        command = [
            "yt-dlp",
            "-P", self.music_folder,
            "--extract-audio",
            "--audio-format", "mp3",
            "--no-playlist",
            url
        ]
        
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            self.refresh_music_files()
            return True
        except subprocess.CalledProcessError as e:
            print(f"Download failed: {e.stderr.strip()}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def draw_button(self, text: str, x: int, y: int, width: int, height: int, color: tuple, hover_color: tuple):
        """Draw a button and return if it's clicked"""
        mouse_pos = pygame.mouse.get_pos()
        clicked = False
        
        # Check if mouse is over button
        if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
            pygame.draw.rect(self.screen, hover_color, (x, y, width, height))
            if pygame.mouse.get_pressed()[0]:  # Left click
                clicked = True
        else:
            pygame.draw.rect(self.screen, color, (x, y, width, height))
        
        # Draw text
        text_surface = self.font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        
        return clicked
    
    def draw_input_box(self, x: int, y: int, width: int, height: int):
        """Draw an input box and handle input"""
        font = pygame.font.Font(None, 28)
        color = self.BLUE if self.input_active else self.GRAY

        # Draw box
        pygame.draw.rect(self.screen, color, (x, y, width, height), 2)

        # Set max text width inside box (subtract padding)
        max_width = width - 10

        # Default to full text
        visible_text = self.input_box

        # Clip left if text too wide
        text_surface = font.render(visible_text, True, self.WHITE)
        if text_surface.get_width() > max_width:
            for i in range(len(visible_text)):
                clipped = visible_text[i:]
                if font.render(clipped, True, self.WHITE).get_width() <= max_width:
                    visible_text = clipped
                    break

        # Render only visible part
        text_surface = font.render(visible_text, True, self.WHITE)
        self.screen.blit(text_surface, (x + 5, y + 5))

    
    def draw_volume_slider(self, x: int, y: int, width: int, height: int):
        """Draw volume slider"""
        # Background
        pygame.draw.rect(self.screen, self.DARK_GRAY, (x, y, width, height))
        
        # Volume level
        volume_width = int(width * self.volume)
        pygame.draw.rect(self.screen, self.BLUE, (x, y, volume_width, height))
        
        # Text
        volume_text = self.small_font.render(f"Volume: {int(self.volume * 100)}%", True, self.WHITE)
        self.screen.blit(volume_text, (x, y - 25))
    
    def draw_track_list(self, x: int, y: int, width: int, height: int):
        """Draw the track list"""
        # Background
        pygame.draw.rect(self.screen, self.DARK_GRAY, (x, y, width, height))
        
        # Draw tracks
        visible_tracks = self.music_files[self.scroll_offset:self.scroll_offset + 10]
        for i, track in enumerate(visible_tracks):
            track_y = y + i * 30
            if track_y + 30 > y + height:
                break
            
            # Highlight current track
            if track == self.current_track:
                pygame.draw.rect(self.screen, self.BLUE, (x, track_y, width, 30))
            
            # Truncate track name if too long
            max_chars = (width - 20) // 8  # Approximate characters that fit
            if len(track) > max_chars:
                display_text = track[:max_chars-3] + "..."
            else:
                display_text = track
            
            # Track text
            track_text = self.small_font.render(display_text, True, self.WHITE)
            self.screen.blit(track_text, (x + 5, track_y + 5))
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check input box click
                    if 50 <= event.pos[0] <= 550 and 50 <= event.pos[1] <= 80:
                        self.input_active = True
                    else:
                        self.input_active = False

                    # Check volume slider
                    if 50 <= event.pos[0] <= 350 and 120 <= event.pos[1] <= 140:
                        volume_x = event.pos[0] - 50
                        self.set_volume(volume_x / 300)

            elif event.type == pygame.KEYDOWN:
                if self.input_active:
                    if event.key == pygame.K_ESCAPE:
                        self.input_box = ""

                    # Paste with Command+V (macOS) or Ctrl+V (Windows/Linux)
                    elif (event.key == pygame.K_v and 
                        ((pygame.key.get_mods() & pygame.KMOD_CTRL) or
                        (pygame.key.get_mods() & pygame.KMOD_META))):  # Meta = ⌘ on macOS
                        try:
                            import pyperclip
                            clipboard = pyperclip.paste()
                            if clipboard:
                                self.input_box += clipboard
                        except Exception as e:
                            print(f"Clipboard error: {e}")

                    elif event.key == pygame.K_RETURN:
                        # Download from YouTube
                        if self.input_box.strip():
                            success = self.download_from_youtube(self.input_box)
                            if success:
                                self.input_box = ""

                    elif event.key == pygame.K_BACKSPACE:
                        self.input_box = self.input_box[:-1]

                    else:
                        self.input_box += event.unicode

            elif event.type == pygame.MOUSEWHEEL:
                # Scroll track list
                self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y))

        return True
    
    def draw(self):
        """Draw the main interface"""
        self.screen.fill(self.BLACK)
        
        # Title
        title = self.font.render("Music Player", True, self.WHITE)
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 10))
        
        # YouTube download section
        download_label = self.small_font.render("YouTube URL:", True, self.WHITE)
        self.screen.blit(download_label, (50, 30))
        
        self.draw_input_box(50, 50, 500, 30)
        
        download_btn = self.draw_button("Download", 570, 50, 100, 30, self.RED, (200, 0, 0))
        if download_btn:
            if self.input_box.strip():
                success = self.download_from_youtube(self.input_box)
                if success:
                    self.input_box = ""
        
        # Volume control
        self.draw_volume_slider(50, 120, 300, 20)
        
        # Current track info
        if self.current_track:
            track_text = self.small_font.render(f"Now Playing: {self.current_track}", True, self.WHITE)
            self.screen.blit(track_text, (50, 160))
        
        # Control buttons
        play_btn = self.draw_button("Play" if not self.is_playing else "Pause", 50, 200, 80, 40, self.GREEN, (0, 200, 0))
        if play_btn:
            if self.is_playing:
                self.pause_music()
            else:
                if self.music_files:
                    file_path = os.path.join(self.music_folder, self.music_files[self.current_index])
                    self.play_music(file_path)
        
        stop_btn = self.draw_button("Stop", 140, 200, 80, 40, self.RED, (200, 0, 0))
        if stop_btn:
            self.stop_music()
        
        prev_btn = self.draw_button("⏮", 230, 200, 60, 40, self.BLUE, (0, 150, 255))
        if prev_btn:
            self.previous_track()
        
        next_btn = self.draw_button("⏭", 300, 200, 60, 40, self.BLUE, (0, 150, 255))
        if next_btn:
            self.skip_track()
        
        # Track list
        list_label = self.small_font.render("Music Library:", True, self.WHITE)
        self.screen.blit(list_label, (50, 260))
        
        self.draw_track_list(50, 280, 400, 300)
        
        # Instructions
        instructions = [
            "Controls:",
            "• Click 'Download' to download from YouTube",
            "• Use Play/Pause/Stop buttons",
            "• Scroll mouse wheel to navigate tracks",
            "• Click volume slider to adjust volume"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, self.GRAY)
            self.screen.blit(inst_text, (470, 280 + i * 20))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    player = MusicPlayer()
    player.run()
