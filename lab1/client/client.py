import socket
from PIL import Image
import io
import random
import numpy as np

def simulate_noise(data, probability=0.01):
    """Симуляция импульсного шума: с вероятностью probability изменяет байты в потоке."""
    data_list = list(data)
    for i in range(len(data_list)):
        if random.random() < probability:
            data_list[i] = random.randint(0, 255)
    return bytes(data_list)


def add_impulse_noise(img, probability=0.01):
    """Добавляет импульсный шум к пикселям изображения."""
    img_array = np.array(img)
    noisy_img = img_array.copy()
    h, w = noisy_img.shape[:2]
    
    for i in range(h):
        for j in range(w):
            if random.random() < probability:
                # Случайно устанавливаем пиксель в белый (255) или черный (0)
                noisy_img[i, j] = random.choice([0, 255])
    return Image.fromarray(noisy_img)

def send_image(image_path, host, port, noise_probability=0.01):
    """Загружает изображение, добавляет шум и отправляет на сервер."""
    # Загрузка изображения
    img = Image.open(image_path).convert('RGB')
    # Сериализация в байты
    noise_image = add_impulse_noise(img, noise_probability)

    img_byte_arr = io.BytesIO()
    noise_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Добавление импульсного шума
    #noisy_data = simulate_noise(img_byte_arr, probability=noise_probability)
    
    # Создание сокета и подключение к серверу
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    print(f'Данных отправлено:{len(img_byte_arr)}')
    # Отправка данных
    sock.sendall(img_byte_arr)
    sock.shutdown(socket.SHUT_WR)
    sock.close()
    print("Изображение с шумом отправлено на сервер.")

# Пример вызова
if __name__ == "__main__":
    image_path = 'D:\\арты на рабочий стол\\image.png'  # Путь к вашему изображению
    host = "192.168.1.31"        # IP-адрес сервера
    port = 12345              # Порт сервера
    send_image(image_path, host, port, noise_probability=0.01)