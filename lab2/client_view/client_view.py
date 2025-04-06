import cv2

# URL сервера с MJPEG-потоком
stream_url = 'http://192.168.1.32:12345/stream'

# Открываем поток
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Не удалось открыть видеопоток")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Не удалось получить кадр")
        break
    # Отображаем кадр
    cv2.imshow('Видеопоток с сервера', frame)
    # Нажмите 'q' для выхода
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()