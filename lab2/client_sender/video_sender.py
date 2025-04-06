import cv2
import requests

# Адрес сервера для отправки кадров
server_url = 'http://192.168.1.32:12345/upload'

# Захват видео с веб-камеры (индекс 0 для встроенной камеры)
cap = cv2.VideoCapture(0)

# Проверка, удалось ли открыть камеру
if not cap.isOpened():
    print("Не удалось открыть веб-камеру")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Ошибка захвата видео")
        break
    # Сжатие кадра в JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    # Отправка кадра на сервер
    try:
        requests.post(server_url, data=buffer.tobytes(), headers={'Content-Type': 'image/jpeg'})
    except Exception as e:
        print(f"Ошибка отправки: {e}")

# Освобождение ресурсов
cap.release()