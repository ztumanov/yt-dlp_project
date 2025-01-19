import subprocess
import os
import json
from datetime import datetime
import concurrent.futures

# Конфигурация
formats = "18,599,140,133,134,135,136,137,298,299"
cookies_file = "cookies.txt"
output_template = "video/%(id)s.f%(format_id)s.%(ext)s"
num_threads = 4  # Количество потоков

# Путь к файлу со списком URL
url_file = "video_urls.txt"
log_file = "download_log.txt"  # Файл журнала скачанных видео
metadata_file = "metadata.json"  # Файл метаданных

# Функция для загрузки одного видео
def download_video(url):
    start_time = datetime.now()
    try:
        command = [
            "yt-dlp",
            "-f", formats,
            "--cookies", cookies_file,
            "--output", output_template,
            "--write-info-json",
            url
        ]
        print(f"Запуск команды: {' '.join(command)}")
        subprocess.run(command, check=True)
        end_time = datetime.now()
        log_download(url, start_time, end_time)
        update_metadata(url)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при загрузке видео {url}: {e}")

# Функция для записи информации о загруженных видео в лог
def log_download(url, start_time, end_time):
    with open(log_file, "a") as log:
        log.write(f"{url} скачано.\nНачало: {start_time}\nКонец: {end_time}\n\n")

# Функция для обновления метаданных
def update_metadata(url):
    video_id = url.split('=')[-1]
    metadata_path = f"video/{video_id}.info.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as meta_file:
            metadata = json.load(meta_file)

        # Загрузка существующих метаданных
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as file:
                all_metadata = json.load(file)
        else:
            all_metadata = {}

        # Добавление новых метаданных
        all_metadata[url] = metadata

        # Сохранение метаданных
        with open(metadata_file, "w") as file:
            json.dump(all_metadata, file, ensure_ascii=False, indent=4)

# Чтение URL из файла
if not os.path.exists(url_file):
    print(f"Файл {url_file} не найден.")
    exit(1)

with open(url_file, "r") as file:
    video_urls = [line.strip() for line in file if line.strip()]

# Проверка наличия папки для вывода
os.makedirs("video", exist_ok=True)

# Многопоточная загрузка
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(download_video, url) for url in video_urls]
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Ошибка при обработке: {e}")
