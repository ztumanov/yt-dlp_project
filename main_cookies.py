import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Константы
CHROME_PROFILE_PATH = r"C:\Users\admin\AppData\Local\Google\Chrome\User Data"
LOCAL_COOKIES_PATH = r"C:\Scripts\cookies.txt"
PRIVATE_KEY_PATH = r"C:\Scripts\id_rsa"
SERVER_USER = "#"
SERVER_IP = "#"
REMOTE_COOKIES_PATH = "/usr/script/cookies.txt"


def extract_cookies():
    """Извлечение cookies с помощью Selenium."""
    try:
        # Настройка Chrome WebDriver
        options = Options()
        options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
        options.add_argument("profile-directory=Default")  # Используем профиль по умолчанию

        # Запуск WebDriver
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.youtube.com")
        time.sleep(5)  # Ожидаем загрузку страницы

        # Проверяем авторизацию
        if "Sign in" not in driver.page_source:
            print("Мы авторизованы!")
        else:
            print("Не удалось авторизоваться.")
            driver.quit()
            return False

        # Извлекаем cookies
        cookies = driver.get_cookies()
        with open(LOCAL_COOKIES_PATH, "w") as file:
            file.write("# Netscape HTTP Cookie File\n")
            file.write("# http://curl.haxx.se/rfc/cookie_spec.html\n")
            file.write("# This is a generated file! Do not edit.\n\n")
            for cookie in cookies:
                expiry = cookie.get('expiry', '')
                file.write(
                    f"{cookie['domain']}\tTRUE\t{cookie['path']}\t{str(cookie['secure']).upper()}\t{expiry}\t{cookie['name']}\t{cookie['value']}\n"
                )
        print(f"Cookies сохранены в {LOCAL_COOKIES_PATH}")
        driver.quit()
        return True
    except Exception as e:
        print(f"Ошибка при извлечении cookies: {e}")
        return False


def transfer_cookies_via_scp():
    """Передача cookies на сервер с использованием SCP через subprocess."""
    try:
        # Проверяем наличие ключа
        if not os.path.exists(PRIVATE_KEY_PATH):
            print(f"Файл ключа {PRIVATE_KEY_PATH} не найден.")
            return False

        # Формируем команду SCP
        scp_command = [
            "scp",
            "-i", PRIVATE_KEY_PATH,
            LOCAL_COOKIES_PATH,
            f"{SERVER_USER}@{SERVER_IP}:{REMOTE_COOKIES_PATH}"
        ]
        
        # Выполняем команду SCP
        result = subprocess.run(scp_command, check=True, text=True, capture_output=True)
        
        if result.returncode == 0:
            print(f"Cookies успешно переданы на сервер {SERVER_IP}.")
            return True
        else:
            print(f"Ошибка при передаче cookies: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении SCP: {e.stderr}")
        return False
    except Exception as e:
        print(f"Общая ошибка: {e}")
        return False


if __name__ == "__main__":
    print("Начинаем выполнение скрипта каждые 5 минут.")
    while True:
        try:
            if extract_cookies():
                if transfer_cookies_via_scp():
                    print("Процесс завершён успешно.")
                else:
                    print("Ошибка при передаче cookies.")
            else:
                print("Ошибка при извлечении cookies.")
        except Exception as e:
            print(f"Общая ошибка выполнения скрипта: {e}")
        
        # Ждём 5 минут перед следующим запуском
        print("Ждём 5 минут перед следующим выполнением...")
        time.sleep(300)  # 300 секунд = 5 минут
