from flask import Flask, Response, request
import cv2
import numpy as np
import time

app = Flask(__name__)

# Переменная для хранения последнего обработанного кадра
last_frame = None

@app.route('/upload', methods=['POST'])
def upload():
    global last_frame
    # Получение JPEG-кадра от клиента
    data = request.data
    # Извлечение временной метки из заголовка (если нет, используется текущее время)
    timestamp = request.headers.get('Timestamp', str(time.time()))
    nparr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Обработка кадра (выделение контуров)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    # Наложение временной метки на изображение
    cv2.putText(edges, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # Сжатие обработанного кадра в JPEG
    last_frame = cv2.imencode('.jpg', edges)[1].tobytes()
    return 'OK'

def generate_stream():
    global last_frame
    while True:
        if last_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
        else:
            # Если кадра нет, отправляем пустой ответ
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')

@app.route('/stream')
def stream():
    return Response(generate_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345)