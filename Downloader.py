import requests


def download_file(url, filename):
    # Отправка запроса на URL
    response = requests.get(url, stream=True)

    # Проверка успешности запроса
    if response.status_code == 200:
        # Открытие файла для записи данных
        with open(filename, 'wb') as file:
            # Сохранение файла по частям
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"{filename} был успешно загружен.")
    else:
        print("Ошибка при попытке скачать файл.")


# Пример использования
url = "https://kinokong.bz/74145-1-golovolomka-2.html"  # замените на действительный URL
filename = "video.mp4"
download_file(url, filename)