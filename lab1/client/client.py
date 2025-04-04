import socket
import cv2
import numpy as np

# Функция добавления импульсного шума
def add_impulse_noise(image, probability):
    noisy = image.copy()
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            for k in range(3):  # для каждого канала (R, G, B)
                if np.random.random() < probability:
                    noisy[i, j, k] = 255 if np.random.random() < 0.5 else 0
    return noisy

def send_image(image_path, host, port, noise_probability=0.05):
    # Создание TCP-сокета
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Загрузка изображения (grayscale)
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print("Ошибка: изображение не загружено.")
        return

    # Добавление импульсного шума (5% пикселей)
    noisy_image = add_impulse_noise(image, noise_probability)
    cv2.imwrite('noisy_image.png', noisy_image)  # Сохранение для сравнения

    # Отправка размеров изображения
    height, width, channels = image.shape
    client.sendall(height.to_bytes(4, 'big'))
    client.sendall(width.to_bytes(4, 'big'))
    client.sendall(channels.to_bytes(4, 'big'))

    # Отправка данных изображения
    data = noisy_image.tobytes()
    client.sendall(len(data).to_bytes(4, 'big'))
    client.sendall(data)

    print("Изображение отправлено.")
    client.close()

if __name__ == '__main__':
    image_path = 'image.png'     # Путь к изображению
    host = "192.168.1.31"        # IP-адрес сервера
    port = 12345                 # Порт сервера
    send_image(image_path, host, port, noise_probability=0.05)