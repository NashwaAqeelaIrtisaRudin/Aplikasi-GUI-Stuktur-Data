import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random

from models import SinglyLinkedList, DoublyLinkedList, Queue, Stack, Lagu
from utils import save_data, load_data, load_dummy_data, play_file, stop_file, pause_file, resume_file


class MusicPlayerGUI:
    """Main GUI application for the music player."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("900x700")
        # Setup styles and fonts for better appearance
        self.setup_styles()

        # Initialize application data
        loaded_data = load_data()
        if loaded_data:
            self.library = loaded_data.get('library', SinglyLinkedList())
            self.playlists = loaded_data.get('playlists', {})
        else:
            # If no data file found, initialize with dummy data
            self.library = SinglyLinkedList()
            self.playlists = {}
            load_dummy_data(self.library, self.playlists)
            # Save dummy data for the first time
            save_data(self.library, self.playlists)

        # Playback state management
        # Start event loop
        self.check_music_events()

        self.playback_state = {
            'current_playing': None,
            'current_file_path': None,
            'is_playing': False,
            '_previous_playing': None,
            'history': Stack(),
            'autoplay_enabled': True  # Autoplay enabled by default
        }
        
        self.playback_queue = Queue()
        self.playback_history = Stack()
        self.current_playlist = None
        self.current_playlist_node = None
        self.current_user_role = None
        self.now_playing_label = None  # Reference to the now playing label
        self.is_playlist_mode = False  # Track if playing from playlist

        # Setup pygame for music end events
        import pygame
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

        # Create main frame for navigation
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a persistent control container at the bottom to keep playback controls
        # visible even when the main_frame is cleared or navigation happens.
        self.control_container = tk.Frame(self.root, name='persistent_control_container')
        self.control_container.pack(side=tk.BOTTOM, fill=tk.X)

        # Set protocol for window close button to save data before closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start checking for music events
                # Show initial login screen
        self.show_login_screen()

    def clear_frame(self):
        """Clear all widgets from the main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def setup_styles(self):
        """Configure ttk styles and root appearance."""
        try:
            from tkinter import ttk
            self.style = ttk.Style()
            try:
                self.style.theme_use('clam')
            except Exception:
                pass
            # Configure ttk styles (fonts only)
            default_bg = self.root.cget('bg')
            self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
            self.style.configure('TLabel', font=('Segoe UI', 11), background=default_bg)
            self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), background=default_bg)
        except Exception:
            # Fallback: ignore style errors
            pass

    def styled_label(self, parent, text, style='TLabel', **pack_opts):
        """Create a themed label and pack it with default padding."""
        try:
            from tkinter import ttk
            lbl = ttk.Label(parent, text=text, style=style)
        except Exception:
            lbl = tk.Label(parent, text=text)
        padx = pack_opts.pop('padx', 10)
        pady = pack_opts.pop('pady', 6)

        lbl.pack(padx=padx, pady=pady)
        return lbl

    def styled_button(self, parent, text, command=None, **pack_opts):
        """Create a themed button and pack it with default padding."""
        try:
            from tkinter import ttk
            btn = ttk.Button(parent, text=text, command=command)
        except Exception:
            btn = tk.Button(parent, text=text, command=command)
        padx = pack_opts.pop('padx', 10)
        pady = pack_opts.pop('pady', 6)
        side = pack_opts.pop('side', None)

        if side:
            btn.pack(side=side, padx=padx, pady=pady)
        else:
            btn.pack(padx=padx, pady=pady)
        return btn

    def on_closing(self):
        """Called when application is closing - saves data before exit."""
        try:
            # Save all data before closing
            save_data(self.library, self.playlists)
            print("Data berhasil disimpan sebelum aplikasi ditutup.")
        except Exception as e:
            print(f"Error saat menyimpan data: {e}")
            messagebox.showerror("Error", f"Terjadi kesalahan saat menyimpan data:\\n{e}")
        finally:
            # Close the application
            self.root.destroy()

    # This prevents multiple event loops and race conditions


    def handle_song_end(self):
        """Handle autoplay when a song ends."""
        import time
        
        # Cooldown check: prevent rapid autoplay triggers
        current_time = time.time()
        if hasattr(self, '_last_autoplay_time'):
            if current_time - self._last_autoplay_time < 2:  # 2 second cooldown
                print("Autoplay cooldown active, skipping trigger")
                return
        
        self._last_autoplay_time = current_time
        print("Song ended, autoplay triggered")
        
        # Priority 1: Play from queue if available
        if not self.playback_queue.is_empty():
            next_song = self.playback_queue.peek()
            if next_song and next_song.file_path:  # Check file exists
                self._next_in_queue()
                return
        
        # Priority 2: Play next in playlist if in playlist mode
        if self.is_playlist_mode and self.current_playlist_node and self.current_playlist_node.next:
            next_node = self.current_playlist_node.next
            if next_node.data and next_node.data.file_path:  # Check file exists
                self._next_in_playlist()
                return
        
        # Priority 3: Play similar song (only if not in playlist mode)
        if not self.is_playlist_mode:
            # Check if there's at least one song with valid file
            all_songs = self.library.get_all_lagu()
            valid_songs = [s for s in all_songs if s.file_path and s.file_path.strip()]
            
            if len(valid_songs) > 1:  # Need at least 2 songs (current + next)
                self._next_similar()
            else:
                print("No valid songs for autoplay, stopping")
                self.playback_state['is_playing'] = False

    # ========== LOGIN SCREENS ==========
    
    def show_login_screen(self):
        """Display the initial login screen."""
        self.clear_frame()
        self.current_user_role = None
        self.playback_state['_previous_playing'] = None
        self.styled_label(self.main_frame, "Selamat Datang di Music Player",style='Header.TLabel', pady=20)
        self.styled_label(self.main_frame, "Pilih Peran Anda:", pady=10)

        self.styled_button(self.main_frame, "Login sebagai Admin", command=self.login_as_admin)
        self.styled_button(self.main_frame, "Login sebagai User", command=self.login_as_user)
        self.styled_button(self.main_frame, "Keluar", command=self.on_closing)

    def login_as_admin(self):
        """Set role as admin and show admin menu."""
        self.current_user_role = "Admin"
        self.show_admin_menu()

    def login_as_user(self):
        """Set role as user and show user menu."""
        self.current_user_role = "User"
        self.show_user_menu()

    # ========== ADMIN MENU ==========
    
    def show_admin_menu(self):
        """Display the admin menu screen."""
        self.clear_frame()
        self.styled_label(self.main_frame, "Menu Admin", style='Header.TLabel', pady=20)

        self.styled_button(self.main_frame, "Tambah Lagu Baru", command=self.tambah_lagu_baru)
        self.styled_button(self.main_frame, "Lihat Semua Lagu di Library", command=self.lihat_semua_lagu)
        self.styled_button(self.main_frame, "Ubah Data Lagu", command=self.ubah_data_lagu)
        self.styled_button(self.main_frame, "Hapus Lagu", command=self.hapus_lagu)
        self.styled_button(self.main_frame, "Logout", command=self.show_login_screen)

    def tambah_lagu_baru(self):
        """Show form to add a new song to the library."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Tambah Lagu Baru", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.main_frame, text="ID Lagu (unik):").pack(anchor="w", padx=50)
        id_entry = tk.Entry(self.main_frame, width=50)
        id_entry.pack(padx=50, pady=2)

        tk.Label(self.main_frame, text="Judul Lagu:").pack(anchor="w", padx=50)
        judul_entry = tk.Entry(self.main_frame, width=50)
        judul_entry.pack(padx=50, pady=2)

        tk.Label(self.main_frame, text="Artis:").pack(anchor="w", padx=50)
        artis_entry = tk.Entry(self.main_frame, width=50)
        artis_entry.pack(padx=50, pady=2)

        tk.Label(self.main_frame, text="Album:").pack(anchor="w", padx=50)
        album_entry = tk.Entry(self.main_frame, width=50)
        album_entry.pack(padx=50, pady=2)

        tk.Label(self.main_frame, text="Genre:").pack(anchor="w", padx=50)
        genre_entry = tk.Entry(self.main_frame, width=50)
        genre_entry.pack(padx=50, pady=2)

        tk.Label(self.main_frame, text="Tahun Rilis:").pack(anchor="w", padx=50)
        tahun_entry = tk.Entry(self.main_frame, width=50)
        tahun_entry.pack(padx=50, pady=2)

        tk.Label(self.main_frame, text="Path File Audio:").pack(anchor="w", padx=50)
        file_entry = tk.Entry(self.main_frame, width=50)
        file_entry.pack(padx=50, pady=2)

        def submit():
            import os
            id_baru = id_entry.get().strip()
            judul_baru = judul_entry.get().strip()
            artis_baru = artis_entry.get().strip()
            album_baru = album_entry.get().strip()
            genre_baru = genre_entry.get().strip()
            file_baru = file_entry.get().strip()
            try:
                tahun_baru = int(tahun_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Tahun harus berupa angka.")
                return

            if not all([id_baru, judul_baru, artis_baru, album_baru, genre_baru, file_baru]):
                messagebox.showwarning("Peringatan", "Semua field harus diisi.")
                return

            if self.library.find_by_id(id_baru):
                messagebox.showerror("Error", f"ID lagu '{id_baru}' sudah ada di library.")
                return

            if not os.path.isfile(file_baru):
                messagebox.showerror("Error", f"File audio '{file_baru}' tidak ditemukan.")
                return

            lagu_baru = Lagu(id_baru, judul_baru, artis_baru, album_baru, genre_baru, tahun_baru, file_baru)
            self.library.append(lagu_baru)
            messagebox.showinfo("Info", f"Lagu '{lagu_baru.judul}' oleh {lagu_baru.artis} telah ditambahkan ke library.")
            save_data(self.library, self.playlists)
            self.show_admin_menu()

        tk.Button(self.main_frame, text="Simpan Lagu", command=submit).pack(pady=20)
        tk.Button(self.main_frame, text="Kembali ke Menu Admin", command=self.show_admin_menu).pack()

    def lihat_semua_lagu(self):
        """Display all songs in the library."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Daftar Semua Lagu di Library", font=("Arial", 14)).pack(pady=10)

        columns = ("ID", "Judul", "Artis", "Album", "Genre", "Tahun", "File")
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15)
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)

        for lagu in self.library.get_all_lagu():
            tree.insert('', tk.END, values=(lagu.id, lagu.judul, lagu.artis, lagu.album, lagu.genre, lagu.tahun, lagu.file_path))


        tk.Button(self.main_frame, text="Kembali ke Menu Admin", command=self.show_admin_menu).pack(pady=10)

    def ubah_data_lagu(self):
        """Show interface to edit song data."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Ubah Data Lagu", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.main_frame, text="Masukkan ID lagu yang ingin diubah:").pack(pady=5)
        id_entry = tk.Entry(self.main_frame, width=30)
        id_entry.pack(pady=5)

        def find_and_edit():
            import os
            id_ubah = id_entry.get().strip()
            lagu_target = self.library.find_by_id(id_ubah)

            if not lagu_target:
                messagebox.showerror("Error", f"Lagu dengan ID '{id_ubah}' tidak ditemukan.")
                return

            for widget in self.main_frame.winfo_children():
                widget.destroy()

            tk.Label(self.main_frame, text=f"Ubah Data Lagu: {lagu_target.judul}", font=("Arial", 14)).pack(pady=10)

            tk.Label(self.main_frame, text="Judul Baru:").pack(anchor="w", padx=50)
            judul_entry = tk.Entry(self.main_frame, width=50)
            judul_entry.insert(0, lagu_target.judul)
            judul_entry.pack(padx=50, pady=2)

            tk.Label(self.main_frame, text="Artis Baru:").pack(anchor="w", padx=50)
            artis_entry = tk.Entry(self.main_frame, width=50)
            artis_entry.insert(0, lagu_target.artis)
            artis_entry.pack(padx=50, pady=2)

            tk.Label(self.main_frame, text="Album Baru:").pack(anchor="w", padx=50)
            album_entry = tk.Entry(self.main_frame, width=50)
            album_entry.insert(0, lagu_target.album)
            album_entry.pack(padx=50, pady=2)

            tk.Label(self.main_frame, text="Genre Baru:").pack(anchor="w", padx=50)
            genre_entry = tk.Entry(self.main_frame, width=50)
            genre_entry.insert(0, lagu_target.genre)
            genre_entry.pack(padx=50, pady=2)

            tk.Label(self.main_frame, text="Tahun Baru:").pack(anchor="w", padx=50)
            tahun_entry = tk.Entry(self.main_frame, width=50)
            tahun_entry.insert(0, str(lagu_target.tahun))
            tahun_entry.pack(padx=50, pady=2)

            tk.Label(self.main_frame, text="Path File Audio Baru:").pack(anchor="w", padx=50)
            file_entry = tk.Entry(self.main_frame, width=50)
            file_entry.insert(0, lagu_target.file_path)
            file_entry.pack(padx=50, pady=2)

            def submit_edit():
                judul_baru = judul_entry.get().strip()
                artis_baru = artis_entry.get().strip()
                album_baru = album_entry.get().strip()
                genre_baru = genre_entry.get().strip()
                file_baru = file_entry.get().strip()
                try:
                    tahun_baru = int(tahun_entry.get().strip())
                except ValueError:
                    messagebox.showerror("Error", "Tahun harus berupa angka.")
                    return

                if not all([judul_baru, artis_baru, album_baru, genre_baru, file_baru]):
                    messagebox.showwarning("Peringatan", "Semua field (termasuk path file) harus diisi.")
                    return

                if not os.path.isfile(file_baru):
                    messagebox.showerror("Error", f"File audio '{file_baru}' tidak ditemukan.")
                    return

    

                lagu_target.judul = judul_baru
                lagu_target.artis = artis_baru
                lagu_target.album = album_baru
                lagu_target.genre = genre_baru
                lagu_target.tahun = tahun_baru
                lagu_target.file_path = file_baru

                messagebox.showinfo("Info", f"Data lagu '{lagu_target.judul}' telah diperbarui.")

                # Update in all playlists
                for playlist in self.playlists.values():
                    node = playlist.find_node_by_lagu_id(id_ubah)
                    if node:
                        node.data.judul = judul_baru
                        node.data.artis = artis_baru
                        node.data.album = album_baru
                        node.data.genre = genre_baru
                        node.data.tahun = tahun_baru
                        node.data.file_path = file_baru
                messagebox.showinfo("Info", "Data lagu juga telah diperbarui di semua playlist.")
                save_data(self.library, self.playlists)
                self.show_admin_menu()

            tk.Button(self.main_frame, text="Simpan Perubahan", command=submit_edit).pack(pady=20)
            tk.Button(self.main_frame, text="Kembali", command=self.show_admin_menu).pack()

        tk.Button(self.main_frame, text="Cari Lagu", command=find_and_edit).pack(pady=10)
        tk.Button(self.main_frame, text="Kembali ke Menu Admin", command=self.show_admin_menu).pack()

    def hapus_lagu(self):
        """Show interface to delete a song from the library."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Hapus Lagu", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.main_frame, text="Masukkan ID lagu yang ingin dihapus:").pack(pady=5)
        id_entry = tk.Entry(self.main_frame, width=30)
        id_entry.pack(pady=5)

        def confirm_and_delete():
            id_hapus = id_entry.get().strip()
            lagu_dihapus = self.library.remove_by_id(id_hapus)

            if not lagu_dihapus:
                messagebox.showerror("Error", f"Lagu dengan ID '{id_hapus}' tidak ditemukan.")
                return

            # Remove from all playlists
            lagu_dihapus_dari_playlist = 0
            for playlist in self.playlists.values():
                node = playlist.find_node_by_lagu_id(id_hapus)
                if node:
                    playlist.remove_node(node)
                    lagu_dihapus_dari_playlist += 1

            # Remove from queue
            queue_lama = list(self.playback_queue.items)
            self.playback_queue = Queue()
            for lagu in queue_lama:
                if lagu.id != id_hapus:
                    self.playback_queue.enqueue(lagu)

            # Stop playback if currently playing
            if self.playback_state['current_playing'] and self.playback_state['current_playing'].id == id_hapus:
                stop_file(self.playback_state)
                self.playback_state['current_playing'] = None
                self.playback_state['current_file_path'] = None
                self.playback_state['is_playing'] = False
                self.current_playlist = None
                self.current_playlist_node = None
                messagebox.showinfo("Info", "Pemutaran lagu yang dihapus dihentikan.")

            message = f"Lagu '{lagu_dihapus.judul}' oleh {lagu_dihapus.artis} telah dihapus dari library."
            if lagu_dihapus_dari_playlist > 0:
                message += f"\nLagu juga telah dihapus dari {lagu_dihapus_dari_playlist} playlist."
            messagebox.showinfo("Info", message)
            save_data(self.library, self.playlists)
            self.show_admin_menu()

        tk.Button(self.main_frame, text="Hapus Lagu", command=confirm_and_delete).pack(pady=10)
        tk.Button(self.main_frame, text="Kembali ke Menu Admin", command=self.show_admin_menu).pack()

    # ========== USER MENU ==========
    
    def show_user_menu(self):
        """Display the user menu screen."""
        self.clear_frame()
        self.styled_label(self.main_frame, "Menu User", style='Header.TLabel', pady=20)

        self.styled_button(self.main_frame, "Cari Lagu", command=self.cari_lagu)
        self.styled_button(self.main_frame, "Putar Lagu (Dari Library)", command=self.putar_lagu_library)
        self.styled_button(self.main_frame, "Buat/Atur Playlist", command=self.buat_atur_playlist)
        self.styled_button(self.main_frame, "Lihat Antrian Pemutaran", command=self.lihat_antrian)
        self.styled_button(self.main_frame, "Lihat Riwayat Pemutaran", command=self.lihat_riwayat)
        self.styled_button(self.main_frame, "Logout", command=self.show_login_screen)

    def cari_lagu(self):
        """Show interface to search for songs."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Cari Lagu", font=("Arial", 14)).pack(pady=10)

        search_frame = tk.Frame(self.main_frame)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Kriteria:").grid(row=0, column=0, padx=5)
        criteria_var = tk.StringVar(value="id")
        tk.Radiobutton(search_frame, text="ID", variable=criteria_var, value="id").grid(row=0, column=1, padx=5)
        tk.Radiobutton(search_frame, text="Judul", variable=criteria_var, value="judul").grid(row=0, column=2, padx=5)
        tk.Radiobutton(search_frame, text="Artis", variable=criteria_var, value="artis").grid(row=0, column=3, padx=5)

        tk.Label(self.main_frame, text="Masukkan nilai:").pack(pady=5)
        search_entry = tk.Entry(self.main_frame, width=30)
        search_entry.pack(pady=5)

        def perform_search():
            criteria = criteria_var.get()
            value = search_entry.get().strip()
            if not value:
                messagebox.showwarning("Peringatan", "Silakan masukkan nilai pencarian.")
                return

            search_kwargs = {criteria: value}
            results = self.library.find_by_criteria(**search_kwargs)

            for widget in self.main_frame.winfo_children():
                widget.destroy()

            tk.Label(self.main_frame, text="Hasil Pencarian", font=("Arial", 14)).pack(pady=10)

            columns = ("ID", "Judul", "Artis", "Album", "Genre", "Tahun", "File")
            tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=10)
            tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor=tk.CENTER)

            for lagu in results:
                tree.insert('', tk.END, values=(lagu.id, lagu.judul, lagu.artis, lagu.album, lagu.genre, lagu.tahun, lagu.file_path))

            if not results:
                tk.Label(self.main_frame, text="Lagu tidak ditemukan.").pack()

            def tambah_ke_antrian():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showwarning("Peringatan", "Pilih lagu terlebih dahulu.")
                    return
                item_values = tree.item(selected_item[0], 'values')
                id_lagu = item_values[0]
                lagu_target = self.library.find_by_id(id_lagu)
                if lagu_target:
                    self.playback_queue.enqueue(lagu_target)
                    messagebox.showinfo("Info", f"Lagu '{lagu_target.judul}' ditambahkan ke antrian pemutaran.")

            tk.Button(self.main_frame, text="Tambah ke Antrian", command=tambah_ke_antrian).pack(pady=5)
            tk.Button(self.main_frame, text="Kembali ke Menu User", command=self.show_user_menu).pack()

        tk.Button(self.main_frame, text="Cari", command=perform_search).pack(pady=10)
        tk.Button(self.main_frame, text="Kembali ke Menu User", command=self.show_user_menu).pack()

    def putar_lagu_library(self):
        """Show interface to play songs from the library."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Putar Lagu dari Library", font=("Arial", 14)).pack(pady=10)

        columns = ("ID", "Judul", "Artis", "Album", "Genre", "Tahun", "File")
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15)
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)

        for lagu in self.library.get_all_lagu():
            tree.insert('', tk.END, values=(lagu.id, lagu.judul, lagu.artis, lagu.album, lagu.genre, lagu.tahun, lagu.file_path))

        def play_selected():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Peringatan", "Pilih lagu terlebih dahulu.")
                return

            item_values = tree.item(selected_item[0], 'values')
            id_lagu = item_values[0]
            lagu_target = self.library.find_by_id(id_lagu)

            if lagu_target:
                self.is_playlist_mode = False
                play_file(lagu_target, self.playback_state)
                self.show_playback_controls(is_playlist=False)
                try:
                    self._start_playback_time_updater()
                except Exception:
                    pass

        def tambah_ke_antrian():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Peringatan", "Pilih lagu terlebih dahulu.")
                return
            item_values = tree.item(selected_item[0], 'values')
            id_lagu = item_values[0]
            lagu_target = self.library.find_by_id(id_lagu)
            if lagu_target:
                self.playback_queue.enqueue(lagu_target)
                messagebox.showinfo("Info", f"Lagu '{lagu_target.judul}' ditambahkan ke antrian pemutaran.")

        tk.Button(self.main_frame, text="Tambah ke Antrian", command=tambah_ke_antrian).pack(pady=5)
        tk.Button(self.main_frame, text="Putar Lagu Terpilih", command=play_selected).pack(pady=5)
        tk.Button(self.main_frame, text="Kembali ke Menu User", command=self.show_user_menu).pack(pady=10)

    # ========== PLAYBACK CONTROLS ==========
    
    def show_playback_controls(self, is_playlist=False):
        """Display playback control buttons."""
        # Clear any existing controls in the persistent control container
        for widget in self.control_container.winfo_children():
            widget.destroy()

        control_frame = tk.Frame(self.control_container, name='control_frame')
        control_frame.pack(pady=10, fill=tk.X)
        # Set playlist mode flag
        self.is_playlist_mode = is_playlist

        # Create and store reference to the now playing label
        self.now_playing_label = tk.Label(control_frame, text=f"Sedang Memutar: {self.playback_state['current_playing' ]}")
        self.now_playing_label.pack()

        # Playback time label (elapsed / total)
        self.playback_time_label = tk.Label(control_frame, text="00:00 / 00:00")
        self.playback_time_label.pack()

        # Autoplay status label
        autoplay_status = "ON" if self.playback_state.get('autoplay_enabled') else "OFF"
        autoplay_label = tk.Label(control_frame, text=f"Autoplay: {autoplay_status}", fg="green" if self.playback_state.get('autoplay_enabled') else "red")
        autoplay_label.pack()

        def next_action():
            if is_playlist:
                self._next_in_playlist()
            else:
                self._next_similar()

        def prev_action():
            if is_playlist:
                self._prev_in_playlist()
            else:
                self._prev_from_history()

        def queue_action():
            self._next_in_queue()

        def pause_action():
            pause_file(self.playback_state)

        def resume_action():
            resume_file(self.playback_state)
            # restart updater
            self._start_playback_time_updater()

        def stop_action():
            stop_file(self.playback_state)
            self.playback_state['current_playing'] = None
            self.playback_state['current_file_path'] = None
            self.current_playlist = None
            self.current_playlist_node = None
            self.is_playlist_mode = False
            messagebox.showinfo("Info", "Pemutaran dihentikan.")
            # When Stop is clicked, remove the playback console (controls)
            try:
                for widget in self.control_container.winfo_children():
                    widget.destroy()
                # stop updater if running
                self._stop_playback_time_updater()
                # clear label references
                self.now_playing_label = None
                self.playback_time_label = None
            except Exception:
                pass

        def toggle_autoplay():
            self.playback_state['autoplay_enabled'] = not self.playback_state.get('autoplay_enabled', True)
            new_status = "ON" if self.playback_state['autoplay_enabled'] else "OFF"
            autoplay_label.config(text=f"Autoplay: {new_status}", fg="green" if self.playback_state['autoplay_enabled'] else "red")
            messagebox.showinfo("Autoplay", f"Autoplay sekarang: {new_status}")

        # Group action buttons in a centered horizontal frame
        actions_frame = tk.Frame(control_frame)
        actions_frame.pack(pady=6)

        tk.Button(actions_frame, text="Lagu Sebelumnya (Riwayat)", command=prev_action).pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Lagu Berikutnya (Mirip)", command=next_action).pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Lagu dari Antrian", command=queue_action).pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Pause", command=pause_action).pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Resume", command=resume_action).pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Autoplay", command=toggle_autoplay).pack(side=tk.LEFT, padx=5)
        tk.Button(actions_frame, text="Hentikan", command=stop_action).pack(side=tk.LEFT, padx=5)


    def check_music_events(self):
        """Check for music events (simple autoplay)"""
        import pygame
        import os
        
        # Ensure pygame is initialized (required for event.get)
        if not pygame.get_init():
            try:
                os.environ['SDL_VIDEODRIVER'] = 'dummy'
                pygame.init()
            except Exception as e:
                print(f"Pygame init error: {e}")
                return

        try:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    if self.playback_state.get('autoplay_enabled') and self.playback_state.get('current_playing'):
                        self.handle_song_end()
        except Exception as e:
            pass
            
        self.root.after(100, self.check_music_events)

    def _update_now_playing_label(self):
        """Update the now playing label with current song information."""
        if self.now_playing_label and self.playback_state['current_playing']:
            self.now_playing_label.config(text=f"Sedang Memutar: {self.playback_state['current_playing']}")

    def _start_playback_time_updater(self):
        """Start periodic updater for playback elapsed/total time."""
        # Cancel existing
        self._stop_playback_time_updater()
        self._playback_time_updater_id = self.root.after(500, self._update_playback_time)

    def _stop_playback_time_updater(self):
        """Stop the periodic updater if running."""
        try:
            if hasattr(self, '_playback_time_updater_id') and self._playback_time_updater_id:
                self.root.after_cancel(self._playback_time_updater_id)
                self._playback_time_updater_id = None
        except Exception:
            pass

    def _update_playback_time(self):
        """Update the playback_time_label with elapsed/total time."""
        try:
            total = self.playback_state.get('duration_seconds')
            pos_ms = 0
            try:
                import pygame
                pos_ms = pygame.mixer.music.get_pos()
            except Exception:
                pos_ms = -1

            elapsed = 0
            if pos_ms is not None and pos_ms >= 0:
                elapsed = int(pos_ms // 1000)

            def fmt(s):
                if s is None:
                    return "--:--"
                m = s // 60
                sec = s % 60
                return f"{m:02d}:{sec:02d}"

            elapsed_str = fmt(elapsed)
            total_str = fmt(total) if total is not None else "--:--"

            if hasattr(self, 'playback_time_label') and self.playback_time_label:
                self.playback_time_label.config(text=f"{elapsed_str} / {total_str}")
        except Exception:
            pass
        finally:
            # reschedule
            try:
                self._playback_time_updater_id = self.root.after(500, self._update_playback_time)
            except Exception:
                self._playback_time_updater_id = None

    def _next_similar(self):
        """Play the next similar song based on artist or genre."""
        if not self.playback_state['current_playing']:
            messagebox.showinfo("Info", "Tidak ada lagu yang sedang diputar.")
            return

        all_lagu = self.library.get_all_lagu()
        
        # Filter only songs with valid file paths
        valid_lagu = [l for l in all_lagu if l.file_path and l.file_path.strip()]
        
        if len(valid_lagu) <= 1:
            messagebox.showinfo("Info", "Tidak cukup lagu dengan file audio untuk mencari lagu berikutnya.")
            self.playback_state['is_playing'] = False
            return

        similar_lagu = []
        for lagu in valid_lagu:
            if lagu.id != self.playback_state['current_playing'].id:
                if lagu.artis == self.playback_state['current_playing'].artis:
                    similar_lagu.append((lagu, 2))
                elif lagu.genre == self.playback_state['current_playing'].genre:
                    similar_lagu.append((lagu, 1))

        similar_lagu.sort(key=lambda x: x[1], reverse=True)

        if similar_lagu:
            next_lagu = similar_lagu[0][0]
            # Autoplay: langsung memutar lagu mirip tanpa notifikasi
            play_file(next_lagu, self.playback_state)
            self._update_now_playing_label()  # Update the label
            try:
                self._start_playback_time_updater()
            except Exception:
                pass
        else:
            fallback_lagu = random.choice([l for l in all_lagu if l.id != self.playback_state['current_playing'].id])
            messagebox.showinfo("Info", f"Tidak ada lagu mirip ditemukan. Memutar lagu acak sebagai fallback.\nMemutar: {fallback_lagu}")
            play_file(fallback_lagu, self.playback_state)
            self._update_now_playing_label()  # Update the label
            try:
                self._start_playback_time_updater()
            except Exception:
                pass

    def _next_in_playlist(self):
        """Play the next song in the current playlist."""
        if not self.current_playlist or not self.current_playlist_node or not self.current_playlist_node.next:
            messagebox.showinfo("Info", "Tidak ada lagu berikutnya dalam playlist.")
            return
        self.current_playlist_node = self.current_playlist_node.next
        next_lagu = self.current_playlist_node.data
        play_file(next_lagu, self.playback_state)
        self._update_now_playing_label()  # Update the label
        try:
            self._start_playback_time_updater()
        except Exception:
            pass

    def _prev_in_playlist(self):
        """Play the previous song in the current playlist."""
        if not self.current_playlist or not self.current_playlist_node or not self.current_playlist_node.prev:
            messagebox.showinfo("Info", "Tidak ada lagu sebelumnya dalam playlist.")
            return
        self.current_playlist_node = self.current_playlist_node.prev
        prev_lagu = self.current_playlist_node.data
        play_file(prev_lagu, self.playback_state)
        self._update_now_playing_label()  # Update the label
        try:
            self._start_playback_time_updater()
        except Exception:
            pass

    def _prev_from_history(self):
        """Play the previous song from playback history."""
        lagu_sebelumnya = self.playback_state['history'].pop()
        if lagu_sebelumnya:
            play_file(lagu_sebelumnya, self.playback_state)
            self.playback_state['_previous_playing'] = lagu_sebelumnya
            self._update_now_playing_label()  # Update the label
            try:
                self._start_playback_time_updater()
            except Exception:
                pass
        else:
            messagebox.showinfo("Info", "Tidak ada lagu sebelumnya dalam riwayat.")

    def _next_in_queue(self):
        """Play the next song from the playback queue."""
        if self.playback_queue.is_empty():
            messagebox.showinfo("Info", "Antrian pemutaran kosong.")
            return
        lagu_berikutnya = self.playback_queue.dequeue()
        play_file(lagu_berikutnya, self.playback_state)
        self._update_now_playing_label()  # Update the label
        try:
            self._start_playback_time_updater()
        except Exception:
            pass

    # ========== PLAYLIST MANAGEMENT ==========
    
    def buat_atur_playlist(self):
        """Show interface to create and manage playlists."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Atur Playlist", font=("Arial", 14)).pack(pady=10)

        playlist_listbox = tk.Listbox(self.main_frame, height=10)
        playlist_listbox.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        for name in self.playlists.keys():
            playlist_listbox.insert(tk.END, name)

        def create_playlist():
            name = simpledialog.askstring("Buat Playlist", "Masukkan nama playlist baru:")
            if name and name not in self.playlists:
                self.playlists[name] = DoublyLinkedList()
                playlist_listbox.insert(tk.END, name)
                messagebox.showinfo("Info", f"Playlist '{name}' berhasil dibuat.")
                save_data(self.library, self.playlists)
            elif name in self.playlists:
                messagebox.showerror("Error", f"Playlist dengan nama '{name}' sudah ada.")

        def manage_selected_playlist():
            selection = playlist_listbox.curselection()
            if not selection:
                messagebox.showwarning("Peringatan", "Pilih playlist terlebih dahulu.")
                return
            selected_name = playlist_listbox.get(selection[0])
            self.manage_playlist_details(selected_name)

        tk.Button(self.main_frame, text="Buat Playlist Baru", command=create_playlist).pack(pady=5)
        tk.Button(self.main_frame, text="Atur Playlist Terpilih", command=manage_selected_playlist).pack(pady=5)
        
        def delete_selected_playlist():
            selection = playlist_listbox.curselection()
            if not selection:
                messagebox.showwarning("Peringatan", "Pilih playlist terlebih dahulu.")
                return
            selected_name = playlist_listbox.get(selection[0])
            confirm = messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus playlist '{selected_name}'?")
            if not confirm:
                return
            # If the deleted playlist is currently playing, stop playback and reset state
            try:
                if self.current_playlist is not None and self.current_playlist == self.playlists.get(selected_name):
                    stop_file(self.playback_state)
                    self.playback_state['current_playing'] = None
                    self.playback_state['current_file_path'] = None
                    self.playback_state['is_playing'] = False
                    self.current_playlist = None
                    self.current_playlist_node = None
                    self.is_playlist_mode = False
            except Exception:
                pass
            # Remove playlist from internal storage and UI
            if selected_name in self.playlists:
                del self.playlists[selected_name]
            playlist_listbox.delete(selection[0])
            save_data(self.library, self.playlists)
            messagebox.showinfo("Info", f"Playlist '{selected_name}' berhasil dihapus.")

        tk.Button(self.main_frame, text="Hapus Playlist", command=delete_selected_playlist).pack(pady=5)
        tk.Button(self.main_frame, text="Kembali ke Menu User", command=self.show_user_menu).pack(pady=10)

    def manage_playlist_details(self, playlist_name):
        """Show detailed management interface for a specific playlist."""
        self.clear_frame()
        playlist_obj = self.playlists[playlist_name]
        tk.Label(self.main_frame, text=f"Atur Playlist: {playlist_name}", font=("Arial", 14)).pack(pady=10)

        columns = ("No", "ID", "Judul", "Artis", "Album", "Genre", "Tahun", "File")
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=10)
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)

        for i, lagu in enumerate(playlist_obj.get_as_list(), 1):
            tree.insert('', tk.END, values=(i, lagu.id, lagu.judul, lagu.artis, lagu.album, lagu.genre, lagu.tahun, lagu.file_path))

        def add_song_to_playlist():
            add_window = tk.Toplevel(self.root)
            add_window.title(f"Tambah Lagu ke {playlist_name}")
            add_window.geometry("700x500")

            tk.Label(add_window, text="Pilih Lagu dari Library:").pack(pady=10)

            lib_columns = ("ID", "Judul", "Artis", "Album", "Genre", "Tahun", "File")
            lib_tree = ttk.Treeview(add_window, columns=lib_columns, show='headings', height=15)
            lib_tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

            for col in lib_columns:
                lib_tree.heading(col, text=col)
                lib_tree.column(col, width=100, anchor=tk.CENTER)

            for lagu in self.library.get_all_lagu():
                lib_tree.insert('', tk.END, values=(lagu.id, lagu.judul, lagu.artis, lagu.album, lagu.genre, lagu.tahun, lagu.file_path))

            def confirm_add():
                selected_item = lib_tree.selection()
                if not selected_item:
                    messagebox.showwarning("Peringatan", "Pilih lagu terlebih dahulu.")
                    return

                item_values = lib_tree.item(selected_item[0], 'values')
                id_lagu = item_values[0]
                lagu_target = self.library.find_by_id(id_lagu)

                if lagu_target:
                    if playlist_obj.find_node_by_lagu_id(lagu_target.id):
                        messagebox.showwarning("Peringatan", f"Lagu '{lagu_target.judul}' sudah ada di playlist ini.")
                    else:
                        playlist_obj.append(lagu_target)
                        messagebox.showinfo("Info", f"Lagu '{lagu_target.judul}' berhasil ditambahkan ke playlist '{playlist_name}'.")
                        add_window.destroy()
                        save_data(self.library, self.playlists)
                        self.manage_playlist_details(playlist_name)

            tk.Button(add_window, text="Tambah ke Playlist", command=confirm_add).pack(pady=10)
            tk.Button(add_window, text="Batal", command=add_window.destroy).pack(pady=5)

        def remove_song_from_playlist():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Peringatan", "Pilih lagu dari playlist terlebih dahulu.")
                return

            item_values = tree.item(selected_item[0], 'values')
            id_lagu = item_values[1]
            node_to_remove = playlist_obj.find_node_by_lagu_id(id_lagu)

            if node_to_remove:
                lagu_dihapus = node_to_remove.data
                playlist_obj.remove_node(node_to_remove)
                messagebox.showinfo("Info", f"Lagu '{lagu_dihapus.judul}' berhasil dihapus dari playlist '{playlist_name}'.")
                save_data(self.library, self.playlists)
                self.manage_playlist_details(playlist_name)

        def play_this_playlist():
            if playlist_obj.size == 0:
                messagebox.showwarning("Peringatan", "Playlist kosong. Tidak ada lagu untuk diputar.")
                return
            self.current_playlist = playlist_obj
            self.current_playlist_node = playlist_obj.head
            first_lagu = self.current_playlist_node.data
            play_file(first_lagu, self.playback_state)
            messagebox.showinfo("Info", f"Sedang memutar playlist: {playlist_name}\nSedang memutar lagu pertama: {first_lagu}")
            self.show_playback_controls(is_playlist=True)
            try:
                self._start_playback_time_updater()
            except Exception:
                pass

        tk.Button(self.main_frame, text="Tambah Lagu ke Playlist", command=add_song_to_playlist).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(self.main_frame, text="Hapus Lagu dari Playlist", command=remove_song_from_playlist).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(self.main_frame, text="Putar Playlist Ini", command=play_this_playlist).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(self.main_frame, text="Kembali ke Atur Playlist", command=self.buat_atur_playlist).pack(pady=10)

    # ========== QUEUE AND HISTORY VIEWS ==========
    
    def lihat_antrian(self):
        """Display the playback queue."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Antrian Pemutaran", font=("Arial", 14)).pack(pady=10)

        if self.playback_queue.is_empty():
            tk.Label(self.main_frame, text="Antrian kosong.").pack(pady=20)
        else:
            columns = ("No", "ID", "Judul", "Artis", "Album", "Genre", "Tahun", "File")
            tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15)
            tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor=tk.CENTER)

            for i, lagu in enumerate(list(self.playback_queue.items), 1):
                tree.insert('', tk.END, values=(i, lagu.id, lagu.judul, lagu.artis, lagu.album, lagu.genre, lagu.tahun, lagu.file_path))

        tk.Button(self.main_frame, text="Kembali ke Menu User", command=self.show_user_menu).pack(pady=10)

    def lihat_riwayat(self):
        """Display the playback history."""
        self.clear_frame()
        tk.Label(self.main_frame, text="Riwayat Pemutaran", font=("Arial", 14)).pack(pady=10)

        if self.playback_state['history'].is_empty():
            tk.Label(self.main_frame, text="Riwayat kosong.").pack(pady=20)
        else:
            columns = ("No", "ID", "Judul", "Artis", "Album", "Genre", "Tahun", "File")
            tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=15)
            tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor=tk.CENTER)

            for i, lagu in enumerate(reversed(self.playback_state['history'].items), 1):
                tree.insert('', tk.END, values=(i, lagu.id, lagu.judul, lagu.artis, lagu.album, lagu.genre, lagu.tahun, lagu.file_path))

        tk.Button(self.main_frame, text="Kembali ke Menu User", command=self.show_user_menu).pack(pady=10)
