import asyncio
import os
import sys
import logging
from torrent_parser import parse_torrent_file
from tracker_client import TrackerClient
from peer_client import PeerClient, BLOCK_SIZE
from piece_manager import PieceManager
from file_assembler import FileAssembler
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def usage():
    print(f"Usage: python {os.path.basename(sys.argv[0])} <torrent_file>")

async def download(torrent_path: str):
    try:
        meta = parse_torrent_file(torrent_path)
    except Exception as e:
        logger.error(f"Failed to parse torrent file: {e}")
        return

    peer_id = b'-PC0001-' + os.urandom(12)
    tracker = TrackerClient(meta['announce'], meta['info_hash'], peer_id, left=meta['length'])
    
    try:
        peers = await tracker.get_peers()
    except Exception as e:
        logger.error(f"Failed to get peers from tracker: {e}")
        return
    
    if not peers:
        logger.info("No peers from tracker, exiting.")
        return

    pm = PieceManager(meta['pieces'], meta['piece_length'], meta['length'])
    fa = FileAssembler(meta['name'], meta['piece_length'], meta['length'], meta['files'])

    failed_pieces = set()
    reliable_peers = set()

    async def fetch_piece(idx):
        ip, port = random.choice(peers)
        pc = PeerClient(ip, port, meta['info_hash'], peer_id)
        piece_size = pm.get_piece_size(idx)  # Получаем точный размер куска
        buffer = bytearray(piece_size)
        try:
            await pc.handshake()
            await pc.send_interested()
            await pc.wait_unchoke()
            for offset in range(0, piece_size, BLOCK_SIZE):
                size = min(BLOCK_SIZE, piece_size - offset)
                block = await pc.request_block(idx, offset, size)
                buffer[offset:offset+len(block)] = block
            if pm.verify(idx, buffer):
                fa.write_piece(idx, buffer)
                logger.info(f"Piece {idx} OK from {ip}:{port}")
                return True
            else:
                logger.warning(f"Piece {idx} hash mismatch, will retry")
                return False
        except Exception as e:
            logger.error(f"Error piece {idx} from {ip}:{port} -> {e}")
            return False

    sem = asyncio.Semaphore(10)

    async def sem_fetch(i):
        async with sem:
            success = await fetch_piece(i)
            if not success:
                failed_pieces.add(i)

    # Первая попытка загрузки всех кусков
    tasks = [sem_fetch(i) for i in range(pm.num_pieces)]
    await asyncio.gather(*tasks)

    # Повторные попытки для неудачных кусков
    max_retries = 5
    retry = 1
    while failed_pieces:
        logger.info(f"Retry attempt {retry}, failed pieces: {len(failed_pieces)}")
        current_failed = list(failed_pieces)
        failed_pieces.clear()
        retry_tasks = [sem_fetch(i) for i in current_failed]
        await asyncio.gather(*retry_tasks)
        retry += 1

    if failed_pieces:
        logger.error(f"Failed to download pieces after {max_retries} retries: {failed_pieces}")
    else:
        logger.info("All pieces downloaded successfully.")

if __name__ == '__main__':
    path_ = '[AI] Фостер Дэвид - Генеративное глубокое обучение. Как не мы рисуем картины, пишем романы и музыку. 2-е межд изд. [2024, PDF, RUS [rutracker-6511606].torrent'
    torrent_path = 'Robert Greene Роберт Грин - The 48 Laws of Power 48 законов власти [2003, PDF, RUS] [rutracker-4379239].torrent'
    asyncio.run(download(path_))