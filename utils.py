"""
Utility Functions for Music Player Application
Contains audio playback and data persistence functions.
"""

import pygame
import os
import pickle
from tkinter import messagebox
from models import Lagu, DoublyLinkedList

DATA_FILE = "music_player_data"






def save_data(library, playlists):
    """
    Save library and playlists to file using pickle.
    
    Args:
        library: SinglyLinkedList containing all songs
        playlists: Dictionary of playlist names to DoublyLinkedList objects
    """
    data_to_save = {
        'library': library,
        'playlists': playlists
    }
    try:
        with open(DATA_FILE, 'wb') as f:
            pickle.dump(data_to_save, f)
        print(f"Data berhasil disimpan ke {DATA_FILE}")
    except Exception as e:
        messagebox.showerror("Error Penyimpanan", f"Gagal menyimpan data ke {DATA_FILE}.\nError: {e}")
        print(f"Error saat menyimpan data: {e}")


def load_data():
    """
    Load library and playlists from file using pickle.
    
    Returns:
        Dictionary containing 'library' and 'playlists' or None if file not found
    """
    try:
        with open(DATA_FILE, 'rb') as f:
            data = pickle.load(f)
        print(f"Data berhasil dimuat dari {DATA_FILE}")
        

        return data
    except FileNotFoundError:
        print(f"File {DATA_FILE} tidak ditemukan. Akan dibuat saat data pertama kali disimpan.")
        return None
    except Exception as e:
        messagebox.showerror("Error Pemuatan", f"Gagal memuat data dari {DATA_FILE}.\nError: {e}")
        print(f"Error saat memuat data: {e}")
        return None


def load_dummy_data(library, playlists):
    """
    Load dummy data for first-time initialization.
    
    Args:
        library: SinglyLinkedList to populate with dummy songs
        playlists: Dictionary to populate with dummy playlists
    """
    # Create dummy songs (without actual audio files, but with durations)
    lagu1 = Lagu("S001", "Lagu Indah", "Artis A", "Album 1", "Pop", 2020, None)  # 3:35
    lagu2 = Lagu("S002", "Musik Ceria", "Artis B", "Album 2", "Rock", 2019, None)  # 4:05
    lagu3 = Lagu("S003", "Melodi Malam", "Artis A", "Album 3", "Jazz", 2021, None)  # 3:18
    lagu4 = Lagu("S004", "Ritme Petualang", "Artis C", "Album 4", "Electronic", 2022, None)  # 5:02
    lagu5 = Lagu("S005", "Harmoni Hujan", "Artis D", "Album 5", "Ambient", 2018, None)  # 4:27

    library.append(lagu1)
    library.append(lagu2)
    library.append(lagu3)
    library.append(lagu4)
    library.append(lagu5)

    # Create a favorite playlist
    playlist_fav = DoublyLinkedList()
    playlist_fav.append(lagu1)
    playlist_fav.append(lagu3)
    playlists["Lagu Favorit Saya"] = playlist_fav


def get_duration_seconds(file_path):
    """Return duration of audio file in seconds.

    Tries mutagen first (if installed) for accurate duration; falls back to
    pygame.mixer.Sound if available. Returns None on failure.
    """
    # Try mutagen for robust metadata parsing
    try:
        from mutagen import File as MutagenFile
        audio = MutagenFile(file_path)
        if audio and hasattr(audio.info, 'length'):
            return int(audio.info.length)
    except Exception:
        pass

    # Fallback: pygame.mixer.Sound
    try:
        # Ensure mixer initialized
        if not pygame.get_init():
            pygame.init()
        snd = pygame.mixer.Sound(file_path)
        length = snd.get_length()
        return int(length)
    except Exception:
        return None


# Audio playback functions
def play_file(lagu, playback_state):
    """
    Load and play an audio file using pygame.
    
    Args:
        lagu: Lagu object to play
        playback_state: Dictionary containing playback state information
    
    Returns:
        bool: True if playback started successfully, False otherwise
    """
    if lagu and lagu.file_path and os.path.isfile(lagu.file_path):
        try:
            pygame.mixer.music.load(lagu.file_path)
            pygame.mixer.music.play()
            playback_state['current_playing'] = lagu
            playback_state['current_file_path'] = lagu.file_path
            playback_state['is_playing'] = True
            # Try to determine duration and store in playback_state
            try:
                dur = get_duration_seconds(lagu.file_path)
                playback_state['duration_seconds'] = dur
            except Exception:
                playback_state['duration_seconds'] = None
            

            
            # Update history
            if playback_state.get('_previous_playing'):
                playback_state['history'].push(playback_state['_previous_playing'])
            playback_state['_previous_playing'] = lagu
            
            print(f"Memutar: {lagu.judul} dari {lagu.file_path}")
            return True
        except pygame.error as e:
            messagebox.showerror("Error Audio", f"Tidak dapat memutar file {lagu.file_path}.\nError: {e}")
            print(f"Pygame error saat memutar {lagu.file_path}: {e}")
            return False
    else:
        # Don't show messagebox for autoplay failures, just print
        print(f"File tidak ditemukan: {lagu.file_path}")
        playback_state['is_playing'] = False  # Mark as not playing
        return False


def stop_file(playback_state):
    """
    Stop audio playback using pygame.
    
    Args:
        playback_state: Dictionary containing playback state information
    """
    if playback_state.get('is_playing'):
        pygame.mixer.music.stop()
        playback_state['is_playing'] = False
        print("Pemutaran dihentikan.")


def pause_file(playback_state):
    """
    Pause audio playback using pygame.
    
    Args:
        playback_state: Dictionary containing playback state information
    """
    if playback_state.get('is_playing') and pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        playback_state['is_playing'] = False
        print("Pemutaran dijeda.")


def resume_file(playback_state):
    """
    Resume audio playback using pygame.
    
    Args:
        playback_state: Dictionary containing playback state information
    """
    if not playback_state.get('is_playing') and playback_state.get('current_file_path'):
        pygame.mixer.music.unpause()
        playback_state['is_playing'] = True
        print("Pemutaran dilanjutkan.")
