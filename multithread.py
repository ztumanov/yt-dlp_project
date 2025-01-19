import concurrent.futures
import subprocess
import os
import json
from datetime import datetime

# Конфигурация
formats = [18, 599, 140, 133, 134, 135, 136, 137, 298, 299]
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
    downloaded_formats = []
    for fmt in formats:
        try:
            command = [
                "yt-dlp",
                "-f", str(fmt),
                "--cookies", cookies_file,
                "--output", output_template,
                "--write-info-json",
                url
            ]
            print(f"Запуск команды: {' '.join(command)}")
            subprocess.run(command, check=True)
            downloaded_formats.append(fmt)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при загрузке формата {fmt} для {url}: {e}")
    if downloaded_formats:
        end_time = datetime.now()
        log_download(url, start_time, end_time, downloaded_formats)
        update_metadata(url)

# Функция для записи информации о загруженных видео в лог
def log_download(url, start_time, end_time, formats):
    with open(log_file, "a") as log:
        log.write(f"{url} | Форматы: {', '.join(map(str, formats))}\nНачало: {start_time}\nКонец: {end_time}\n\n")

# Функция для обновления метаданных
def update_metadata(url):
    metadata_path = f"video/{url.split('=')[-1]}.info.json"
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

# Загрузка уже скачанных URL из лога
if os.path.exists(log_file):
    with open(log_file, "r") as log:
        downloaded_urls = set(line.strip().split(' | ')[0] for line in log if line.startswith("http"))
else:
    downloaded_urls = set()

with open(url_file, "r") as file:
    video_urls = [line.strip() for line in file if line.strip() and line.strip() not in downloaded_urls]

# Проверка наличия папки для вывода
os.makedirs("video", exist_ok=True)

# Объединенный файл метаданных
all_metadata = {}
if os.path.exists(metadata_file):
    with open(metadata_file, "r") as file:
        all_metadata = json.load(file)

# Многопоточная загрузка
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(download_video, url) for url in video_urls]
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Ошибка при обработке: {e}")

# Сохранение объединенного файла метаданных
with open(metadata_file, "w") as file:
    json.dump(all_metadata, file, ensure_ascii=False, indent=4)
