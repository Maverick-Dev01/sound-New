import yt_dlp
import os

def get_ydl_instance():
    cookies_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cookies.txt"))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Referer": "https://www.youtube.com/",
    }

    if os.path.exists(cookies_path):
        print("✅ Usando cookies.txt")
        return yt_dlp.YoutubeDL({
            'cookies': cookies_path,
            'quiet': True,
            'http_headers': headers,
        })
    else:
        print("⚠️ No se encontró cookies.txt. Continuando sin cookies (puede fallar)")
        return yt_dlp.YoutubeDL({
            'quiet': True,
            'http_headers': headers,
        })

