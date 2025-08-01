import pygame, pygame.scrap
import pyperclip
import os
import subprocess
import sys
import threading
import time
import json
from typing import List, Optional, Dict
from collections import deque

class MusicPlayer:
    def __init__(self, headless=False):
        pygame.init()
        pygame.mixer.init()
        pygame.scrap.init()
        
        self.headless = headless
        
        self.WIDTH = 1000
        self.HEIGHT = 800
        
        if not self.headless:
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("Advanced Music Player")
        else:
            # Set a dummy display for headless mode
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            self.screen = pygame.display.set_mode((1, 1))
        
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.DARK_GRAY = (64, 64, 64)
        self.BLUE = (0, 100, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (128, 0, 128)
        
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
        
        self.music_folder = "music_files"
        os.makedirs(self.music_folder, exist_ok=True)
        self.music_files = []
        self.current_index = 0
        self.is_playing = False
        self.volume = 0.7
        self.current_track = ""
        
        self.queue = deque()
        self.queue_index = 0
        self.repeat_mode = "none"
        
        self.search_query = ""
        self.search_results = []
        self.search_active = False
        self.show_search_results = False
        
        self.bluetooth_devices = []
        self.connected_device = None
        self.bluetooth_active = False
        
        self.buttons = {}
        self.input_box = ""
        self.input_active = False
        self.scroll_offset = 0
        self.max_scroll = 0
        self.queue_scroll = 0
        self.search_scroll = 0
        
        self.prev_mouse_pressed = False
        
        self.refresh_music_files()
        pygame.mixer.music.set_volume(self.volume)
        self.init_bluetooth()
    
    def init_bluetooth(self):
        self.bluetooth_devices = [
            {"name": "JBL Flip 5", "address": "00:11:22:33:44:55", "connected": False},
            {"name": "Sony WH-1000XM4", "address": "AA:BB:CC:DD:EE:FF", "connected": False},
            {"name": "AirPods Pro", "address": "11:22:33:44:55:66", "connected": False},
            {"name": "Bose QuietComfort", "address": "22:33:44:55:66:77", "connected": False}
        ]
    
    def refresh_music_files(self):
        self.music_files = sorted([f for f in os.listdir(self.music_folder) if f.endswith(".mp3")])
        self.max_scroll = max(0, len(self.music_files) - 10)
    
    def search_music(self, query: str):
        if not query.strip():
            self.search_results = []
            return
        
        query = query.lower()
        self.search_results = [
            track for track in self.music_files 
            if query in track.lower()
        ]
    
    def add_to_queue(self, track_name: str):
        if track_name in self.music_files and track_name not in self.queue:
            self.queue.append(track_name)
    
    def remove_from_queue(self, index: int):
        if 0 <= index < len(self.queue):
            self.queue.remove(self.queue[index])
    
    def delete_music_file(self, track_name: str):
        try:
            file_path = os.path.join(self.music_folder, track_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.refresh_music_files()
                if track_name == self.current_track:
                    self.stop_music()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {track_name}: {e}")
            return False
    
    def clear_queue(self):
        self.queue.clear()
        self.queue_index = 0
    
    def play_from_queue(self):
        if self.queue:
            track_name = self.queue[self.queue_index]
            file_path = os.path.join(self.music_folder, track_name)
            if self.play_music(file_path):
                self.current_track = track_name
                return True
        return False
    
    def next_in_queue(self):
        if self.queue:
            self.queue_index = (self.queue_index + 1) % len(self.queue)
            self.play_from_queue()
    
    def previous_in_queue(self):
        if self.queue:
            self.queue_index = (self.queue_index - 1) % len(self.queue)
            self.play_from_queue()
    
    def connect_bluetooth_device(self, device_index: int):
        if 0 <= device_index < len(self.bluetooth_devices):
            for device in self.bluetooth_devices:
                device["connected"] = False
            
            self.bluetooth_devices[device_index]["connected"] = True
            self.connected_device = self.bluetooth_devices[device_index]
    
    def disconnect_bluetooth(self):
        if self.connected_device:
            self.connected_device["connected"] = False
            self.connected_device = None
    
    def play_music(self, file_path: str) -> bool:
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
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
        except Exception as e:
            print(f"Error stopping music: {e}")
    
    def pause_music(self):
        try:
            pygame.mixer.music.pause()
            self.is_playing = False
        except Exception as e:
            print(f"Error pausing music: {e}")
    
    def unpause_music(self):
        try:
            pygame.mixer.music.unpause()
            self.is_playing = True
        except Exception as e:
            print(f"Error unpausing music: {e}")
    
    def skip_track(self):
        if self.queue:
            self.next_in_queue()
        elif self.music_files:
            self.stop_music()
            self.current_index = (self.current_index + 1) % len(self.music_files)
            file_path = os.path.join(self.music_folder, self.music_files[self.current_index])
            self.play_music(file_path)
    
    def previous_track(self):
        if self.queue:
            self.previous_in_queue()
        elif self.music_files:
            self.stop_music()
            self.current_index = (self.current_index - 1) % len(self.music_files)
            file_path = os.path.join(self.music_folder, self.music_files[self.current_index])
            self.play_music(file_path)
    
    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def toggle_repeat_mode(self):
        modes = ["none", "one", "all"]
        current_index = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_index + 1) % len(modes)]
    
    def download_from_youtube(self, url: str):
        if not url.strip():
            return False
        
        command = ["yt-dlp", "-P", self.music_folder, "--extract-audio", "--audio-format", "mp3", "--no-playlist", url]
        
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
        if self.headless:
            return False
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        clicked = False
        if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
            pygame.draw.rect(self.screen, hover_color, (x, y, width, height))
            if mouse_pressed and not self.prev_mouse_pressed:
                clicked = True
        else:
            pygame.draw.rect(self.screen, color, (x, y, width, height))
        text_surface = self.font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        return clicked
    
    def draw_small_button(self, text: str, x: int, y: int, width: int, height: int, color: tuple, hover_color: tuple):
        if self.headless:
            return False
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        clicked = False
        if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
            pygame.draw.rect(self.screen, hover_color, (x, y, width, height))
            if mouse_pressed and not self.prev_mouse_pressed:
                clicked = True
        else:
            pygame.draw.rect(self.screen, color, (x, y, width, height))
        text_surface = self.small_font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        return clicked
    
    def draw_input_box(self, x: int, y: int, width: int, height: int, text: str, active: bool):
        """Draw an input box and handle input"""
        if self.headless:
            return
            
        font = pygame.font.Font(None, 28)
        color = self.BLUE if active else self.GRAY

        # Draw box
        pygame.draw.rect(self.screen, color, (x, y, width, height), 2)

        # Set max text width inside box (subtract padding)
        max_width = width - 10

        # Default to full text
        visible_text = text

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
        if self.headless:
            return
            
        pygame.draw.rect(self.screen, self.DARK_GRAY, (x, y, width, height))
        
        volume_width = int(width * self.volume)
        pygame.draw.rect(self.screen, self.BLUE, (x, y, volume_width, height))
        
        volume_text = self.small_font.render(f"{int(self.volume * 100)}%", True, self.WHITE)
        self.screen.blit(volume_text, (x + width + 10, y))
    
    def draw_track_list(self, x: int, y: int, width: int, height: int, tracks: List[str], current_track: str, scroll_offset: int, show_delete_buttons=False):
        if self.headless:
            return None
            
        pygame.draw.rect(self.screen, self.DARK_GRAY, (x, y, width, height))
        
        clicked_track = None
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height:
                relative_y = mouse_pos[1] - y
                track_index = relative_y // 30
                if track_index < len(tracks) and track_index >= 0:
                    clicked_track = tracks[track_index]
        
        visible_tracks = tracks[scroll_offset:scroll_offset + 10]
        for i, track in enumerate(visible_tracks):
            track_y = y + i * 30
            if track_y + 30 > y + height:
                break
            
            if track == current_track:
                pygame.draw.rect(self.screen, self.BLUE, (x, track_y, width, 30))
            
            if x <= mouse_pos[0] <= x + width and track_y <= mouse_pos[1] <= track_y + 30:
                pygame.draw.rect(self.screen, self.GRAY, (x, track_y, width, 30))
            
            text_width = width - 60 if show_delete_buttons else width - 20
            max_chars = text_width // 8
            if len(track) > max_chars:
                display_text = track[:max_chars-3] + "..."
            else:
                display_text = track
            
            track_text = self.small_font.render(display_text, True, self.WHITE)
            self.screen.blit(track_text, (x + 5, track_y + 5))
            
            if show_delete_buttons:
                delete_btn = self.draw_small_button("DEL", x + width - 50, track_y + 5, 45, 20, self.RED, (200, 0, 0))
                if delete_btn:
                    self.delete_music_file(track)
        
        return clicked_track
    
    def draw_bluetooth_devices(self, x: int, y: int, width: int, height: int):
        if self.headless:
            return
            
        pygame.draw.rect(self.screen, self.DARK_GRAY, (x, y, width, height))
        
        title = self.small_font.render("Bluetooth Devices:", True, self.WHITE)
        self.screen.blit(title, (x + 5, y + 5))
        
        for i, device in enumerate(self.bluetooth_devices):
            device_y = y + 30 + i * 25
            if device_y + 25 > y + height:
                break
            
            color = self.GREEN if device["connected"] else self.WHITE
            
            name_text = self.small_font.render(device["name"], True, color)
            self.screen.blit(name_text, (x + 5, device_y))
            
            btn_text = "Disconnect" if device["connected"] else "Connect"
            btn_color = self.RED if device["connected"] else self.GREEN
            btn_hover = (200, 0, 0) if device["connected"] else (0, 200, 0)
            
            btn_clicked = self.draw_small_button(btn_text, x + width - 80, device_y, 75, 20, btn_color, btn_hover)
            if btn_clicked:
                if device["connected"]:
                    self.disconnect_bluetooth()
                else:
                    self.connect_bluetooth_device(i)
    
    def handle_events(self):
        if self.headless:
            return True
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if 50 <= event.pos[0] <= 550 and 70 <= event.pos[1] <= 100:
                        self.input_active = True
                        self.search_active = False
                    elif 50 <= event.pos[0] <= 350 and 140 <= event.pos[1] <= 170:
                        self.input_active = False
                        self.search_active = True
                    elif 50 <= event.pos[0] <= 350 and 210 <= event.pos[1] <= 230:
                        self.input_active = False
                        self.search_active = False
                        volume_x = event.pos[0] - 50
                        self.set_volume(volume_x / 300)
                    else:
                        self.input_active = False
                        self.search_active = False

            elif event.type == pygame.KEYDOWN:
                # Check for paste first (Command+V or Ctrl+V)
                if (event.key == pygame.K_v and 
                    ((pygame.key.get_mods() & pygame.KMOD_CTRL) or
                    (pygame.key.get_mods() & pygame.KMOD_META))):
                    try:
                        clipboard = pyperclip.paste()
                        if clipboard:
                            if self.input_active:
                                self.input_box += clipboard
                            elif self.search_active:
                                self.search_query += clipboard
                    except Exception as e:
                        print(f"Clipboard error: {e}")
                else:
                    if self.input_active:
                        if event.key == pygame.K_ESCAPE:
                            self.input_box = ""
                        elif event.key == pygame.K_RETURN:
                            if self.input_box.strip():
                                success = self.download_from_youtube(self.input_box)
                                if success:
                                    self.input_box = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_box = self.input_box[:-1]
                        else:
                            self.input_box += event.unicode
                    
                    elif self.search_active:
                        if event.key == pygame.K_ESCAPE:
                            self.search_query = ""
                            self.show_search_results = False
                        elif event.key == pygame.K_RETURN:
                            if self.search_query.strip():
                                self.search_music(self.search_query)
                                self.show_search_results = True
                        elif event.key == pygame.K_BACKSPACE:
                            self.search_query = self.search_query[:-1]
                        else:
                            self.search_query += event.unicode

            elif event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                if 50 <= mouse_pos[0] <= 450 and 370 <= mouse_pos[1] <= 620:
                    self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y))
                elif 470 <= mouse_pos[0] <= 870 and 370 <= mouse_pos[1] <= 620:
                    self.queue_scroll = max(0, min(len(self.queue) - 10, self.queue_scroll - event.y))
                elif 50 <= mouse_pos[0] <= 450 and 370 <= mouse_pos[1] <= 620 and self.show_search_results:
                    self.search_scroll = max(0, min(len(self.search_results) - 10, self.search_scroll - event.y))

        return True
    
    def draw(self):
        if self.headless:
            return
            
        self.screen.fill(self.BLACK)
        
        title = self.font.render("Advanced Music Player", True, self.WHITE)
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 10))
        
        download_label = self.small_font.render("YouTube URL:", True, self.WHITE)
        self.screen.blit(download_label, (50, 50))
        
        self.draw_input_box(50, 70, 500, 30, self.input_box, self.input_active)
        
        download_btn = self.draw_button("Download", 570, 70, 100, 30, self.RED, (200, 0, 0))
        if download_btn:
            if self.input_box.strip():
                success = self.download_from_youtube(self.input_box)
                if success:
                    self.input_box = ""
        
        search_label = self.small_font.render("Search:", True, self.WHITE)
        self.screen.blit(search_label, (50, 120))
        
        self.draw_input_box(50, 140, 300, 30, self.search_query, self.search_active)
        
        search_btn = self.draw_button("Search", 370, 140, 80, 30, self.PURPLE, (100, 0, 100))
        if search_btn:
            if self.search_query.strip():
                self.search_music(self.search_query)
                self.show_search_results = True
        
        volume_label = self.small_font.render("Volume:", True, self.WHITE)
        self.screen.blit(volume_label, (50, 190))
        self.draw_volume_slider(50, 210, 300, 20)
        
        status_y = 250
        if self.current_track:
            track_text = self.small_font.render(f"Now Playing: {self.current_track}", True, self.WHITE)
            self.screen.blit(track_text, (50, status_y))
        
        repeat_text = self.small_font.render(f"Repeat: {self.repeat_mode.title()}", True, self.YELLOW)
        self.screen.blit(repeat_text, (50, status_y + 25))
        
        controls_y = 290
        current_time = time.time()
        
        play_btn = self.draw_button("Play" if not self.is_playing else "Pause", 50, controls_y, 80, 40, self.GREEN, (0, 200, 0))
        if play_btn:
            if self.is_playing:
                self.pause_music()
            else:
                if self.queue:
                    self.play_from_queue()
                elif self.music_files:
                    file_path = os.path.join(self.music_folder, self.music_files[self.current_index])
                    self.play_music(file_path)
        
        stop_btn = self.draw_button("Stop", 140, controls_y, 80, 40, self.RED, (200, 0, 0))
        if stop_btn:
            self.stop_music()
        
        prev_btn = self.draw_button("<<", 230, controls_y, 60, 40, self.BLUE, (0, 150, 255))
        if prev_btn:
            self.previous_track()
        
        next_btn = self.draw_button(">>", 300, controls_y, 60, 40, self.BLUE, (0, 150, 255))
        if next_btn:
            self.skip_track()
        
        repeat_btn = self.draw_button("RPT", 370, controls_y, 60, 40, self.YELLOW, (200, 200, 0))
        if repeat_btn:
            self.toggle_repeat_mode()
        
        queue_btn = self.draw_button("Add to Queue", 450, controls_y, 120, 40, self.PURPLE, (100, 0, 100))
        if queue_btn:
            if self.current_track:
                self.add_to_queue(self.current_track)
        
        clear_queue_btn = self.draw_button("Clear Queue", 580, controls_y, 100, 40, self.RED, (200, 0, 0))
        if clear_queue_btn:
            self.clear_queue()
        
        content_y = 350
        content_height = 250
        
        if not self.show_search_results:
            list_label = self.small_font.render("Music Library:", True, self.WHITE)
            self.screen.blit(list_label, (50, content_y))
            
            clicked_track = self.draw_track_list(50, content_y + 20, 400, content_height, self.music_files, self.current_track, self.scroll_offset, show_delete_buttons=True)
            if clicked_track:
                file_path = os.path.join(self.music_folder, clicked_track)
                self.play_music(file_path)
        else:
            list_label = self.small_font.render(f"Search Results ({len(self.search_results)}):", True, self.WHITE)
            self.screen.blit(list_label, (50, content_y))
            
            clicked_track = self.draw_track_list(50, content_y + 20, 400, content_height, self.search_results, self.current_track, self.search_scroll)
            if clicked_track:
                self.add_to_queue(clicked_track)
        
        queue_label = self.small_font.render(f"Queue ({len(self.queue)} tracks):", True, self.WHITE)
        self.screen.blit(queue_label, (470, content_y))
        
        clicked_queue_track = self.draw_track_list(470, content_y + 20, 400, content_height, list(self.queue), self.current_track, self.queue_scroll)
        if clicked_queue_track:
            try:
                queue_index = list(self.queue).index(clicked_queue_track)
                self.remove_from_queue(queue_index)
            except ValueError:
                pass
        
        bottom_y = 620
        
        bluetooth_label = self.small_font.render("Bluetooth Devices:", True, self.WHITE)
        self.screen.blit(bluetooth_label, (50, bottom_y))
        
        self.draw_bluetooth_devices(50, bottom_y + 20, 400, 60)
        
        if self.connected_device:
            connected_text = self.small_font.render(f"Connected: {self.connected_device['name']}", True, self.GREEN)
            self.screen.blit(connected_text, (470, bottom_y))
        
        instructions = [
            "Controls:",
            "• Download from YouTube URLs",
            "• Search music library", 
            "• Add tracks to queue",
            "• Connect Bluetooth devices",
            "• Use mouse wheel to scroll lists"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.tiny_font.render(instruction, True, self.GRAY)
            self.screen.blit(inst_text, (470, bottom_y + 20 + i * 15))
        
        pygame.display.flip()
        self.prev_mouse_pressed = pygame.mouse.get_pressed()[0]
    
    def run(self):
        if self.headless:
            while True:
                time.sleep(0.1)
        else:
            clock = pygame.time.Clock()
            running = True
            
            while running:
                running = self.handle_events()
                self.draw()
                clock.tick(60)
            
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    headless = "--headless" in sys.argv
    player = MusicPlayer(headless=headless)
    player.run()
