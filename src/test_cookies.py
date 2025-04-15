import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cookies_helper import get_ydl_instance

url = "https://www.youtube.com/watch?v=pDddlvCfTiw"

with get_ydl_instance() as ydl:
    info = ydl.extract_info(url, download=False)
    print("✅ Título del video:", info["title"])
