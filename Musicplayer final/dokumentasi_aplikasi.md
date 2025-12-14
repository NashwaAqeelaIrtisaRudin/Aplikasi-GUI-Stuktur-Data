# Dokumentasi Aplikasi Music Player

## Deskripsi Singkat
Aplikasi Music Player ini adalah perangkat lunak pemutar musik berbasis desktop yang dibangun menggunakan bahasa pemrograman Python dan pustaka Tkinter untuk antarmuka pengguna (GUI). Aplikasi ini memungkinkan pengguna untuk memutar lagu, mengelola playlist, dan mengatur antrian pemutaran.

## Fitur Utama

Aplikasi memiliki dua peran pengguna: **Admin** dan **User**.

### 1. Fitur Admin
Admin bertugas untuk mengelola database lagu.
*   **Tambah Lagu Baru**: Menambahkan metadata lagu (Judul, Artis, Album, Genre, Tahun) dan lokasi file audio.
*   **Lihat Semua Lagu**: Menampilkan daftar seluruh lagu yang ada di perpustakaan.
*   **Ubah Data Lagu**: Mengedit informasi lagu yang sudah ada.
*   **Hapus Lagu**: Menghapus lagu dari perpustakaan (juga menghapusnya dari playlist yang relevan).

### 2. Fitur User (Pengguna)
User adalah pengguna umum yang ingin mendengarkan musik.
*   **Cari Lagu**: Mencari lagu berdasarkan ID, Judul, atau Artis.
*   **Putar Lagu (Dari Library)**:
    *   Memilih dan memutar lagu langsung dari daftar utama.
    *   **Fitur Tambah ke Antrian**: Menambahkan lagu ke dalam antrian pemutaran tanpa menghentikan lagu saat ini.
*   **Buat/Atur Playlist**: Membuat playlist pribadi dan menambahkan/menghapus lagu di dalamnya.
*   **Lihat Antrian Pemutaran**: Melihat daftar lagu yang akan diputar selanjutnya.
*   **Lihat Riwayat Pemutaran**: Melihat daftar lagu yang baru saja diputar.

### 3. Kontrol Pemutaran
*   **Play/Pause/Resume**: Mengendalikan jalannya lagu.
*   **Stop**: Menghentikan pemutaran sepenuhnya.
*   **Next (Lagu Berikutnya)**:
    *   Jika dalam mode Playlist: Memutar lagu selanjutnya di playlist.
    *   Jika bukan mode Playlist: Memutar lagu dari antrian (jika ada) atau mencari lagu yang mirip (rekomendasi).
*   **Prev (Lagu Sebelumnya)**:
    *   Jika dalam mode Playlist: Memutar lagu sebelumnya di playlist.
    *   Jika bukan mode Playlist: Memutar lagu terakhir dari riwayat.
*   **Autoplay**: Fitur otomatis memutar lagu selanjutnya ketika lagu saat ini selesai.

## Struktur Data Teknis
Aplikasi ini menggunakan berbagai struktur data untuk efisiensi:
*   **Singly Linked List**: Digunakan untuk menyimpan daftar seluruh lagu di **Library**.
*   **Doubly Linked List**: Digunakan untuk **Playlist**, memungkinkan navigasi lagu sebelumnya/selanjutnya dengan mudah.
*   **Queue (Antrian)**: Digunakan untuk fitur **Antrian Pemutaran** (FIFO - First In First Out).
*   **Stack (Tumpukan)**: Digunakan untuk **Riwayat Pemutaran** (LIFO - Last In First Out).

## Cara Menjalankan Aplikasi
1.  Pastikan Python dan pustaka `pygame` serta `tkinter` sudah terinstal.
2.  Jalankan file `main.py` melalui terminal atau IDE favorit Anda.
3.  Login sesuai peran yang diinginkan.
