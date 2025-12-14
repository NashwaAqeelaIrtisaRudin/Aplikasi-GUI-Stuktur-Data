import sys
import tkinter as tk

from tkinter import messagebox

# Ensure pygame is available and give a clear error if not
try:
    import pygame
except Exception as e:
    # show error using a temporary hidden Tk root so user sees a dialog
    try:
        _tmp = tk.Tk()
        _tmp.withdraw()
        messagebox.showerror(
            "Dependency error",
            f"Module 'pygame' tidak ditemukan untuk Python:\n{sys.executable}\n\nError: {e}\n\nJalankan:\n{sys.executable} -m pip install pygame"
        )
        _tmp.destroy()
    except Exception:
        # fallback to console
        print(f"pygame import error: {e}\nInstall with: {sys.executable} -m pip install pygame")
    raise

from gui import MusicPlayerGUI


def main():
    # Initialize pygame mixer for audio playback
    try:
        pygame.mixer.init()
    except Exception as e:
        try:
            _tmp = tk.Tk()
            _tmp.withdraw()
            messagebox.showerror("Pygame init error", f"Gagal menginisialisasi pygame mixer:\n{e}")
            _tmp.destroy()
        except Exception:
            print(f"Pygame init error: {e}")
        return
    
    # Create the main window
    root = tk.Tk()
    
    # Create the application
    app = MusicPlayerGUI(root)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
