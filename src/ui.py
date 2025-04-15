import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.downloader import search_youtube, download_audio_files
from src.player import MusicPlayer
import threading
import os

class SoundSnapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎧 SoundSnap Downloader")
        self.root.geometry("950x600")
        self.root.configure(bg="#1e1e1e")
        self.search_query = tk.StringVar()
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.download_format = tk.StringVar(value="mp3")
        self.video_results = []
        self.player_window = None
        self.music_player = None

        self.set_styles()
        self.create_widgets()

    def set_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e")
        style.configure("TButton", padding=6, background="#292929", foreground="white")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("Treeview", background="#2c2c2c", foreground="white", fieldbackground="#2c2c2c")
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background="#383838", foreground="white")
        style.configure("TEntry", fieldbackground="#2e2e2e", foreground="white")
        style.configure("TRadiobutton", background="#1e1e1e", foreground="white")

    def create_widgets(self):
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Buscar (Artista/Álbum/Canción):").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_query, width=50)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: self.search_music())
        ttk.Button(search_frame, text="Buscar", command=self.search_music).pack(side=tk.LEFT)

        results_frame = ttk.Frame(self.root, padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(results_frame, columns=("Tipo", "Nombre"), show="headings", selectmode="extended")
        self.tree.bind("<Double-1>", lambda e: self.listen_selected())
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.column("Tipo", width=100, anchor=tk.CENTER)
        self.tree.column("Nombre", width=700)

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill=tk.X)

        ttk.Label(bottom_frame, text="Guardar en:").pack(side=tk.LEFT)
        ttk.Entry(bottom_frame, textvariable=self.download_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Seleccionar", command=self.select_directory).pack(side=tk.LEFT, padx=5)

        format_frame = ttk.Frame(bottom_frame)
        format_frame.pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(format_frame, text="MP3", variable=self.download_format, value="mp3").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="MP4", variable=self.download_format, value="mp4").pack(side=tk.LEFT)

        ttk.Button(bottom_frame, text="Escuchar", command=self.listen_selected).pack(side=tk.RIGHT)
        ttk.Button(bottom_frame, text="Descargar selección", command=lambda: self.start_download(False)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="Descargar todo", command=lambda: self.start_download(True)).pack(side=tk.RIGHT, padx=5)

    def search_music(self):
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("Error", "Ingresa un nombre de artista, álbum o canción.")
            return

        self.tree.delete(*self.tree.get_children())
        self.video_results = []

        try:
            search_results = search_youtube(query, 50)
            for entry in search_results:
                tipo = "Playlist" if "playlist" in entry.get("url", "") else "Video"
                titulo = entry["title"]
                video_url = entry["url"]
                self.video_results.append({'title': titulo, 'url': video_url})
                self.tree.insert("", tk.END, values=(tipo, titulo))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la búsqueda:\n{e}")

    def select_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)

    def start_download(self, download_all):
        threading.Thread(target=self.download_handler, args=(download_all,), daemon=True).start()

    def download_handler(self, download_all):
        if download_all:
            items = self.video_results
        else:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Error", "Selecciona uno o más elementos.")
                return
            items = [self.video_results[self.tree.index(i)] for i in selected]

        if not items:
            messagebox.showinfo("Info", "No hay elementos para descargar.")
            return

        download_audio_files(items, self.download_path.get(), self.root, self.download_format.get())

    def listen_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Reproducir", "Selecciona una canción para escuchar.")
            return
        idx = self.tree.index(selected[0])
        video = self.video_results[idx]

        if self.music_player:
            self.music_player.close()

        self.music_player = MusicPlayer(self.root, self.video_results, idx)
