from tkinter import *
from tkinter import filedialog, ttk
import yt_dlp
from moviepy.editor import *
import os
import threading
################################################################
def download():
    video_url = url_entry.get()
    save_path = path_label.cget('text')

    def progress_hook(d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percent = int(downloaded * 100 / total)
            progress_bar['value'] = percent
            progress_label.config(text=f"Downloaded: {percent}%")
        elif d['status'] == 'finished':
            progress_label.config(text="Download complete")
            progress_bar['value'] = 100

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        video_title = info_dict.get('title', None)
        video_ext = info_dict.get('ext', None)

    video_file_path = f"{save_path}/{video_title}.{video_ext}"

    # Вывод пути файла для отладки
    print(f"Загруженный файл: {video_file_path}")

    # Ждём, пока файл будет полностью загружен
    while not os.path.exists(video_file_path):
        time.sleep(1)

    # Конвертация видео в MP3 с помощью moviepy
    try:
        video = VideoFileClip(video_file_path)
        audio_file_path = f"{save_path}/{video_title}.mp3"
        video.audio.write_audiofile(audio_file_path)
        video.close()
        progress_label.config(text="Conversion to MP3 complete")
    except Exception as e:
        progress_label.config(text=f"Error: {str(e)}")

    progress_bar.stop()

def start_download():
    threading.Thread(target=download).start()

def get_path():
    path = filedialog.askdirectory()
    if path:
        path_label.config(text=path)
    else:
        raise Exception("Choose a directory")

root = Tk()
root.title('Video Downloader')
canvas = Canvas(root, width=400, height=400)
canvas.pack()

app_label = Label(root, text="Download")
canvas.create_window(200, 20, window=app_label)

url_label = Label(root, text="Enter URL")
canvas.create_window(200, 80, window=url_label)

url_entry = Entry(root)
canvas.create_window(200, 105, window=url_entry)

path_label = Label(root, text='Select path to download')
path_button = Button(root, text='Select', command=get_path)

canvas.create_window(200, 130, window=path_label)
canvas.create_window(200, 150, window=path_button)

download_button = Button(root, text='Download', command=start_download)
canvas.create_window(200, 220, window=download_button)

progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
canvas.create_window(200, 270, window=progress_bar)

progress_label = Label(root, text="")
canvas.create_window(200, 300, window=progress_label)

root.mainloop()
