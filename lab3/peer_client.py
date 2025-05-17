import asyncio
import struct

BLOCK_SIZE = 16384  # 16 KiB

class PeerClientError(Exception):
    pass

class PeerClient:
    def __init__(self, ip: str, port: int, info_hash: bytes, peer_id: bytes):
        if not isinstance(info_hash, (bytes, bytearray)):
            raise PeerClientError(f"info_hash must be bytes, got {type(info_hash)}")
        if not isinstance(peer_id, (bytes, bytearray)):
            raise PeerClientError(f"peer_id must be bytes, got {type(peer_id)}")

        self.ip = ip
        self.port = port
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.reader = None # чтение из сокета StreamReader
        self.writer = None # загрузка в сокет StreamWriter

    # рукопожатие 
    async def handshake(self):
        pstr = b"BitTorrent protocol"
        packet = struct.pack("!B19s8x20s20s", len(pstr), pstr, self.info_hash, self.peer_id) # байтовое сообщение рукопожатия
        self.reader, self.writer = await asyncio.wait_for(              # ожидаем пока не произойдет
            asyncio.open_connection(self.ip, self.port), timeout=10     # создание асинхронного TCP соединения
        )
        self.writer.write(packet)                                       # сформированное сообщение рукопожатия
        resp = await asyncio.wait_for(self.reader.readexactly(68), timeout=10) # читаем ровно 68 байт ответа от пира
        if resp[1:20] != pstr or resp[28:48] != self.info_hash:     # сравниваем байты 1-19 с b"BitTorrent protocol", чтобы убедиться что тот же протокол
            raise PeerClientError("Invalid handshake response")     # байты 28–47 ответа с info_hash - работает с тем же торентом

    async def send_interested(self):        # отправляем пиру interested, чтобы сказать, что клиент хочет скачать данные
        msg = struct.pack("!IB", 1, 2)      # формируем сообщение interested
        self.writer.write(msg)              # отправляем пиру

    async def wait_unchoke(self):           # ожидаем unchoke от пира
        while True:
            header = await asyncio.wait_for(self.reader.readexactly(4), timeout=5) # читаем 4 байта заголовка сообщения
            length = struct.unpack("!I", header)[0]                                # распаковывает 4 байта заголовка в целое число - размер сообщения
            if length == 0:
                continue
            body = await asyncio.wait_for(self.reader.readexactly(length), timeout=5) # получаем тело сообщения
            msg_id = body[0]    # идентификатор сообщения
            if msg_id == 1:     # если 1 (unchoke) то все норм выходим
                return

    async def request_block(self, index: int, offset: int, size: int) -> bytes: # метод запрашивает конкретный блок данных из куска у пира.
        msg = struct.pack("!IBIII", 13, 6, index, offset, size)
        self.writer.write(msg)
        header = await asyncio.wait_for(self.reader.readexactly(4), timeout=5)
        length = struct.unpack("!I", header)[0]
        payload = await asyncio.wait_for(self.reader.readexactly(length), timeout=5)
        return payload[9:]