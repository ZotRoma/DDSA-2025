import cv2
import pytesseract
import time

# URL сервера с MJPEG-потоком
stream_url = 'http://192.168.1.31:12345/stream'

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
    # Извлечение области с временной меткой (верхний левый угол, 40x200 пикселей)
    text_region = frame[0:40, 0:200]
    # Используем OCR для извлечения текста
    timestamp_str = pytesseract.image_to_string(text_region)
    try:
        timestamp = float(timestamp_str.strip())
        current_time = time.time()
        latency = current_time - timestamp
        print(f"Задержка: {latency:.3f} секунд")
        # Отображение задержки на кадре
        cv2.putText(frame, f"Latency: {latency:.3f}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    except ValueError:
        print("Не удалось извлечь временную метку")
    
    # Отображаем кадр
    cv2.imshow('Видеопоток с сервера', frame)
    # Нажмите 'q' для выхода
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Освобождаем ресурсы
cap.release()
cv2.destroyAllWindows()