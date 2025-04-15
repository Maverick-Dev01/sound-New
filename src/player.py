import os
import sys  # ✅ IMPORTANTE para compatibilidad con PyInstaller
import tkinter as tk
from tkinter import ttk, messagebox
import vlc
import yt_dlp
from src.cookies_helper import get_ydl_instance


class MusicPlayer:
    def __init__(self, root, video_list, start_index=0):
        self.root = root
        self.video_list = video_list
        self.index = start_index
        self.instance = None
        self.player = None
        self.progress_var = tk.DoubleVar()
        self.timer = None

        self.setup()

    def setup(self):
        self.close()

        # ✅ Ruta compatible con PyInstaller (exe) y entorno normal
        # Solo agrega path si estás usando VLC portable (y tú ya no lo harás)
        # vlc_path = os.path.abspath("vlc")
        # os.add_dll_directory(vlc_path)
        try:
            import vlc
        except ImportError:
            messagebox.showerror("Error",
                                 "VLC no está instalado. Por favor, instálalo desde https://www.videolan.org/vlc/")
            return

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.window = tk.Toplevel(self.root)
        self.window.title("🎵 Reproduciendo")
        self.window.geometry("400x250")
        self.window.configure(bg="#111111")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        # Título
        tk.Label(self.window, text=self.video_list[self.index]['title'],
                 font=("Segoe UI", 11, "bold"), fg="white", bg="#111111", wraplength=380,
                 justify="center").pack(pady=(20, 10))

        # Tiempo actual y duración
        time_frame = tk.Frame(self.window, bg="#111111")
        time_frame.pack(fill=tk.X, padx=30)

        self.current_time_lbl = tk.Label(time_frame, text="0:00", fg="gray", bg="#111111", font=("Segoe UI", 9))
        self.current_time_lbl.pack(side=tk.LEFT)

        self.total_time_lbl = tk.Label(time_frame, text="0:00", fg="gray", bg="#111111", font=("Segoe UI", 9))
        self.total_time_lbl.pack(side=tk.RIGHT)

        # Progreso
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Horizontal.TScale", troughcolor="#222222", background="#e91e63", sliderlength=10)

        self.progress = ttk.Scale(self.window, variable=self.progress_var,
                                  orient="horizontal", from_=0, to=100, command=self.seek,
                                  style="Horizontal.TScale")
        self.progress.pack(fill=tk.X, padx=30, pady=10)

        # Controles
        control_frame = tk.Frame(self.window, bg="#111111")
        control_frame.pack(pady=15)

        btn_cfg = {"font": ("Segoe UI", 12), "bg": "#1c1c1c", "fg": "white", "width": 3, "bd": 0, "relief": "flat"}

        tk.Button(control_frame, text="⏮", command=self.prev, **btn_cfg).grid(row=0, column=0, padx=6)
        tk.Button(control_frame, text="⏸", command=self.toggle_pause, **btn_cfg).grid(row=0, column=1, padx=6)
        tk.Button(control_frame, text="⏹", command=self.stop, **btn_cfg).grid(row=0, column=2, padx=6)
        tk.Button(control_frame, text="⏭", command=self.next, **btn_cfg).grid(row=0, column=3, padx=6)
        tk.Button(control_frame, text="🔁", command=self.restart, **btn_cfg).grid(row=0, column=4, padx=6)

        self.play(self.video_list[self.index]['url'])

    def get_audio_url(self, url):
        try:
            with get_ydl_instance() as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get("formats", [])
                best_audio = next((f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"), None)
                return best_audio.get("url") if best_audio else None
        except Exception as e:
            print(f"❌ Error obteniendo el stream de audio: {e}")
            return None

    def play(self, url):
        media_url = self.get_audio_url(url)

        if not media_url:
            messagebox.showerror(
                "Error",
                f"No se pudo reproducir el contenido desde la URL:\n{url}\n\n❗ Posibles causas:\n- Video restringido\n- Cookies caducadas\n- Bloqueo regional\n- No tienes internet"
            )
            return

        media = self.instance.media_new(media_url)
        self.player.set_media(media)
        self.player.audio_set_volume(100)
        self.player.play()
        self.update_progress()
        self.check_vlc_window()

    def update_progress(self):
        if self.player is None:
            return
        try:
            if self.player.get_length() > 0:
                current = self.player.get_time()
                total = self.player.get_length()
                percentage = (current / total) * 100 if total > 0 else 0
                self.progress_var.set(percentage)

                # Actualizar tiempo en etiquetas
                self.current_time_lbl.config(text=self.format_time(current))
                self.total_time_lbl.config(text=self.format_time(total))

            self.timer = self.window.after(500, self.update_progress)
        except:
            pass

    def check_vlc_window(self):
        if self.player is None:
            return
        state = self.player.get_state()
        if state in [vlc.State.Ended, vlc.State.Stopped, vlc.State.Error]:
            self.close()
        else:
            self.window.after(1000, self.check_vlc_window)

    def seek(self, value):
        if self.player.get_length() > 0:
            new_time = (float(value) / 100) * self.player.get_length()
            self.player.set_time(int(new_time))

    def toggle_pause(self):
        if self.player:
            self.player.pause()

    def restart(self):
        if self.player:
            self.player.set_time(0)

    def stop(self):
        if self.timer:
            self.window.after_cancel(self.timer)
            self.timer = None
        if self.player:
            self.player.stop()
        self.window.destroy()

    def next(self):
        self.index = (self.index + 1) % len(self.video_list)
        self.setup()

    def prev(self):
        self.index = (self.index - 1) % len(self.video_list)
        self.setup()

    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def close(self):
        try:
            if self.timer:
                self.window.after_cancel(self.timer)
                self.timer = None
            if self.player:
                self.player.stop()
                self.player.release()
                self.player = None
            if self.instance:
                self.instance.release()
                self.instance = None
            if hasattr(self, "window") and self.window.winfo_exists():
                self.window.destroy()
        except:
            pass
