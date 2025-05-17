import asyncio
import aiohttp
from urllib.parse import urlencode
import bencodepy
from torrent_parser import parse_torrent_file 
import os

class TrackerClientError(Exception):
    pass

class TrackerClient:
    def __init__(self,
                 announce: str, 
                 info_hash: bytes, 
                 peer_id: bytes, 
                 port: int = 6881,
                 downloaded: int = 0,
                 uploaded: int  = 0,
                 left: int = 0):
        self.announce = announce
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.port = port
        self.downloaded = downloaded
        self.uploaded = uploaded
        self.left = left #размер

    async def get_peers(self) -> list:
        # Кодирование байтовых строк для URL
        parametr  = {
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'port': self.port,
            'uploaded': self.uploaded,
            'downloaded': self.downloaded,
            'left': self.left,
            'compact': 1
        }
        url = f'{self.announce}?{urlencode(parametr)}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=100) as resp:
                data = await resp.read()

        try:
            resp_dict = bencodepy.decode(data)
        except Exception as e:
            raise TrackerClientError(f"Failed to decode tracker response: {e}")
        
        peers_ = resp_dict[b'peers']
        peers = [] 

        for i in range(0, len(peers_), 6):
            ip_bytes = peers_[i:i+4]
            port_bytes = peers_[i+4:i+6]
            ip = ".".join(str(b) for b in ip_bytes)
            port = (port_bytes[0] << 8) + port_bytes[1]
            peers.append((ip, port))
        
        return peers
    
# async def main():
#     meta = parse_torrent_file("Robert Greene Роберт Грин - The 48 Laws of Power 48 законов власти [2003, PDF, RUS] [rutracker-4379239].torrent")
#     peer_id = b'-PC0001-' + os.urandom(1)
#     client = TrackerClient(meta['announce'], meta['info_hash'], peer_id, left = meta['length'])
#     peers = await client.get_peers()

# asyncio.run(main())