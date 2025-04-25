import cv2
import requests
import time

# Адрес сервера для отправки кадров
server_url = 'http://192.168.1.31:12345/upload'

# Захват видео с веб-камеры (индекс 0 для встроенной камеры)
cap = cv2.VideoCapture(0)

# Проверка, удалось ли открыть камеру
if not cap.isOpened():
    print("Не удалось открыть веб-камеру")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Кодирование кадра в JPEG
    _, encoded_frame = cv2.imencode('.jpg', frame)
    # Создание временной метки
    timestamp = str(time.time())
    # Заголовки с временной меткой
    headers = {'Timestamp': timestamp}
    # Отправка кадра на сервер
    response = requests.post('http://192.168.1.31:12345/upload', 
                            data=encoded_frame.tobytes(), 
                            headers=headers)
    if response.status_code != 200:
        print("Ошибка при отправке кадра")
    # Небольшая задержка для имитации реального потока
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождение ресурсов
cap.release()