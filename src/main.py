from src.ui import SoundSnapApp

if __name__ == "__main__":
    import tkinter as tk
    import os
    import sys

    root = tk.Tk()

    # Construir la ruta completa al ícono
    ico_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "assets", "icono_soundsnap.ico"))

    # Verificar si el archivo .ico existe antes de configurarlo
    if os.path.exists(ico_path):
        try:
            root.iconbitmap(ico_path)
        except Exception as e:
            print(f"Advertencia: No se pudo establecer el ícono con el archivo ubicado en '{ico_path}'. Error: {e}")
    else:
        print(
            f"Advertencia: El archivo de ícono '{ico_path}' no existe. Asegúrese de que el archivo se encuentra en la ubicación correcta.")

    # Inicializar la aplicación
    app = SoundSnapApp(root)
    root.mainloop()
