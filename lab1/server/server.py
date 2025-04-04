import socket
import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr

# Функция медианного фильтра
def median_filter(image, kernel_size=3):
    return cv2.medianBlur(image, kernel_size)

def calculate_psnr(original, distorted):
    """Вычисляет PSNR между оригинальным и искаженным изображениями."""
    original = np.array(original)
    distorted = np.array(distorted)
    return psnr(original, distorted)

def receive_image(port, original_img_path):
    # Создание TCP-сокета
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    print('Ожидание подключения...')

    conn, addr = server.accept()
    print('Подключено:', addr)

    # Прием размеров изображения
    height = int.from_bytes(conn.recv(4), 'big')
    width = int.from_bytes(conn.recv(4), 'big')
    channels = int.from_bytes(conn.recv(4), 'big')

    # Прием размера данных
    data_size = int.from_bytes(conn.recv(4), 'big')
    data = b''
    while len(data) < data_size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    # Преобразование данных в изображение
    image = np.frombuffer(data, dtype=np.uint8).reshape((height, width,channels))

    # Сохранение зашумленного изображения
    cv2.imwrite('received_noisy_image.png', image)
    print(f'Изобажение сохранено как received_noisy_image.png')

    # Применение медианного фильтра
    restored_image = median_filter(image)
    cv2.imwrite('restored_image.png', restored_image)
    print(f'Фильтр применен, изображение сохранено как restored_image.png')

    print("Изображение обработано и сохранено.")

    original_img = cv2.imread(original_img_path, cv2.IMREAD_COLOR)


    psnr_noisy = calculate_psnr(original_img, image)
    psnr_filtered = calculate_psnr(original_img, restored_image)
    print(f"PSNR зашумленного изображения: {psnr_noisy:.2f} dB")
    print(f"PSNR восстановленного изображения: {psnr_filtered:.2f} dB")
    

    conn.close()
    server.close()

if __name__ == '__main__':
    port = 12345
    original_img_path = 'original_image.png'
    receive_image(port, original_img_path)