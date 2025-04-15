import yt_dlp

from src.utils import descargar_con_ytdlp


def search_youtube(query, max_results=50):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        return [{'title': e['title'], 'url': f"https://www.youtube.com/watch?v={e['id']}"} for e in search['entries']]


def download_audio_files(items, download_path, root, format_type="mp3"):
    import tkinter as tk
    from tkinter import ttk
    import os

    progress_win = tk.Toplevel(root)
    progress_win.title("Descargando...")
    progress_win.geometry("500x100")
    label = ttk.Label(progress_win, text="Iniciando descargas...")
    label.pack(pady=10)
    progress = ttk.Progressbar(progress_win, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=5)
    progress["maximum"] = len(items)

    for idx, video in enumerate(items, start=1):
        print(f"▶️ Preparando descarga del video: {video['title']} - URL: {video['url']}")
        label.config(text=f"Descargando: {video['title']}")
        try:
            descargar_con_ytdlp(video['url'], download_path, format_type)
        except Exception as e:
            print(f"❌ Error descargando {video['title']}: {e}")

        progress["value"] = idx
        progress_win.update()

