import os
import yt_dlp
from src.cookies_helper import get_ydl_instance

def descargar_con_ytdlp(url, output_dir, format_type="mp3"):
    print(f"🛠️ Iniciando descarga de {url} en formato {format_type}")
    filename_template = os.path.join(output_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        'outtmpl': filename_template,
        'quiet': False,  # ← pon esto en False para ver logs
        'format': 'bestaudio/best' if format_type == "mp3" else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'ffmpeg_location': 'C:\\ffmpeg\\bin',
        'merge_output_format': 'mp4' if format_type == "mp4" else None,
    }

    if format_type == "mp3":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    print(f"📦 Opciones de yt-dlp:\n{ydl_opts}")

    from src.cookies_helper import get_ydl_instance
    with get_ydl_instance() as ydl:
        result = ydl.download([url])
        print(f"✅ Resultado de la descarga: {result}")


