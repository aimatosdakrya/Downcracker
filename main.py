import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage, ttk
import yt_dlp
import threading

# FOR DOWNLOAD EXECUTION CONTROL
stop_download = False

# TO DETERMINE THE BASE DIRECTORY - DO NOT TOUCH THIS IF YOU DON'T KNOW WHAT YOU'RE DOING
def resource_path(relative_path):
    """ RETURNS THE ABSOLUTE PATH, HANDLING THE COMPILED EXECUTABLE """
    if getattr(sys, 'frozen', False):  
        base_path = sys._MEIPASS
    else:  
        base_path = os.path.abspath(".")
    full_path = os.path.join(base_path, relative_path)
    print(f"Resource path for {relative_path}: {full_path}")  # Debug print
    return full_path

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        label_directory.config(text=directory)
    else:
        label_directory.config(text="NO DIRECTORY SELECTED")

def download_video():
    global stop_download
    stop_download = False
    url = entry_url.get()
    directory = label_directory.cget("text")
    
    if not url:
        messagebox.showwarning("ERROR:", "ENTER THE VIDEO URL")
        return
    if directory == "NO DIRECTORY SELECTED":
        messagebox.showwarning("ERROR", "SELECT THE DIRECTORY TO SAVE THE VIDEO")
        return

    # REDIRECTS THE OUTPUT OF "yt_dlp" TO THE "Text widget"
    def write_log(text):
        text_output.insert(tk.END, text + "\n")
        text_output.see(tk.END)  # AUTO SCROLL

    # CUSTOM LOGGER CLASS
    class MyLogger:
        def debug(self, msg):
            write_log(msg)
        def warning(self, msg):
            write_log(f"WARNING: {msg}")
        def error(self, msg):
            write_log(f"ERROR: {msg}")

    def run_download():
        try:
            # UPDATE THE PROGRESS
            def progress_hook(d):
                if d['status'] == 'downloading':
                    p = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
                    progress_var.set(p)
                    write_log(f"Downloading: {d.get('filename', '')} ({d.get('info_dict', {}).get('title', '')})")
                if stop_download:
                    raise Exception("DOWNLOAD INTERRUPTED")

            # REMOVE GENERAL DEPENDENCY ON "FFmpeg"
            ydl_opts = {
                'outtmpl': f'{directory}/%(title)s.%(ext)s',
                'logger': MyLogger(),
                'progress_hooks': [progress_hook],
                'noplaylist': not checkbox_playlist_var.get(),
                'format': 'bestaudio/best' if checkbox_audio_var.get() else 'best',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            messagebox.showinfo(title='SUCCESS', message='DOWNLOAD COMPLETED')
        except Exception as e:
            write_log(f"ERROR {e}")
            messagebox.showerror("ERROR", f"Error: {e}")

    threading.Thread(target=run_download).start()

def stop_download():
    global stop_download
    stop_download = True

def exit_application():
    root.destroy()

# GENERAL SETTINGS
root = tk.Tk()

# IMAGES USED IN THE GRAPHICAL INTERFACE
icon_path = resource_path("downcracker.png")
logo_path = resource_path("downlogo.png")

# CHECK IF IMAGE FILES EXIST
if not os.path.isfile(icon_path):
    raise FileNotFoundError(f"Icon file not found: {icon_path}")

if not os.path.isfile(logo_path):
    raise FileNotFoundError(f"Logo file not found: {logo_path}")

icon = PhotoImage(file=icon_path)
root.iconphoto(True, icon)
root.title("DOWNCRACKER v2.2")
root.geometry("900x850")  
root.resizable(width=False, height=False)
root.config(bg="#000000")

# TITLE-LOGO
logo_image = PhotoImage(file=logo_path)
label_logo = tk.Label(root, image=logo_image, bg="#000000")
label_logo.pack(pady=20)

# URL
label_url = tk.Label(root, text="YOUTUBE LINK:", fg="red", bg="#000000", font=("Helvetica", 12, "bold"))
label_url.pack(pady=0)

entry_url = tk.Entry(root, width=50, font=("Helvetica", 12))
entry_url.pack(pady=5)

# STORAGE DIRECTORY
btn_directory = tk.Button(root, text="STORAGE LOCATION", command=select_directory, bg="#00ff00", fg="black", font=("Helvetica", 12, "bold"), width=25)
btn_directory.pack(pady=20)

# SELECTED DIRECTORY
label_directory = tk.Label(root, text="NO DIRECTORY SELECTED", fg="red", bg="#000000", font=("Helvetica", 12, "bold"))
label_directory.pack(pady=0)

# CHECKBOX FOR PLAYLISTS
checkbox_playlist_var = tk.BooleanVar()
checkbox_playlist = tk.Checkbutton(root, text="IF IN A PLAYLIST, DOWNLOAD ENTIRE PLAYLIST?", variable=checkbox_playlist_var, bg="#000000", fg="red", font=("Helvetica", 12, "bold"))
checkbox_playlist.pack(pady=10)

# CHECKBOX TO DOWNLOAD AUDIO ONLY
checkbox_audio_var = tk.BooleanVar()
checkbox_audio = tk.Checkbutton(root, text="DOWNLOAD AUDIO ONLY", variable=checkbox_audio_var, bg="#000000", fg="red", font=("Helvetica", 12, "bold"))
checkbox_audio.pack(pady=10)

# FRAME FOR BUTTONS
frame_buttons = tk.Frame(root, bg="#000000")
frame_buttons.pack(pady=20)

# DOWNLOAD BUTTON
btn_download = tk.Button(frame_buttons, text="START", command=download_video, bg="#00ff00", fg="black", font=("Helvetica", 12, "bold"), width=7)
btn_download.pack(side=tk.LEFT, padx=10)

# STOP BUTTON
btn_stop = tk.Button(frame_buttons, text="STOP", command=stop_download, bg="red", fg="black", font=("Helvetica", 12, "bold"), width=7)
btn_stop.pack(side=tk.LEFT, padx=10)

# TEXT OUTPUT FOR "yt_dlp"
label_output_title = tk.Label(root, text="DOWNLOAD PROCESS", fg="red", bg="#000000", font=("Helvetica", 12, "bold"))
label_output_title.pack(pady=(10, 0))  

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=800)
progress_bar.pack(pady=10)

text_output = tk.Text(root, height=20, width=124, bg="#000000", fg="red", font=("Helvetica", 10))
text_output.pack(pady=10)

# STATUS LABEL
label_status = tk.Label(root, text="", fg="white", bg="#000000", font=("Helvetica", 12, "bold"))
label_status.pack(pady=5)

# MAIN GUI LOOP
root.mainloop()
